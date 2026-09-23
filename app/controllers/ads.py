from fastapi import APIRouter, Depends, HTTPException, Query, status
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


router = APIRouter(prefix="/ads", tags=["ads"])


def _service(session: Session) -> AdService:
    return AdService(session)


@router.get("", response_model=list[AdSummary])
def list_ads(
    job_offer_id: str | None = Query(default=None),
    channel: Channel | None = Query(default=None),
    session: Session = Depends(get_session),
) -> list[AdSummary]:
    return _service(session).list_ads(job_offer_id=job_offer_id, channel=channel)


@router.get("/{ad_id}", response_model=AdRead)
def get_ad(ad_id: str, session: Session = Depends(get_session)) -> AdRead:
    try:
        return _service(session).get_ad(ad_id)
    except ResourceNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("", response_model=AdRead, status_code=status.HTTP_201_CREATED)
def create_ad(data: AdCreate, session: Session = Depends(get_session)) -> AdRead:
    try:
        return _service(session).create_ad(data)
    except ResourceNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except GenerationUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GenerationRejected as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/{ad_id}/variants", response_model=AdVariantRead, status_code=status.HTTP_201_CREATED)
def generate_variant(
    ad_id: str, data: VariantGenerationRequest, session: Session = Depends(get_session)
) -> AdVariantRead:
    try:
        return _service(session).generate_additional_variant(ad_id, data.variant_name)
    except ResourceNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except GenerationUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GenerationRejected as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.patch("/{ad_id}", response_model=AdRead)
def update_ad(ad_id: str, data: AdUpdate, session: Session = Depends(get_session)) -> AdRead:
    try:
        return _service(session).update_ad(ad_id, data)
    except ResourceNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/{ad_id}/variants/{variant_id}", response_model=AdVariantRead)
def update_variant(
    ad_id: str,
    variant_id: str,
    data: AdVariantUpdate,
    session: Session = Depends(get_session),
) -> AdVariantRead:
    try:
        return _service(session).update_variant(ad_id, variant_id, data)
    except ResourceNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidVariantContent as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
