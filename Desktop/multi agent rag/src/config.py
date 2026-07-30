"""
Config — PHASE 4 UPDATE: adds optional Langfuse observability setup.
If LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY are set in .env, every
agent call is automatically traced and visible in your Langfuse dashboard.
If the keys are missing, the project runs fine without any tracing.
"""
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PROXY_BASE_URL = os.getenv("PROXY_BASE_URL")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")
GEMINI_LITE_MODEL = os.getenv("GEMINI_LITE_MODEL")
GEMINI_EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")

VECTOR_DB_PATH = "data/qdrant_db"
COLLECTION_NAME = "company_docs"
SQLITE_DB_PATH = "data/company.db"

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Copy .env.example to .env and paste in "
        "the key your mentor gave you."
    )

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
