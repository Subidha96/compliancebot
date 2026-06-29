"""ComplianceBot+ Backend — FastAPI Application."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.chat import router as chat_router
from app.api.gap_assessment import router as gap_router
from app.api.health import router as health_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: auto-ingest corpus if ChromaDB is empty."""
    try:
        from app.rag.ingest import get_collection, ingest_corpus
        import os
        collection = get_collection()
        count = collection.count()
        if count == 0:
            data_dir = settings.DATA_DIR
            if not os.path.isdir(data_dir):
                data_dir = "data_raw"
            if os.path.isdir(data_dir):
                logger.info("ChromaDB is empty — auto-ingesting corpus from %s", data_dir)
                n = ingest_corpus(raw_dir=data_dir)
                logger.info("Auto-ingest complete: %d chunks stored", n)
            else:
                logger.warning("No data directory found (tried %s and data_raw)", settings.DATA_DIR)
        else:
            logger.info("ChromaDB already has %d chunks — skipping ingest", count)
    except Exception as e:
        logger.error("Auto-ingest failed: %s", e)
    yield


app = FastAPI(
    title="ComplianceBot+ API",
    description="GRC Awareness Chatbot for Women in Kathmandu's Tech Workforce",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)
app.include_router(gap_router)
app.include_router(health_router)


@app.get("/")
async def root():
    """Root endpoint — API info."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/health",
    }
