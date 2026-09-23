from sqlalchemy.orm import Session

from app.models.job_offer import JobOffer
from app.repositories.job_offer_repository import JobOfferRepository


class JobOfferService:
    def __init__(self, repository: JobOfferRepository):
        self.repository = repository

    def list_job_offers(self) -> list[JobOffer]:
        return self.repository.list_job_offers()

    def get_job_offer(self, job_offer_id: str) -> JobOffer | None:
        return self.repository.get_job_offer(job_offer_id)


def get_job_offer_service(session: Session) -> JobOfferService:
    return JobOfferService(JobOfferRepository(session))
