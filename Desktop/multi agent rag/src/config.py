"""
Config — PHASE 4 UPDATE: adds optional Langfuse observability setup.
If LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY are set in .env, every
agent call is automatically traced and visible in your Langfuse dashboard.
If the keys are missing, the project runs fine without any tracing.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
from dotenv import load_dotenv

load_dotenv(BASE_DIR / ".env")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
CHAT_MODEL = os.getenv("GOOGLE_CHAT_MODEL", "gemini-3.5-flash-lite")
EMBED_MODEL = os.getenv("GOOGLE_EMBED_MODEL", "gemini-embedding-001")
INDEX_VERSION = os.getenv("GOOGLE_INDEX_VERSION", "v1")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
VECTOR_DB_PATH = str(BASE_DIR / "data" / ("qdrant_google_" + EMBED_MODEL.replace("-", "_") + "_" + INDEX_VERSION))
COLLECTION_NAME = "company_docs_google_" + EMBED_MODEL.replace("-", "_") + "_" + INDEX_VERSION
SQLITE_DB_PATH = str(BASE_DIR / "data/company.db")

def require_google_key():
    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY is missing. Add a Google AI Studio key to the server environment.")
    return GOOGLE_API_KEY

# --- Feature 12: Langfuse tracing (optional) ---
# If keys are present, patch LangChain so every call is automatically traced.
if LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY:
    try:
        from langfuse.callback import CallbackHandler
        langfuse_handler = CallbackHandler(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY,
        )
        print("Langfuse tracing enabled — visit https://cloud.langfuse.com to see traces.")
    except ImportError:
        langfuse_handler = None
        print("Langfuse keys found but package not installed. Run: pip install langfuse")
else:
    langfuse_handler = None  # tracing is off, project runs normally
