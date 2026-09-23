from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.llm.client import (
    LLMConfigurationError,
    LLMOutputError,
    LLMProviderError,
    OpenAIClient,
)
from app.models.ad import Ad
from app.models.ad_variant import AdVariant
from app.models.enums import AdFormat, AdStatus, Channel, ContentOrigin
from app.repositories.ad_repository import AdRepository
from app.repositories.job_offer_repository import JobOfferRepository
from app.schemas.ad import AdCreate
from app.schemas.ad_update import AdUpdate, AdVariantUpdate
from app.schemas.generation import VariantDraft, validate_variant_draft
from app.schemas.job_offer import format_location
from app.services.ad_generation_service import AdGenerationService


class ResourceNotFound(Exception):
    pass


class GenerationUnavailable(Exception):
    pass


class GenerationRejected(Exception):
    pass


class InvalidVariantContent(Exception):
    pass


class AdService:
    def __init__(self, session: Session, settings: Settings | None = None):
        self.session = session
        self.settings = settings or get_settings()
        self.ads = AdRepository(session)
        self.offers = JobOfferRepository(session)
        self.generation = AdGenerationService(self.ads, OpenAIClient(self.settings))

    def _commit(self) -> None:
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def list_ads(self, job_offer_id: str | None = None, channel: Channel | None = None) -> list[Ad]:
        return self.ads.list_ads(job_offer_id=job_offer_id, channel=channel)

    def get_ad(self, ad_id: str) -> Ad:
        ad = self.ads.get_ad(ad_id)
        if ad is None:
            raise ResourceNotFound("Annuncio non trovato")
        return ad

    def create_ad(self, data: AdCreate) -> Ad:
        offer = self.offers.get_job_offer(data.job_offer_id)
        if offer is None:
            raise ResourceNotFound("Job offer non trovata")
        location = data.location or format_location(offer.location)
        if not location:
            raise ValueError("Indicare il luogo di pubblicazione")
        try:
            ad = self.ads.create_ad(
                job_offer_id=offer.id,
                channel=data.channel,
                ad_format=data.format,
                status=AdStatus.DRAFT,
                location=location,
            )
            self.generation.generate_variant(ad)
            self._commit()
        except (LLMConfigurationError, LLMProviderError) as exc:
            self.session.rollback()
            raise GenerationUnavailable(str(exc)) from exc
        except LLMOutputError as exc:
            self.session.rollback()
            raise GenerationRejected(str(exc)) from exc
        except Exception:
            self.session.rollback()
            raise
        return self.get_ad(ad.id)

    def generate_additional_variant(self, ad_id: str, variant_name: str | None = None) -> AdVariant:
        ad = self.get_ad(ad_id)
        try:
            variant = self.generation.generate_variant(ad, variant_name)
            self._commit()
            return variant
        except (LLMConfigurationError, LLMProviderError) as exc:
            self.session.rollback()
            raise GenerationUnavailable(str(exc)) from exc
        except LLMOutputError as exc:
            self.session.rollback()
            raise GenerationRejected(str(exc)) from exc
        except Exception:
            self.session.rollback()
            raise

    def update_ad(self, ad_id: str, data: AdUpdate) -> Ad:
        ad = self.ads.update_ad(ad_id, data.model_dump(exclude_unset=True))
        if ad is None:
            raise ResourceNotFound("Annuncio non trovato")
        self._commit()
        return self.get_ad(ad_id)

    def update_variant(self, ad_id: str, variant_id: str, data: AdVariantUpdate) -> AdVariant:
        ad = self.get_ad(ad_id)
        variant = self.ads.get_variant_for_ad(ad_id, variant_id)
        if variant is None:
            raise ResourceNotFound("Variante non trovata per questo annuncio")

        changes = data.model_dump(exclude_unset=True)
        merged = {
            "variant_name": variant.variant_name,
            "title": variant.title,
            "body_text": variant.body_text,
            "requirements": variant.requirements,
            "compensation": variant.compensation,
            "channel_fields": variant.channel_fields,
            "creative_text": variant.creative_text,
            "creative_brief": variant.creative_brief,
        }
        merged.update(changes)
        try:
            draft = VariantDraft.model_validate(merged)
            validate_variant_draft(draft, ad.channel, ad.ad_format)
        except (ValidationError, ValueError) as exc:
            raise InvalidVariantContent(str(exc)) from exc

        normalized = draft.model_dump()
        normalized["channel_fields"] = {
            key: value for key, value in draft.channel_fields.items() if value is not None
        }
        normalized["origin"] = ContentOrigin.MANUAL
        updated = self.ads.update_variant(variant_id, normalized)
        self._commit()
        return updated

    def attach_variant_image(self, ad_id: str, variant_id: str, image_path: str) -> AdVariant:
        self.get_ad(ad_id)
        variant = self.ads.get_variant_for_ad(ad_id, variant_id)
        if variant is None:
            raise ResourceNotFound("Variante non trovata per questo annuncio")
        updated = self.ads.update_variant(variant_id, {"image_path": image_path})
        self._commit()
        return updated
