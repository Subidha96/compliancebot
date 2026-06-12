"""ComplianceBot+ Backend — FastAPI Application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.chat import router as chat_router

app = FastAPI(
    title="ComplianceBot+ API",
    description="GRC Awareness Chatbot for Women in Kathmandu's Tech Workforce",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


@app.get("/health")
async def health_check():
    """Liveness probe endpoint."""
    return {"status": "healthy", "version": "0.1.0"}
