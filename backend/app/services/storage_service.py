"""
Storage service — local filesystem in dev, S3/R2 in production.
Switches automatically based on whether AWS_ACCESS_KEY_ID is configured.
"""
import io
import os
from pathlib import Path
from typing import BinaryIO

from app.core.config import settings

# Local storage path for dev
_LOCAL_DIR = Path(__file__).parent.parent.parent / "local_storage"


def _use_local() -> bool:
    return not settings.aws_access_key_id or settings.aws_access_key_id in ("", "your_access_key")


def _local_path(key: str) -> Path:
    p = _LOCAL_DIR / key
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


# ── Public API ────────────────────────────────────────────────────────────────

def upload_fileobj(fileobj: BinaryIO, key: str, content_type: str) -> str:
    if _use_local():
        path = _local_path(key)
        with open(path, "wb") as f:
            f.write(fileobj.read())
        base = settings.public_url.rstrip("/")
        return f"{base}/local/{key}"

    import boto3
    s3 = _s3_client()
    s3.upload_fileobj(fileobj, settings.storage_bucket, key,
                      ExtraArgs={"ContentType": content_type})
    return _s3_url(key)


def upload_bytes(data: bytes, key: str, content_type: str) -> str:
    return upload_fileobj(io.BytesIO(data), key, content_type)


def download_bytes(key: str) -> bytes:
    if _use_local():
        return _local_path(key).read_bytes()
    s3 = _s3_client()
    buf = io.BytesIO()
    s3.download_fileobj(settings.storage_bucket, key, buf)
    buf.seek(0)
    return buf.read()


def presigned_upload_url(key: str, content_type: str, expires: int = 3600) -> str:
    if _use_local():
        return f"http://localhost:8000/local/upload/{key}"
    return _s3_client().generate_presigned_url(
        "put_object",
        Params={"Bucket": settings.storage_bucket, "Key": key, "ContentType": content_type},
        ExpiresIn=expires,
    )


def presigned_download_url(key: str, expires: int = 3600) -> str:
    if _use_local():
        base = settings.public_url.rstrip("/")
        return f"{base}/local/{key}"
    return _s3_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.storage_bucket, "Key": key},
        ExpiresIn=expires,
    )


def key_exists(key: str) -> bool:
    if _use_local():
        return _local_path(key).exists()
    try:
        _s3_client().head_object(Bucket=settings.storage_bucket, Key=key)
        return True
    except Exception:
        return False


def _url(key: str) -> str:
    if _use_local():
        base = settings.public_url.rstrip("/")
        return f"{base}/local/{key}"
    return _s3_url(key)


# ── S3 helpers ────────────────────────────────────────────────────────────────

def _s3_client():
    import boto3
    kwargs = {
        "region_name": settings.storage_region,
        "aws_access_key_id": settings.aws_access_key_id,
        "aws_secret_access_key": settings.aws_secret_access_key,
    }
    if settings.storage_endpoint_url and "account_id" not in settings.storage_endpoint_url:
        kwargs["endpoint_url"] = settings.storage_endpoint_url
    return boto3.client("s3", **kwargs)


def _s3_url(key: str) -> str:
    if settings.cdn_base_url and "yourdomain" not in settings.cdn_base_url:
        return f"{settings.cdn_base_url.rstrip('/')}/{key}"
    return f"https://{settings.storage_bucket}.s3.{settings.storage_region}.amazonaws.com/{key}"
