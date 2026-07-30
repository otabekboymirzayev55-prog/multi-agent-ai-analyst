"""
Feature 2: Ingestion & vector store.
Run this once (and again any time you add new documents) to load the
files in data/sample_docs, split them into chunks, embed them with
Gemini (via the proxy), and store them in a local Qdrant collection.

PROXY UPDATE: now uses OpenAIEmbeddings pointed at the mentor's proxy
instead of calling Google directly. Model: gemini-embedding.

IMPORTANT: because the embedding model changed, any OLD vector store
built with the previous (direct Google) embeddings is not compatible.
Delete data/qdrant_db/ before running this again:
    rmdir /s /q data\qdrant_db      (Windows)
    rm -rf data/qdrant_db           (Mac/Linux)

Run it with:  python -m src.ingest
"""
import os
import shutil
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

from src.config import GEMINI_API_KEY, PROXY_BASE_URL, VECTOR_DB_PATH, COLLECTION_NAME

DOCS_FOLDER = "data/sample_docs"


def load_documents():
    docs = []
    for filename in os.listdir(DOCS_FOLDER):
        if filename.endswith(".txt"):
            path = os.path.join(DOCS_FOLDER, filename)
            docs.extend(TextLoader(path, encoding="utf-8").load())
    return docs


def main():
    # Wipe any old vector store built with the previous embedding model —
    # a mismatched vector size will otherwise fail silently or error out.
    if os.path.exists(VECTOR_DB_PATH):
        shutil.rmtree(VECTOR_DB_PATH)
        print(f"Removed old vector store at {VECTOR_DB_PATH} (embedding model changed).")

    print(f"Loading documents from {DOCS_FOLDER} ...")
    docs = load_documents()
    print(f"Loaded {len(docs)} document(s).")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(docs)
    print(f"Split into {len(chunks)} chunks.")

    embeddings = OpenAIEmbeddings(
        base_url=PROXY_BASE_URL, api_key=GEMINI_API_KEY, model="gemini-embedding"
    )

    # from_documents creates the collection automatically with the right
    # vector size — no need to hardcode a dimension.
    QdrantVectorStore.from_documents(
        chunks,
        embedding=embeddings,
        path=VECTOR_DB_PATH,
        collection_name=COLLECTION_NAME,
    )
    print(f"Stored {len(chunks)} chunks in Qdrant collection '{COLLECTION_NAME}'.")
    print("Done. You can now run: python -m tests.test_retriever")


if __name__ == "__main__":
    main()
