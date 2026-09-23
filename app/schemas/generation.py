from pydantic import BaseModel, ConfigDict, field_validator

from app.models.enums import AdFormat, Channel


class VariantDraft(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    variant_name: str
    title: str
    body_text: str | None
    requirements: list[str]
    compensation: str | None
    channel_fields: dict[str, str | None]
    creative_text: str | None
    creative_brief: str | None

    @field_validator("variant_name", "title")
    @classmethod
    def required_text_must_not_be_empty(cls, value: str) -> str:
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("requirements")
    @classmethod
    def clean_requirements(cls, values: list[str]) -> list[str]:
        return [value.strip() for value in values if value.strip()]

    @field_validator("channel_fields")
    @classmethod
    def supported_channel_field_names(cls, values: dict[str, str | None]) -> dict[str, str | None]:
        allowed = {"experience", "employment_type", "schedule", "application_url"}
        if set(values) - allowed:
            raise ValueError("channel_fields contains unsupported field names")
        return {key: value.strip() if value else None for key, value in values.items()}


def validate_variant_draft(draft: VariantDraft, channel: Channel, ad_format: AdFormat) -> VariantDraft:
    if ad_format == AdFormat.TEXT:
        if not draft.body_text:
            raise ValueError("text format requires body_text")
        if draft.creative_text or draft.creative_brief:
            raise ValueError("text format cannot include creative fields")
    elif ad_format == AdFormat.IMAGE:
        if draft.body_text:
            raise ValueError("image format cannot include body_text")
        if not draft.creative_text or not draft.creative_brief:
            raise ValueError("image format requires creative_text and creative_brief")
    elif ad_format == AdFormat.IMAGE_TEXT:
        if not draft.body_text or not draft.creative_text or not draft.creative_brief:
            raise ValueError("image_text format requires body_text, creative_text and creative_brief")

    if channel == Channel.INDEED and not draft.channel_fields.get("experience"):
        raise ValueError("Indeed variants require the experience channel field")
    return draft
