from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field


def format_location(location: dict[str, str]) -> str:
    locality = location.get("locality", "")
    province_code = location.get("province_code") or location.get("province", "")
    return f"{locality} ({province_code})" if province_code else locality


class JobOfferRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    company_name: str
    status: str
    location: dict[str, str]
    contract_type: str | None = None
    min_exp_years: int | None = None
    max_exp_years: int | None = None
    ral_min: int | None = None
    ral_max: int | None = None
    currency: str | None = None
    required_skills: list[str] = Field(default_factory=list)
    role_description: str
    location_and_hours: str
    company_description: str
    requirements_description: str
    compensation_package: str
    source_created_at: datetime | None = None

    @computed_field
    @property
    def location_label(self) -> str:
        return format_location(self.location)
