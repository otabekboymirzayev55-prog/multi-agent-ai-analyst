from pathlib import Path

from pypdf import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

import config
from gem import embed


def load_chunks(pdf_path: Path, size: int = 900, overlap: int = 150):
    """Read the PDF and cut each page into small overlapping pieces."""
    reader = PdfReader(str(pdf_path))
    chunks = []
    for page_no, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if not text:
            continue
        start = 0
        while start < len(text):
            piece = text[start : start + size]
            chunks.append({"text": piece, "page": page_no})
            start += size - overlap
    return chunks


def resolve_pdf_path() -> Path:
    candidates = [config.PDF_PATH, config.ROOT_PDF_PATH]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "Missing PDF. Add the chosen loan document as docs/loan_terms.pdf "
        "or as loan_terms.pdf in the repo root."
    )


def main():
    pdf_path = resolve_pdf_path()
    chunks = load_chunks(pdf_path)
    print(f"Loaded {len(chunks)} chunks from {pdf_path}")

    dim = len(embed("dimension probe"))
    print(f"Embedding size = {dim}")

    unique_texts = {}

    client = QdrantClient(
        url=config.QDRANT_URL,
        api_key=config.QDRANT_API_KEY,
    )

    try:
        if client.collection_exists(config.COLLECTION):
            client.delete_collection(config.COLLECTION)

        client.create_collection(
            collection_name=config.COLLECTION,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )

        points = []
        for i, chunk in enumerate(chunks):
            print(f"Embedding chunk {i+1}/{len(chunks)}...")
            text = chunk["text"]
            if text not in unique_texts:
                unique_texts[text] = embed(text)
            points.append(
                PointStruct(
                    id=i,
                    vector=unique_texts[text],
                    payload={
                        "text": text,
                        "page": chunk["page"],
                        "chunk": i,
                    },
                )
            )

        client.upsert(collection_name=config.COLLECTION, points=points)
        print(f"Stored {len(points)} clauses in Qdrant Cloud. Done!")
    finally:
        client.close()


if __name__ == "__main__":
    main()
