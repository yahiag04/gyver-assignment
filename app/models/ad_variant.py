from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import ContentOrigin


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AdVariant(Base):
    __tablename__ = "ad_variants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    ad_id: Mapped[str] = mapped_column(ForeignKey("ads.id", ondelete="CASCADE"), nullable=False, index=True)
    variant_name: Mapped[str] = mapped_column(String(120), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    body_text: Mapped[str | None] = mapped_column(Text)
    requirements: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    compensation: Mapped[str | None] = mapped_column(Text)
    channel_fields: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    creative_text: Mapped[str | None] = mapped_column(Text)
    creative_brief: Mapped[str | None] = mapped_column(Text)
    image_path: Mapped[str | None] = mapped_column(String(500))
    origin: Mapped[ContentOrigin] = mapped_column(Enum(ContentOrigin, values_callable=lambda e: [v.value for v in e], native_enum=False, validate_strings=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    ad: Mapped["Ad"] = relationship(back_populates="variants")
