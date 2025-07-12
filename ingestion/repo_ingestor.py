"""
Use gitingest to convert a GitHub repo (or local path) into Markdown documents.
Each repo file becomes one LangChain `Document` with metadata describing origin.
"""
from __future__ import annotations

# Type imports handled by __future__ annotations
from gitingest import ingest
from langchain_core.documents import Document


def ingest_repo(repo: str, *, token: str | None = None) -> list[Document]:
    """
    Ingest a repository using gitingest and convert to LangChain Documents.

    Args:
        repo: Repository URL or local path
        token: Optional GitHub token for private repos

    Returns:
        List of Document objects with repo file contents and metadata
    """
    summary, tree, files = ingest(repo, token=token, output="-")  # stdout -> str objects
    docs: list[Document] = []

    for f in files:  # every file dict has keys: path, content, highlight, ...
        docs.append(
            Document(
                page_content=f["content"],
                metadata={
                    "source_type": "repo",
                    "repo": repo,
                    "path": f["path"],
                    "summary": summary,
                    "tree": tree,
                },
            )
        )

    return docs
