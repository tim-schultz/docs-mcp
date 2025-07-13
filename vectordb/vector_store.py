"""
Vector store helpers for Chroma.
"""
from __future__ import annotations

# Type imports handled by __future__ annotations
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from config import EMBED_MODEL_NAME, VECTOR_STORE_DIR

_embedder = OpenAIEmbeddings(model=EMBED_MODEL_NAME)


def build_vector_store(docs: list[Document], collection_name: str) -> Chroma:
    """
    Create a new vector store from documents.

    Args:
        docs: Documents to embed and store
        collection_name: Name for the collection

    Returns:
        Chroma vector store instance
    """
    # Process documents in batches to avoid OpenAI token limits
    batch_size = 100  # Process 100 documents at a time
    
    if not docs:
        # Create empty vector store if no documents
        vs = Chroma(
            collection_name=collection_name,
            embedding_function=_embedder,
            persist_directory=str(VECTOR_STORE_DIR / collection_name),
        )
        vs.persist()
        return vs
    
    # Create initial vector store with first batch
    first_batch = docs[:batch_size]
    vs = Chroma.from_documents(
        first_batch,
        embedding=_embedder,
        collection_name=collection_name,
        persist_directory=str(VECTOR_STORE_DIR / collection_name),
    )
    vs.persist()
    
    # Add remaining documents in batches
    for i in range(batch_size, len(docs), batch_size):
        batch = docs[i:i + batch_size]
        vs.add_documents(batch)
        vs.persist()
    
    return vs


def load_vector_store(collection_name: str) -> Chroma | None:
    """
    Load an existing vector store.

    Args:
        collection_name: Name of the collection to load

    Returns:
        Chroma vector store instance or None if not found
    """
    try:
        collection_path = VECTOR_STORE_DIR / collection_name
        if not collection_path.exists():
            return None

        return Chroma(
            collection_name=collection_name,
            embedding_function=_embedder,
            persist_directory=str(collection_path),
        )
    except Exception:
        return None


def add_documents_to_store(
    docs: list[Document],
    collection_name: str
) -> Chroma:
    """
    Add documents to an existing vector store or create new one.

    Args:
        docs: Documents to add
        collection_name: Name of the collection

    Returns:
        Updated Chroma vector store instance
    """
    vs = load_vector_store(collection_name)
    if vs is not None:
        # Add documents in batches to avoid token limits
        batch_size = 100
        for i in range(0, len(docs), batch_size):
            batch = docs[i:i + batch_size]
            vs.add_documents(batch)
            vs.persist()
        return vs
    else:
        # Collection doesn't exist, create new one
        return build_vector_store(docs, collection_name)
