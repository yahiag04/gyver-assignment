from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.ad import Ad
from app.models.ad_variant import AdVariant
from app.models.enums import Channel


class AdRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_ads(self, job_offer_id: str | None = None, channel: Channel | None = None) -> list[Ad]:
        query = select(Ad).options(selectinload(Ad.variants)).order_by(Ad.created_at, Ad.id)
        if job_offer_id is not None:
            query = query.where(Ad.job_offer_id == job_offer_id)
        if channel is not None:
            query = query.where(Ad.channel == channel)
        return list(self.session.scalars(query).unique())

    def get_ad(self, ad_id: str) -> Ad | None:
        return self.session.scalar(
            select(Ad).options(selectinload(Ad.variants)).where(Ad.id == ad_id)
        )

    def create_ad(self, **values) -> Ad:
        ad = Ad(**values)
        self.session.add(ad)
        self.session.flush()
        return ad

    def create_variant(self, **values) -> AdVariant:
        variant = AdVariant(**values)
        self.session.add(variant)
        self.session.flush()
        return variant

    def get_variant(self, variant_id: str) -> AdVariant | None:
        return self.session.get(AdVariant, variant_id)

    def get_variant_for_ad(self, ad_id: str, variant_id: str) -> AdVariant | None:
        return self.session.scalar(
            select(AdVariant).where(AdVariant.id == variant_id, AdVariant.ad_id == ad_id)
        )

    def update_ad(self, ad_id: str, changes: dict) -> Ad | None:
        ad = self.get_ad(ad_id)
        if ad is None:
            return None
        for field, value in changes.items():
            setattr(ad, field, value)
        self.session.flush()
        return ad

    def update_variant(self, variant_id: str, changes: dict) -> AdVariant | None:
        variant = self.get_variant(variant_id)
        if variant is None:
            return None
        for field, value in changes.items():
            setattr(variant, field, value)
        self.session.flush()
        return variant
