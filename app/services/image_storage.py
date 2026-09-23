from io import BytesIO
from pathlib import Path
from uuid import uuid4

from PIL import Image, UnidentifiedImageError


A4_PORTRAIT_RATIO = 210 / 297
A4_RATIO_TOLERANCE = 0.02


class InvalidImage(Exception):
    pass


class InvalidImageDimensions(InvalidImage):
    pass


class ImageTooLarge(Exception):
    pass


def validate_a4_portrait(data: bytes) -> None:
    try:
        with Image.open(BytesIO(data)) as image:
            width, height = image.size
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise InvalidImage("Il file immagine non è valido") from exc

    ratio = width / height
    relative_difference = abs(ratio - A4_PORTRAIT_RATIO) / A4_PORTRAIT_RATIO
    if height <= width or relative_difference > A4_RATIO_TOLERANCE:
        raise InvalidImageDimensions(
            "Per WhatsApp carica un'immagine verticale in proporzione A4 (210:297)."
        )


def save_image(
    data: bytes,
    content_type: str | None,
    upload_dir: Path,
    max_bytes: int,
    require_a4_portrait: bool = False,
) -> Path:
    if not data:
        raise InvalidImage("Il file è vuoto")
    if len(data) > max_bytes:
        raise ImageTooLarge("L'immagine supera la dimensione massima consentita")

    media_type = (content_type or "").split(";", 1)[0].strip().lower()
    signatures = {
        "image/jpeg": (".jpg", lambda value: value.startswith(b"\xff\xd8\xff")),
        "image/png": (".png", lambda value: value.startswith(b"\x89PNG\r\n\x1a\n")),
        "image/webp": (
            ".webp",
            lambda value: len(value) >= 12 and value[:4] == b"RIFF" and value[8:12] == b"WEBP",
        ),
    }
    signature = signatures.get(media_type)
    if signature is None or not signature[1](data):
        raise InvalidImage("Carica un'immagine PNG, JPEG o WebP valida")
    if require_a4_portrait:
        validate_a4_portrait(data)

    upload_dir.mkdir(parents=True, exist_ok=True)
    path = upload_dir / f"{uuid4().hex}{signature[0]}"
    path.write_bytes(data)
    return path
