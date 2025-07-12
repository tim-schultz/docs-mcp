# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

This project uses uv as the Python package manager.

### Core Commands
- **Run the application**: `uv run python main.py`
- **Install dependencies**: `uv sync`
- **Add new dependency**: `uv add <package_name>`
- **Lint code**: `uv run ruff check .`
- **Auto-fix linting issues**: `uv run ruff check . --fix`
- **Format code**: `uv run ruff format .`
- **Type check**: `uv run mypy .`

### Python Environment
- Requires Python >=3.9
- Uses uv for dependency management and virtual environment handling
- Lock file: `uv.lock`

## Project Structure

This is a minimal Python project with:
- `main.py`: Entry point with a simple "Hello from maiar-mcp!" message
- `pyproject.toml`: Project configuration and dependencies
- `uv.lock`: Dependency lock file
- Empty `README.md`

## Code Style

The project uses Ruff for linting and formatting with these settings:
- Line length: 88 characters
- Target: Python 3.8+
- Enabled rules: pycodestyle (E,W), Pyflakes (F), isort (I), flake8-bugbear (B), flake8-comprehensions (C4), pyupgrade (UP)
- Ignores E501 (line too long, handled by formatter)

## Type Checking

MyPy is configured with strict settings:
- Requires type annotations for all function definitions
- Disallows untyped or incomplete function definitions
- Warns about unused configurations and redundant casts
- Shows error codes and column numbers for better debugging

## Architecture Notes

Currently a minimal single-file Python application. The name "maiar-mcp" suggests this may be intended as an MCP (Model Context Protocol) server, but no MCP-specific code is present yet.

## Development Workflow

- Whenever you finish making a set of changes use mypy and ruff to ensure that all changes are properly types and formatted