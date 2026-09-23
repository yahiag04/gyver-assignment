from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import AdFormat, AdStatus, Channel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Ad(Base):
    __tablename__ = "ads"
    __table_args__ = (Index("ix_ads_offer_channel", "job_offer_id", "channel"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    job_offer_id: Mapped[str] = mapped_column(ForeignKey("job_offers.id", ondelete="CASCADE"), nullable=False)
    channel: Mapped[Channel] = mapped_column(Enum(Channel, values_callable=lambda e: [v.value for v in e], native_enum=False, validate_strings=True), nullable=False)
    ad_format: Mapped[AdFormat] = mapped_column("format", Enum(AdFormat, values_callable=lambda e: [v.value for v in e], native_enum=False, validate_strings=True), nullable=False)
    status: Mapped[AdStatus] = mapped_column(Enum(AdStatus, values_callable=lambda e: [v.value for v in e], native_enum=False, validate_strings=True), default=AdStatus.DRAFT, nullable=False)
    location: Mapped[str] = mapped_column(String(240), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    job_offer: Mapped["JobOffer"] = relationship(back_populates="ads")
    variants: Mapped[list["AdVariant"]] = relationship(back_populates="ad", cascade="all, delete-orphan", order_by="AdVariant.created_at, AdVariant.id")
