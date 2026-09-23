from typing import Any

import httpx
from pydantic import ValidationError

from app.core.config import Settings, get_settings
from app.llm.prompts import SYSTEM_PROMPT, build_user_prompt
from app.models.enums import AdFormat, Channel
from app.models.job_offer import JobOffer
from app.schemas.generation import VariantDraft, validate_variant_draft


class LLMError(Exception):
    """Base class for safe, user-facing generation errors."""


class LLMConfigurationError(LLMError):
    pass


class LLMProviderError(LLMError):
    pass


class LLMOutputError(LLMError):
    pass


def output_schema() -> dict[str, Any]:
    schema = VariantDraft.model_json_schema()
    schema["properties"]["channel_fields"] = {
        "type": "object",
        "properties": {
            name: {"type": ["string", "null"]}
            for name in ("experience", "employment_type", "schedule", "application_url")
        },
        "required": ["experience", "employment_type", "schedule", "application_url"],
        "additionalProperties": False,
    }
    return schema


class OpenAIClient:
    def __init__(self, settings: Settings | None = None, http_client: httpx.Client | None = None):
        self.settings = settings or get_settings()
        self.http_client = http_client

    def generate_variant(
        self, offer: JobOffer, channel: Channel, ad_format: AdFormat, location: str
    ) -> VariantDraft:
        if not self.settings.openai_api_key:
            raise LLMConfigurationError("OPENAI_API_KEY non configurata")

        payload = {
            "model": self.settings.openai_model,
            "store": False,
            "instructions": SYSTEM_PROMPT,
            "input": build_user_prompt(
                self._offer_context(offer), channel.value, ad_format.value, location
            ),
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "ad_variant",
                    "strict": True,
                    "schema": output_schema(),
                }
            },
        }
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        try:
            if self.http_client is None:
                with httpx.Client(timeout=self.settings.openai_timeout_seconds) as client:
                    response = client.post(
                        "https://api.openai.com/v1/responses", headers=headers, json=payload
                    )
            else:
                response = self.http_client.post(
                    "https://api.openai.com/v1/responses", headers=headers, json=payload
                )
        except httpx.TimeoutException as exc:
            raise LLMProviderError("Timeout durante la generazione dell'annuncio") from exc
        except httpx.RequestError as exc:
            raise LLMProviderError("Servizio di generazione temporaneamente non raggiungibile") from exc

        if response.is_error:
            raise LLMProviderError(f"Il provider LLM ha restituito HTTP {response.status_code}")
        try:
            response_data = response.json()
        except ValueError as exc:
            raise LLMOutputError("Il provider ha restituito una risposta non JSON") from exc

        if not isinstance(response_data, dict):
            raise LLMOutputError("Il provider ha restituito una risposta inattesa")
        if response_data.get("status") != "completed":
            raise LLMOutputError("La generazione non è stata completata")
        output_text = self._extract_output_text(response_data)
        if output_text is None:
            raise LLMOutputError("La risposta del provider non contiene testo strutturato")
        try:
            draft = VariantDraft.model_validate_json(output_text)
            return validate_variant_draft(draft, channel, ad_format)
        except (ValidationError, ValueError) as exc:
            raise LLMOutputError("La risposta del provider non rispetta il formato richiesto") from exc

    @staticmethod
    def _offer_context(offer: JobOffer) -> dict[str, Any]:
        location = offer.location or {}
        province_code = location.get("province_code") or location.get("province", "")
        return {
            "title": offer.title,
            "company_name": offer.company_name,
            "company_description": offer.company_description,
            "role_description": offer.role_description,
            "requirements_description": offer.requirements_description,
            "required_skills": offer.required_skills,
            "contract_type": offer.contract_type,
            "experience_years": {"min": offer.min_exp_years, "max": offer.max_exp_years},
            "compensation_package": offer.compensation_package,
            "location_and_hours": offer.location_and_hours,
            "offer_location": ", ".join(
                part for part in (location.get("locality"), province_code) if part
            ),
        }

    @staticmethod
    def _extract_output_text(response: dict[str, Any]) -> str | None:
        output = response.get("output", [])
        if not isinstance(output, list):
            raise LLMOutputError("Il provider ha restituito una risposta inattesa")
        for item in output:
            if not isinstance(item, dict):
                continue
            if item.get("type") != "message":
                continue
            contents = item.get("content", [])
            if not isinstance(contents, list):
                continue
            for content in contents:
                if not isinstance(content, dict):
                    continue
                if content.get("type") == "refusal":
                    raise LLMOutputError("Il provider ha rifiutato di generare questo contenuto")
                if content.get("type") == "output_text":
                    return content.get("text")
        return None
