"""
Feature 3: Retriever agent.
Given a question, returns the top-k most relevant chunks from the vector
store built by src/ingest.py. This answers "from your documents" questions.

Uses Google's official endpoint and a separate Google embedding index.
"""
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from pathlib import Path

from src.config import VECTOR_DB_PATH, COLLECTION_NAME
from src.llm import create_embeddings
from src.state import AgentState


def _get_vectorstore():
    if not Path(VECTOR_DB_PATH).is_dir():
        raise RuntimeError("Google document index is missing. Run python -m src.ingest first.")
    embeddings = create_embeddings()
    client = QdrantClient(path=VECTOR_DB_PATH)
    try:
        return QdrantVectorStore(client=client, collection_name=COLLECTION_NAME, embedding=embeddings)
    except Exception:
        client.close()
        raise


def retriever_agent(state: AgentState) -> dict:
    vectorstore = _get_vectorstore()
    try:
        docs = vectorstore.as_retriever(search_kwargs={"k": 4}).invoke(state["question"])
    finally:
        vectorstore.client.close()
    return {
        "documents": state.get("documents", []) + [d.page_content for d in docs],
        "steps": state.get("steps", []) + ["retriever"],
    }
