from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class JobOffer(Base):
    __tablename__ = "job_offers"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    company_name: Mapped[str] = mapped_column(String(240), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")
    source_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    location: Mapped[dict] = mapped_column(JSON, nullable=False)
    contract_type: Mapped[str | None] = mapped_column(String(120))
    min_exp_years: Mapped[int | None] = mapped_column(Integer)
    max_exp_years: Mapped[int | None] = mapped_column(Integer)
    ral_min: Mapped[int | None] = mapped_column(Integer)
    ral_max: Mapped[int | None] = mapped_column(Integer)
    currency: Mapped[str | None] = mapped_column(String(8))
    required_skills: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    role_description: Mapped[str] = mapped_column(Text, nullable=False)
    location_and_hours: Mapped[str] = mapped_column(Text, nullable=False)
    company_description: Mapped[str] = mapped_column(Text, nullable=False)
    requirements_description: Mapped[str] = mapped_column(Text, nullable=False)
    compensation_package: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    ads: Mapped[list["Ad"]] = relationship(back_populates="job_offer", cascade="all, delete-orphan")
