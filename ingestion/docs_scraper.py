"""
Scrape documentation pages (sitemap) and convert to LangChain `Document`s.
"""
from __future__ import annotations

# Type imports handled by __future__ annotations
from langchain_community.document_loaders.sitemap import SitemapLoader
from langchain_core.documents import Document


def scrape_docs(base_url: str, restrict_domain: bool = True) -> list[Document]:
    """
    Scrape documentation from a website using sitemap.

    Args:
        base_url: Base URL of the documentation site
        restrict_domain: Whether to restrict scraping to the same domain

    Returns:
        List of Document objects with documentation content and metadata
    """
    loader = SitemapLoader(
        web_path=base_url,
        restrict_to_same_domain=restrict_domain
    )
    docs = loader.load()

    # Add metadata to identify these as documentation
    for d in docs:
        d.metadata.update({
            "source_type": "docs",
            "docs_base": base_url
        })

    return docs
