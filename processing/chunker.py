"""
Semantically-friendly chunking (recursive on paragraphs/lines).
"""
from __future__ import annotations

# Type imports handled by __future__ annotations
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE


def chunk_documents(
    docs: list[Document],
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Document]:
    """
    Split documents into smaller chunks for better vector search.

    Args:
        docs: List of documents to chunk
        chunk_size: Maximum size of each chunk
        chunk_overlap: Overlap between consecutive chunks

    Returns:
        List of chunked documents with preserved metadata
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " "],
    )

    out: list[Document] = []
    for d in docs:
        chunks = splitter.split_text(d.page_content)
        for i, chunk in enumerate(chunks):
            meta = d.metadata.copy()
            meta["chunk_index"] = i
            meta["total_chunks"] = len(chunks)
            out.append(Document(page_content=chunk, metadata=meta))

    return out
