import uuid
import mimetypes
from pathlib import Path


ALLOWED_IMAGE_MIME = {"image/jpeg", "image/png", "image/webp", "image/tiff"}
ALLOWED_DOC_MIME = {"application/pdf"}
ALLOWED_MIME = ALLOWED_IMAGE_MIME | ALLOWED_DOC_MIME

MIME_TO_EXT = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/tiff": ".tiff",
    "application/pdf": ".pdf",
}


def generate_job_id() -> str:
    return str(uuid.uuid4())


def s3_key(job_id: str, filename: str) -> str:
    return f"jobs/{job_id}/inputs/{filename}"


def output_s3_key(job_id: str, filename: str) -> str:
    return f"jobs/{job_id}/outputs/{filename}"


def ext_from_mime(mime_type: str) -> str:
    return MIME_TO_EXT.get(mime_type, mimetypes.guess_extension(mime_type) or ".bin")


def is_allowed_mime(mime_type: str) -> bool:
    return mime_type in ALLOWED_MIME


def safe_filename(name: str) -> str:
    stem = Path(name).stem
    suffix = Path(name).suffix
    clean = "".join(c if c.isalnum() or c in "-_" else "_" for c in stem)
    return f"{clean[:64]}{suffix}"
