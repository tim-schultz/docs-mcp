"""
Main CLI entry point for the maiar-mcp project.
Orchestrates repository ingestion, documentation scraping, and MCP server.
"""
from __future__ import annotations

# Type imports handled by __future__ annotations
import click
from dotenv import load_dotenv

from ingestion.docs_scraper import scrape_docs
from ingestion.repo_ingestor import ingest_repo
from processing.chunker import chunk_documents
from server.mcp_server import run_server
from summaries.dir_summarizer import summarise_directories
from vectordb.vector_store import add_documents_to_store

# Load environment variables
load_dotenv()


@click.group()
def cli() -> None:
    """Maiar MCP - GitHub Repository Analysis and Query System."""
    pass


@cli.command()
@click.option(
    "--repo",
    required=True,
    help="GitHub repository URL or local path"
)
@click.option(
    "--docs-url",
    help="Documentation website URL (optional)"
)
@click.option(
    "--token",
    help="GitHub token for private repositories"
)
@click.option(
    "--collection",
    default="project",
    help="Vector store collection name"
)
def ingest(
    repo: str,
    docs_url: str | None,
    token: str | None,
    collection: str
) -> None:
    """Ingest repository and documentation into vector database."""
    click.echo(f"🔄 Ingesting repository: {repo}")

    # Ingest repository
    repo_docs = ingest_repo(repo, token=token)
    click.echo(f"📁 Found {len(repo_docs)} repository files")

    # Chunk repository documents
    repo_chunks = chunk_documents(repo_docs)
    click.echo(f"🔧 Created {len(repo_chunks)} repository chunks")

    # Add to vector store
    add_documents_to_store(repo_chunks, collection)
    click.echo(f"💾 Stored repository chunks in collection '{collection}'")

    # Generate directory summaries
    summary_file = summarise_directories(repo_docs, repo)
    click.echo(f"📝 Generated directory summary: {summary_file}")

    # Ingest documentation if provided
    if docs_url:
        click.echo(f"🔄 Scraping documentation: {docs_url}")
        try:
            docs = scrape_docs(docs_url)
            click.echo(f"📖 Found {len(docs)} documentation pages")

            # Chunk documentation
            doc_chunks = chunk_documents(docs)
            click.echo(f"🔧 Created {len(doc_chunks)} documentation chunks")

            # Add to vector store
            add_documents_to_store(doc_chunks, collection)
            click.echo(f"💾 Stored documentation chunks in collection '{collection}'")
        except Exception as e:
            click.echo(f"⚠️ Failed to scrape documentation: {e}")

    click.echo("✅ Ingestion complete!")


@cli.command()
@click.option(
    "--host",
    default="0.0.0.0",
    help="Host to bind the server to"
)
@click.option(
    "--port",
    default=8000,
    help="Port to bind the server to"
)
def serve(host: str, port: int) -> None:
    """Start the MCP server."""
    click.echo(f"🚀 Starting MCP server on {host}:{port}")
    run_server(host, port)


@cli.command()
@click.option(
    "--repo",
    required=True,
    help="GitHub repository URL or local path"
)
@click.option(
    "--docs-url",
    help="Documentation website URL (optional)"
)
@click.option(
    "--token",
    help="GitHub token for private repositories"
)
@click.option(
    "--collection",
    default="project",
    help="Vector store collection name"
)
@click.option(
    "--host",
    default="0.0.0.0",
    help="Host to bind the server to"
)
@click.option(
    "--port",
    default=8000,
    help="Port to bind the server to"
)
def run(
    repo: str,
    docs_url: str | None,
    token: str | None,
    collection: str,
    host: str,
    port: int,
) -> None:
    """Run the full pipeline: ingest and serve."""
    # First ingest
    from click.testing import CliRunner
    runner = CliRunner()

    ingest_args = ["ingest", "--repo", repo, "--collection", collection]
    if docs_url:
        ingest_args.extend(["--docs-url", docs_url])
    if token:
        ingest_args.extend(["--token", token])

    result = runner.invoke(cli, ingest_args)
    if result.exit_code != 0:
        click.echo(f"❌ Ingestion failed: {result.output}")
        return

    # Then serve
    click.echo(f"🚀 Starting MCP server on {host}:{port}")
    run_server(host, port)


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
