from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import AdStatus


class AdUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: AdStatus | None = None
    location: str | None = Field(default=None, min_length=1, max_length=240)

    @model_validator(mode="after")
    def require_at_least_one_field(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        if "status" in self.model_fields_set and self.status is None:
            raise ValueError("status cannot be null")
        if "location" in self.model_fields_set and self.location is None:
            raise ValueError("location cannot be null")
        return self

    @field_validator("location")
    @classmethod
    def normalize_location(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("location must not be empty")
        return normalized


class VariantGenerationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    variant_name: str | None = Field(default=None, max_length=120)


class AdVariantUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    variant_name: str | None = Field(default=None, max_length=120)
    title: str | None = Field(default=None, max_length=300)
    body_text: str | None = None
    requirements: list[str] | None = None
    compensation: str | None = None
    channel_fields: dict[str, str] | None = None
    creative_text: str | None = None
    creative_brief: str | None = None

    @model_validator(mode="after")
    def require_at_least_one_field(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        for field in ("variant_name", "title", "requirements", "channel_fields"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        if "variant_name" in self.model_fields_set and not self.variant_name:
            raise ValueError("variant_name must not be empty")
        if "title" in self.model_fields_set and not self.title:
            raise ValueError("title must not be empty")
        return self
