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

from collections import defaultdict
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
        repo_docs: List of documents from the repository
        repo_url: URL of the repository for generating links
        output_file: Optional custom output file path

    Returns:
        Path to the generated summary file
    """
    if output_file is None:
        output_file = README_OUTPUT_DIR / "dir_summary.md"

    # Group docs by directory ('' for root)
    directories: dict[str, list[Document]] = defaultdict(list)
    for d in repo_docs:
        if "path" in d.metadata:
            dir_path = str(Path(d.metadata["path"]).parent)
            directories[dir_path].append(d)

    llm = ChatOpenAI(model=LLM_MODEL_NAME, temperature=0.2)

    lines: list[str] = [
        "# Repository directory overview",
        f"_Auto‑generated summary for {repo_url}_\n",
    ]

    for dir_path, docs in sorted(directories.items()):
        display_path = dir_path or "."
        # Build context for the LLM – first few hundred chars from up to 3 files
        sample_context = "\n\n".join(
            doc.page_content[:800] for doc in docs[:3]
        )

        prompt = (
            "You are generating documentation for an open‑source repository. "
            f"Write one concise paragraph (max 80 words) summarizing the overall "
            f"purpose and main components of the directory `{display_path}`.\n\n"
            "Context from representative files:\n"
            "-----\n"
            f"{sample_context}\n"
            "-----"
        )

        response = llm.invoke(prompt)
        summary_text = str(response.content).strip() if isinstance(response.content, str) else str(response.content)

        lines.append(f"## `{display_path}`")
        lines.append(summary_text)
        lines.append("\n**Files**")

        for doc in sorted(docs, key=lambda d: d.metadata.get("path", "")):
            rel_path = doc.metadata.get("path", "")
            if repo_url.startswith("http"):
                link = f"{repo_url.rstrip('/')}/blob/main/{rel_path}"
                lines.append(f"- [{rel_path}]({link})")
            else:
                lines.append(f"- {rel_path}")
        lines.append("")  # blank line spacer

    output_file.write_text("\n".join(lines))
    return output_file
