from datetime import datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from app.models.enums import AdFormat, AdStatus, Channel
from app.schemas.variant import AdVariantRead


class AdCreate(BaseModel):
    job_offer_id: str
    channel: Channel
    format: AdFormat = Field(validation_alias=AliasChoices("format", "ad_format"))
    location: str | None = Field(default=None, max_length=240)

    @field_validator("job_offer_id")
    @classmethod
    def offer_id_not_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("job_offer_id must not be empty")
        return value

    @field_validator("location")
    @classmethod
    def normalize_location(cls, value: str | None) -> str | None:
        return value.strip() if value and value.strip() else None


class AdRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    job_offer_id: str
    channel: Channel
    format: AdFormat = Field(validation_alias=AliasChoices("format", "ad_format"))
    status: AdStatus
    location: str
    created_at: datetime
    updated_at: datetime
    variants: list[AdVariantRead] = Field(default_factory=list)


class AdSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    job_offer_id: str
    channel: Channel
    format: AdFormat = Field(validation_alias=AliasChoices("format", "ad_format"))
    status: AdStatus
    location: str
    variants: list[AdVariantRead] = Field(default_factory=list)
