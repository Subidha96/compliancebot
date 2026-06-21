"""Health check API endpoint — system readiness and diagnostics."""
import logging

from fastapi import APIRouter

from app.core.config import settings
from app.models.schemas import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/api/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return system health status including model and ChromaDB state."""
    model_loaded = False
    chromadb_connected = False
    corpus_size = 0

    # Check model
    try:
        from app.llm.model_loader import get_model
        model = get_model()
        model_loaded = model is not None
    except Exception as e:
        logger.warning("Model health check failed: %s", e)

    # Check ChromaDB
    try:
        from app.rag.ingest import get_collection
        collection = get_collection()
        corpus_size = collection.count()
        chromadb_connected = True
    except Exception as e:
        logger.warning("ChromaDB health check failed: %s", e)

    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        model_loaded=model_loaded,
        chromadb_connected=chromadb_connected,
        corpus_size=corpus_size,
    )
