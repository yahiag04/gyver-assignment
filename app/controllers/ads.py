from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.models.enums import Channel
from app.schemas.ad import AdCreate, AdRead, AdSummary
from app.schemas.ad_update import AdUpdate, AdVariantUpdate, VariantGenerationRequest
from app.schemas.variant import AdVariantRead
from app.services.ad_service import (
    AdService,
    GenerationRejected,
    GenerationUnavailable,
    InvalidVariantContent,
    ResourceNotFound,
)
from app.services.image_storage import ImageTooLarge, InvalidImage, InvalidImageDimensions, save_image


router = APIRouter(prefix="/ads", tags=["ads"])


def _service(request: Request, session: Session) -> AdService:
    return AdService(session, request.app.state.settings)


@router.get("", response_model=list[AdSummary])
def list_ads(
    request: Request,
    job_offer_id: str | None = Query(default=None),
    channel: Channel | None = Query(default=None),
    session: Session = Depends(get_session),
) -> list[AdSummary]:
    return _service(request, session).list_ads(job_offer_id=job_offer_id, channel=channel)


@router.get("/{ad_id}", response_model=AdRead)
def get_ad(ad_id: str, request: Request, session: Session = Depends(get_session)) -> AdRead:
    try:
        return _service(request, session).get_ad(ad_id)
    except ResourceNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("", response_model=AdRead, status_code=status.HTTP_201_CREATED)
def create_ad(data: AdCreate, request: Request, session: Session = Depends(get_session)) -> AdRead:
    try:
        return _service(request, session).create_ad(data)
    except ResourceNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except GenerationUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GenerationRejected as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.delete("/{ad_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ad(ad_id: str, request: Request, session: Session = Depends(get_session)) -> None:
    try:
        _service(request, session).delete_ad(ad_id)
    except ResourceNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{ad_id}/variants", response_model=AdVariantRead, status_code=status.HTTP_201_CREATED)
def generate_variant(
    ad_id: str, data: VariantGenerationRequest, request: Request,
    session: Session = Depends(get_session)
) -> AdVariantRead:
    try:
        return _service(request, session).generate_additional_variant(ad_id, data.variant_name)
    except ResourceNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except GenerationUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GenerationRejected as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.patch("/{ad_id}", response_model=AdRead)
def update_ad(ad_id: str, data: AdUpdate, request: Request, session: Session = Depends(get_session)) -> AdRead:
    try:
        return _service(request, session).update_ad(ad_id, data)
    except ResourceNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/{ad_id}/variants/{variant_id}", response_model=AdVariantRead)
def update_variant(
    ad_id: str,
    variant_id: str,
    data: AdVariantUpdate,
    request: Request,
    session: Session = Depends(get_session),
) -> AdVariantRead:
    try:
        return _service(request, session).update_variant(ad_id, variant_id, data)
    except ResourceNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidVariantContent as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post(
    "/{ad_id}/variants/{variant_id}/image",
    response_model=AdVariantRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_variant_image(
    ad_id: str,
    variant_id: str,
    request: Request,
    image: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> AdVariantRead:
    settings = request.app.state.settings
    max_bytes = settings.max_upload_mb * 1024 * 1024
    try:
        data = await image.read(max_bytes + 1)
        ad = _service(request, session).get_ad(ad_id)
        path = save_image(
            data,
            image.content_type,
            Path(settings.upload_dir),
            max_bytes,
            require_a4_portrait=ad.channel == Channel.WHATSAPP,
        )
        image_url = f"/uploads/{path.name}"
        try:
            return _service(request, session).attach_variant_image(ad_id, variant_id, image_url)
        except ResourceNotFound as exc:
            path.unlink(missing_ok=True)
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except InvalidVariantContent as exc:
            path.unlink(missing_ok=True)
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except Exception:
            path.unlink(missing_ok=True)
            raise
    except ImageTooLarge as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    except InvalidImageDimensions as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ResourceNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidImage as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc
    finally:
        await image.close()
