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
    vs = Chroma.from_documents(
        docs,
        embedding=_embedder,
        collection_name=collection_name,
        persist_directory=str(VECTOR_STORE_DIR / collection_name),
    )
    vs.persist()
    return vs


def load_vector_store(collection_name: str) -> Chroma:
    """
    Load an existing vector store.

    Args:
        collection_name: Name of the collection to load

    Returns:
        Chroma vector store instance
    """
    return Chroma(
        collection_name=collection_name,
        embedding_function=_embedder,
        persist_directory=str(VECTOR_STORE_DIR / collection_name),
    )


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
    try:
        vs = load_vector_store(collection_name)
        vs.add_documents(docs)
        vs.persist()
        return vs
    except Exception:
        # Collection doesn't exist, create new one
        return build_vector_store(docs, collection_name)
