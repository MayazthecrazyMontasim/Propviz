import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import ActiveUser, get_current_user
from app.models.user import User
from app.core.config import settings
from app.models.job import Job
from app.models.asset import Asset, AssetType
from app.services import storage_service
from app.utils.helpers import (
    is_allowed_mime, s3_key, safe_filename, ext_from_mime, ALLOWED_MIME
)

router = APIRouter(prefix="/assets", tags=["assets"])

MAX_BYTES = settings.max_upload_size_mb * 1024 * 1024


# ── Schemas ───────────────────────────────────────────────────────────────────

class PresignedUploadResponse(BaseModel):
    upload_url: str
    s3_key: str
    asset_id: str


class PresignedUploadRequest(BaseModel):
    job_id: str
    filename: str
    content_type: str
    asset_type: AssetType


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/presign", response_model=PresignedUploadResponse)
async def get_presigned_upload_url(
    body: PresignedUploadRequest,
    _: ActiveUser,
    db: AsyncSession = Depends(get_db),
):
    """Return a presigned S3 PUT URL. Client uploads directly to S3, then calls /confirm."""
    job = await db.get(Job, body.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not is_allowed_mime(body.content_type):
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported type {body.content_type}. Allowed: {sorted(ALLOWED_MIME)}",
        )

    filename = safe_filename(body.filename)
    key = s3_key(body.job_id, f"{uuid.uuid4().hex}_{filename}")
    upload_url = storage_service.presigned_upload_url(key, body.content_type)

    asset = Asset(
        job_id=body.job_id,
        asset_type=body.asset_type,
        original_filename=filename,
        s3_key=key,
        mime_type=body.content_type,
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)

    return PresignedUploadResponse(upload_url=upload_url, s3_key=key, asset_id=asset.id)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def direct_upload(
    job_id: str = Form(...),
    asset_type: AssetType = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Direct server-side upload (simpler but not recommended for large files)."""
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    mime = file.content_type or "application/octet-stream"
    if not is_allowed_mime(mime):
        raise HTTPException(status_code=415, detail=f"Unsupported type: {mime}")

    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {settings.max_upload_size_mb} MB limit",
        )

    filename = safe_filename(file.filename or f"upload{ext_from_mime(mime)}")
    key = s3_key(job_id, f"{uuid.uuid4().hex}_{filename}")
    cdn_url = storage_service.upload_bytes(data, key, mime)

    asset = Asset(
        job_id=job_id,
        asset_type=asset_type,
        original_filename=filename,
        s3_key=key,
        mime_type=mime,
        size_bytes=len(data),
        cdn_url=cdn_url,
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)

    return {"asset_id": asset.id, "s3_key": key, "cdn_url": cdn_url}


@router.get("/{asset_id}/download-url")
async def get_download_url(asset_id: str, db: AsyncSession = Depends(get_db)):
    asset = await db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    url = storage_service.presigned_download_url(asset.s3_key)
    return {"download_url": url}


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(asset_id: str, db: AsyncSession = Depends(get_db)):
    asset = await db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    await db.delete(asset)
    await db.commit()
