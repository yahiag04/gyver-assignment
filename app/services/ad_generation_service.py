from app.llm.client import OpenAIClient
from app.models.ad import Ad
from app.models.ad_variant import AdVariant
from app.models.enums import ContentOrigin
from app.repositories.ad_repository import AdRepository


class AdGenerationService:
    def __init__(self, repository: AdRepository, client: OpenAIClient):
        self.repository = repository
        self.client = client

    def generate_variant(self, ad: Ad, variant_name: str | None = None) -> AdVariant:
        draft = self.client.generate_variant(
            offer=ad.job_offer,
            channel=ad.channel,
            ad_format=ad.ad_format,
            location=ad.location,
        )
        values = draft.model_dump()
        values["channel_fields"] = {
            key: value for key, value in draft.channel_fields.items() if value is not None
        }
        values["variant_name"] = variant_name or values["variant_name"]
        values["origin"] = ContentOrigin.LLM
        return self.repository.create_variant(ad_id=ad.id, **values)
