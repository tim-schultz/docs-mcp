# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

This project uses uv as the Python package manager.

### Core Commands
- **Install dependencies**: `uv sync`
- **Add new dependency**: `uv add <package_name>`
- **Lint code**: `uv run ruff check .`
- **Auto-fix linting issues**: `uv run ruff check . --fix --unsafe-fixes`
- **Format code**: `uv run ruff format .`
- **Type check**: `uv run mypy .`

### Application Commands
- **Ingest repository only**: `uv run python main.py ingest --repo <url>`
- **Ingest with docs**: `uv run python main.py ingest --repo <url> --docs-url <docs-url>`
- **Start MCP server**: `uv run python main.py serve`
- **Full pipeline**: `uv run python main.py run --repo <url>`

### Python Environment
- Requires Python >=3.10 (due to onnxruntime dependency)
- Uses uv for dependency management and virtual environment handling
- Lock file: `uv.lock`

## Project Structure

GitHub repository analysis and MCP server system with modular architecture:

```
maiar-mcp/
├── main.py                 # CLI entry point with click commands
├── config.py               # Configuration settings and paths
├── ingestion/              # Data ingestion modules
│   ├── repo_ingestor.py    # GitIngest integration for repositories
│   └── docs_scraper.py     # Documentation scraping via sitemap
├── processing/             # Text processing modules
│   └── chunker.py          # Semantic text chunking for vector storage
├── vectordb/               # Vector database operations
│   └── vector_store.py     # Chroma vector store with embeddings
├── summaries/              # Directory summarization
│   └── dir_summarizer.py   # LLM-generated directory overviews
├── agent/                  # LangChain agent system
│   └── agent_builder.py    # Agent with repo/docs search tools
└── server/                 # MCP server implementation
    └── mcp_server.py       # FastAPI server exposing agent via MCP
```

## Key Features

- **Repository Ingestion**: Uses gitingest to convert GitHub repos to LangChain Documents
- **Documentation Scraping**: Extracts content from documentation websites via sitemap
- **Semantic Chunking**: Splits content into overlapping chunks for better vector search
- **Vector Storage**: Persistent Chroma database with OpenAI embeddings
- **Directory Summaries**: AI-generated README-style overviews of repository structure
- **Dual Search**: Independent search across code and documentation content
- **MCP Server**: Model Context Protocol server for external integration

## Code Style

The project uses Ruff for linting and formatting with these settings:
- Line length: 88 characters
- Target: Python 3.10+
- Enabled rules: pycodestyle (E,W), Pyflakes (F), isort (I), flake8-bugbear (B), flake8-comprehensions (C4), pyupgrade (UP)
- Ignores E501 (line too long, handled by formatter)

## Type Checking

MyPy is configured with strict settings:
- Requires type annotations for all function definitions
- Disallows untyped or incomplete function definitions
- Warns about unused configurations and redundant casts
- Shows error codes and column numbers for better debugging
- Uses Python 3.10 union syntax (X | None instead of Optional[X])

## Environment Variables

Required environment variables (create `.env` file):
- `OPENAI_API_KEY`: OpenAI API key for embeddings and LLM calls

## Data Storage

- `data/vectordb/`: Persistent Chroma vector database collections
- `data/summaries/`: Generated directory overview markdown files

## Development Workflow

- Whenever you finish making a set of changes use mypy and ruff to ensure that all changes are properly types and formatted