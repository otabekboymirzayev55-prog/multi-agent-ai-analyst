"""Clients for Google's official OpenAI-compatible Gemini endpoint."""
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from src.config import GEMINI_BASE_URL, CHAT_MODEL, EMBED_MODEL, require_google_key

def create_chat_model():
    return ChatOpenAI(base_url=GEMINI_BASE_URL, api_key=require_google_key(), model=CHAT_MODEL, timeout=25, max_retries=1)

def create_embeddings():
    # Send text strings, not OpenAI token IDs, to the Gemini embeddings endpoint.
    return OpenAIEmbeddings(base_url=GEMINI_BASE_URL, api_key=require_google_key(), model=EMBED_MODEL, check_embedding_ctx_length=False, model_kwargs={"encoding_format": "float"}, request_timeout=25, max_retries=1)
