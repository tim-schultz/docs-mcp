"""
Generate a Markdown README-like overview summarizing each directory in the repo.

Approach
--------
1. Group repo `Document`s by their directory path.
2. Use an LLM to craft a 1–2 sentence summary for each directory, given sample
   file contents as context.
3. Append a bullet‑list of files with clickable GitHub links.
"""
from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

from config import LLM_MODEL_NAME, README_OUTPUT_DIR


def summarise_directories(
    repo_docs: list[Document],
    repo_url: str,
    output_file: Path | None = None
) -> Path:
    """
    Generate directory summaries for a repository.

    Args:
        repo_docs: List of documents from the repository (single consolidated doc from gitingest)
        repo_url: URL of the repository for generating links
        output_file: Optional custom output file path

    Returns:
        Path to the generated summary file
    """
    if output_file is None:
        output_file = README_OUTPUT_DIR / "dir_summary.md"

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # With gitingest, we get a single consolidated document
    if not repo_docs:
        # Create minimal summary if no docs
        lines = [
            "# Repository Overview",
            f"_Auto-generated summary for {repo_url}_\n",
            "No content available for analysis."
        ]
        output_file.write_text("\n".join(lines))
        return output_file

    # Get the first (and likely only) document
    repo_doc = repo_docs[0]

    llm = ChatOpenAI(model=LLM_MODEL_NAME, temperature=0.2)

    # Extract directory structure from tree metadata if available
    tree_structure = repo_doc.metadata.get("tree", "")

    # Create a high-level summary using the consolidated content and tree structure
    prompt = (
        "You are generating documentation for an open-source repository. "
        "Based on the repository content and file tree provided, write a comprehensive "
        "overview of the project structure and main components (max 200 words).\n\n"
        "Repository file tree:\n"
        "-----\n"
        f"{tree_structure[:1500]}...\n"  # Limit tree size
        "-----\n\n"
        "Repository content sample:\n"
        "-----\n"
        f"{repo_doc.page_content[:2000]}...\n"  # First 2000 chars
        "-----"
    )

    response = llm.invoke(prompt)
    summary_text = str(response.content).strip() if isinstance(response.content, str) else str(response.content)

    lines = [
        "# Repository Overview",
        f"_Auto-generated summary for {repo_url}_\n",
        summary_text,
        "\n## Project Structure",
    ]

    # Add tree structure if available
    if tree_structure:
        lines.append("```")
        lines.append(tree_structure[:2000])  # Limit tree output
        lines.append("```")

    # Add repository summary from metadata
    if repo_doc.metadata.get("summary"):
        lines.extend([
            "\n## Repository Summary",
            repo_doc.metadata["summary"]
        ])

    output_file.write_text("\n".join(lines))
    return output_file
