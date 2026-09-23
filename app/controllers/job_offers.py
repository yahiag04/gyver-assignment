from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.job_offer import JobOfferRead
from app.services.job_offer_service import get_job_offer_service


router = APIRouter(prefix="/job-offers", tags=["job offers"])


@router.get("", response_model=list[JobOfferRead])
def list_job_offers(session: Session = Depends(get_session)) -> list[JobOfferRead]:
    return get_job_offer_service(session).list_job_offers()


@router.get("/{job_offer_id}", response_model=JobOfferRead)
def get_job_offer(job_offer_id: str, session: Session = Depends(get_session)) -> JobOfferRead:
    offer = get_job_offer_service(session).get_job_offer(job_offer_id)
    if offer is None:
        raise HTTPException(status_code=404, detail="Job offer not found")
    return offer
