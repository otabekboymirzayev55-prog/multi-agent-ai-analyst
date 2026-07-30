"""
Feature 3: Retriever agent.
Given a question, returns the top-k most relevant chunks from the vector
store built by src/ingest.py. This answers "from your documents" questions.

PROXY UPDATE: now uses OpenAIEmbeddings pointed at the mentor's proxy
instead of calling Google directly. Model: gemini-embedding.
"""
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from src.config import GEMINI_API_KEY, PROXY_BASE_URL, VECTOR_DB_PATH, COLLECTION_NAME
from src.state import AgentState


def _get_vectorstore():
    embeddings = OpenAIEmbeddings(
        base_url=PROXY_BASE_URL, api_key=GEMINI_API_KEY, model="gemini-embedding"
    )
    client = QdrantClient(path=VECTOR_DB_PATH)
    return QdrantVectorStore(client=client, collection_name=COLLECTION_NAME, embedding=embeddings)


def retriever_agent(state: AgentState) -> dict:
    vectorstore = _get_vectorstore()
    docs = vectorstore.as_retriever(search_kwargs={"k": 4}).invoke(state["question"])
    return {
        "documents": state.get("documents", []) + [d.page_content for d in docs],
        "steps": state.get("steps", []) + ["retriever"],
    }
