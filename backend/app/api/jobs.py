from typing import Any
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.auth import ActiveUser
from app.models.job import Job, JobStatus
from app.models.property import Property
from app.models.asset import Asset, AssetType

router = APIRouter(prefix="/jobs", tags=["jobs"])


# ── Schemas ──────────────────────────────────────────────────────────────────

class PropertyIn(BaseModel):
    name: str
    developer: str | None = None
    location: str | None = None
    unit_type: str | None = None
    area_sqft: int | None = None
    price_range: str | None = None


class JobCreateIn(BaseModel):
    property: PropertyIn


class AssetOut(BaseModel):
    id: str
    asset_type: str
    original_filename: str
    cdn_url: str | None
    size_bytes: int | None

    class Config:
        from_attributes = True


class JobOut(BaseModel):
    id: str
    status: str
    current_stage: str | None
    progress_pct: int
    output_url: str | None
    error_message: str | None
    assets: list[AssetOut]

    class Config:
        from_attributes = True


class JobListItem(BaseModel):
    id: str
    status: str
    progress_pct: int
    output_url: str | None
    property_name: str

    class Config:
        from_attributes = True


# ── Routes ───────────────────────────────────────────────────────────────────

@router.post("/", response_model=JobOut, status_code=status.HTTP_201_CREATED)
async def create_job(body: JobCreateIn, _: ActiveUser, db: AsyncSession = Depends(get_db)):
    prop = Property(**body.property.model_dump())
    db.add(prop)
    await db.flush()

    job = Job(property_id=prop.id)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


@router.get("/", response_model=list[JobListItem])
async def list_jobs(_: ActiveUser, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Job, Property.name)
        .join(Property, Job.property_id == Property.id)
        .order_by(Job.created_at.desc())
        .limit(100)
    )
    rows = result.all()
    return [
        JobListItem(
            id=row.Job.id,
            status=row.Job.status,
            progress_pct=row.Job.progress_pct,
            output_url=row.Job.output_url,
            property_name=row.name,
        )
        for row in rows
    ]


@router.get("/{job_id}", response_model=JobOut)
async def get_job(job_id: str, _: ActiveUser, db: AsyncSession = Depends(get_db)):
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/start", response_model=JobOut)
async def start_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    _: ActiveUser,
    db: AsyncSession = Depends(get_db),
):
    """Trigger the ingest pipeline for a job that has assets uploaded."""
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status not in (JobStatus.PENDING, JobStatus.FAILED):
        raise HTTPException(status_code=409, detail=f"Job is already {job.status}")
    if not job.assets:
        raise HTTPException(status_code=422, detail="No assets uploaded — upload files first")

    from app import pipeline
    background_tasks.add_task(pipeline.run, job_id)

    job.status = JobStatus.INGESTING
    job.progress_pct = 5
    job.error_message = None
    await db.commit()
    await db.refresh(job)
    return job


@router.get("/{job_id}/debug")
async def debug_job(job_id: str, _: ActiveUser, db: AsyncSession = Depends(get_db)):
    """Debug endpoint: shows assets, storage state, and runs ingest stage directly."""
    from app.services import storage_service
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    assets_info = []
    for asset in job.assets:
        exists = storage_service.key_exists(asset.s3_key)
        assets_info.append({
            "id": asset.id,
            "type": str(asset.asset_type),
            "filename": asset.original_filename,
            "s3_key": asset.s3_key,
            "exists_in_storage": exists,
        })

    # Try running ingest directly and report result
    ingest_result = None
    ingest_error = None
    try:
        from app.pipeline import _MockTask
        from app.workers.ingest import _run_async as ingest_async
        mock = _MockTask()
        ingest_result = await ingest_async(mock, job_id)
    except Exception as exc:
        import traceback
        ingest_error = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"

    return {
        "job_id": job_id,
        "status": str(job.status),
        "progress_pct": job.progress_pct,
        "asset_count": len(job.assets),
        "assets": assets_info,
        "ingest_result": ingest_result,
        "ingest_error": ingest_error,
    }


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: str, _: ActiveUser, db: AsyncSession = Depends(get_db)):
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    await db.delete(job)
    await db.commit()
