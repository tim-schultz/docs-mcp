"""Configuration settings for the maiar-mcp project."""
from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent

# Persistent data (vector store, temp downloads, summaries)
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

VECTOR_STORE_DIR = DATA_DIR / "vectordb"
VECTOR_STORE_DIR.mkdir(exist_ok=True)

# Where to place generated directory-level README files
README_OUTPUT_DIR = DATA_DIR / "summaries"
README_OUTPUT_DIR.mkdir(exist_ok=True)

# Embedding model
EMBED_MODEL_NAME = "text-embedding-3-small"

# Default chunking parameters
DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 200

# LLM model for summaries and agent
LLM_MODEL_NAME = "gpt-4o-mini"

# Server configuration
DEFAULT_PORT = 8000
DEFAULT_HOST = "0.0.0.0"
