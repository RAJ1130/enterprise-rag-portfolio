import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
VECTOR_DB_DIR = DATA_DIR / "vector_db"
SAMPLES_DIR = DATA_DIR / "samples"

for d in [DATA_DIR, DOCUMENTS_DIR, VECTOR_DB_DIR, SAMPLES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    app_name: str = "Enterprise RAG & Knowledge Base"
    version: str = "1.0.0"
    
    # LLM Settings
    llm_provider: str = os.getenv("LLM_PROVIDER", "gemini")  # "gemini", "ollama", "openai", "local_simulated"
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Embedding Settings
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "local")  # "local", "gemini", "ollama"
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "enterprise-fast-dense-384")
    
    # Retrieval Settings
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "800"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "150"))
    top_k: int = int(os.getenv("TOP_K", "4"))
    similarity_threshold: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.30"))
    hybrid_search: bool = True
    hybrid_rrf_k: int = 60
    
    # Guardrail Settings
    strict_anti_hallucination: bool = True
    citation_enforcement: bool = True
    pii_masking: bool = True
    prompt_injection_detection: bool = True

settings = Settings()
