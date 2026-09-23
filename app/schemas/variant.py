from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ContentOrigin


class AdVariantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    ad_id: str
    variant_name: str
    title: str
    body_text: str | None = None
    requirements: list[str] = Field(default_factory=list)
    compensation: str | None = None
    channel_fields: dict[str, str] = Field(default_factory=dict)
    creative_text: str | None = None
    creative_brief: str | None = None
    image_path: str | None = None
    origin: ContentOrigin
    created_at: datetime
    updated_at: datetime
