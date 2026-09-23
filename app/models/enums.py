from enum import StrEnum


class Channel(StrEnum):
    INDEED = "indeed"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    WHATSAPP = "whatsapp"


class AdFormat(StrEnum):
    TEXT = "text"
    IMAGE = "image"
    IMAGE_TEXT = "image_text"


class AdStatus(StrEnum):
    DRAFT = "draft"
    READY = "ready"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ContentOrigin(StrEnum):
    LLM = "llm"
    MANUAL = "manual"
