from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job_offer import JobOffer


class JobOfferRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_job_offers(self) -> list[JobOffer]:
        query = select(JobOffer).order_by(JobOffer.id, JobOffer.title)
        return list(self.session.scalars(query))

    def get_job_offer(self, job_offer_id: str) -> JobOffer | None:
        return self.session.get(JobOffer, job_offer_id)

    def create_job_offer(self, **values) -> JobOffer:
        offer = JobOffer(**values)
        self.session.add(offer)
        self.session.flush()
        return offer

    def update_job_offer(self, job_offer_id: str, changes: dict) -> JobOffer | None:
        offer = self.get_job_offer(job_offer_id)
        if offer is None:
            return None
        for field, value in changes.items():
            setattr(offer, field, value)
        self.session.flush()
        return offer
