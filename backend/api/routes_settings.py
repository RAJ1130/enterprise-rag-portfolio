from typing import Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter
from core.config import settings
from core.vector_store import get_shared_vector_store

router = APIRouter(prefix="/api/settings", tags=["settings"])

vector_store = get_shared_vector_store()


class SettingsUpdate(BaseModel):
    llm_provider: Optional[str] = None
    gemini_api_key: Optional[str] = None
    gemini_model: Optional[str] = None
    ollama_base_url: Optional[str] = None
    ollama_model: Optional[str] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    top_k: Optional[int] = None
    similarity_threshold: Optional[float] = None
    strict_anti_hallucination: Optional[bool] = None

@router.get("")
def get_current_settings():
    return {
        "llm_provider": settings.llm_provider,
        "has_gemini_key": bool(settings.gemini_api_key),
        "gemini_model": settings.gemini_model,
        "ollama_base_url": settings.ollama_base_url,
        "ollama_model": settings.ollama_model,
        "embedding_provider": settings.embedding_provider,
        "embedding_model": settings.embedding_model,
        "chunk_size": settings.chunk_size,
        "chunk_overlap": settings.chunk_overlap,
        "top_k": settings.top_k,
        "similarity_threshold": settings.similarity_threshold,
        "strict_anti_hallucination": settings.strict_anti_hallucination,
        "citation_enforcement": settings.citation_enforcement,
        "prompt_injection_detection": settings.prompt_injection_detection
    }

@router.post("")
def update_settings(update: SettingsUpdate):
    if update.llm_provider is not None:
        settings.llm_provider = update.llm_provider
    if update.gemini_api_key is not None:
        settings.gemini_api_key = update.gemini_api_key
    if update.gemini_model is not None:
        settings.gemini_model = update.gemini_model
    if update.ollama_base_url is not None:
        settings.ollama_base_url = update.ollama_base_url
    if update.ollama_model is not None:
        settings.ollama_model = update.ollama_model
    if update.chunk_size is not None:
        settings.chunk_size = update.chunk_size
    if update.chunk_overlap is not None:
        settings.chunk_overlap = update.chunk_overlap
    if update.top_k is not None:
        settings.top_k = update.top_k
    if update.similarity_threshold is not None:
        settings.similarity_threshold = update.similarity_threshold
    if update.strict_anti_hallucination is not None:
        settings.strict_anti_hallucination = update.strict_anti_hallucination

    return {"status": "updated", "current_settings": get_current_settings()}

@router.get("/stats")
def get_system_stats():
    stats = vector_store.get_stats()
    stats["app_name"] = settings.app_name
    stats["version"] = settings.version
    stats["active_llm"] = settings.llm_provider
    stats["active_embedder"] = settings.embedding_provider
    return stats
