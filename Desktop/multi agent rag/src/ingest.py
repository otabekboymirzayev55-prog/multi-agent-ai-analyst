"""Build a new Google embedding index without deleting previous data."""
from pathlib import Path
from uuid import uuid4
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from src.config import BASE_DIR, VECTOR_DB_PATH, COLLECTION_NAME
from src.llm import create_embeddings

DOCS_FOLDER = BASE_DIR / 'data/sample_docs'

def load_documents():
    docs = []
    for path in sorted(DOCS_FOLDER.glob('*.txt')):
        docs.extend(TextLoader(str(path), encoding='utf-8').load())
    return docs

def main():
    target = Path(VECTOR_DB_PATH)
    if target.exists():
        raise RuntimeError('Index path already exists. Set a new GOOGLE_INDEX_VERSION before rebuilding; previous indexes are preserved.')
    docs = load_documents()
    chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150).split_documents(docs)
    if not chunks:
        raise RuntimeError('No document text found to index')
    embeddings = create_embeddings()
    staging = target.with_name(target.name + '.building-' + uuid4().hex)
    store = QdrantVectorStore.from_documents(chunks, embedding=embeddings, path=str(staging), collection_name=COLLECTION_NAME)
    store.client.close()
    staging.rename(target)
    print(f'Indexed {len(chunks)} chunks in {target.name}. Previous indexes were not changed.')

if __name__ == '__main__': main()
