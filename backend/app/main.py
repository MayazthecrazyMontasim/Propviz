from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db
from app.api.auth import router as auth_router
from app.api.jobs import router as jobs_router
from app.api.assets import router as assets_router

_LOCAL_STORAGE = Path(__file__).parent.parent / "local_storage"
_LOCAL_STORAGE.mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="PropViz-AI API",
    description="AI-powered immersive real estate video generation",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(assets_router, prefix="/api/v1")

app.mount("/local", StaticFiles(directory=str(_LOCAL_STORAGE)), name="local")


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
