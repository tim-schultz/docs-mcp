"""
Model Context Protocol server implementation using stdio.
Provides search tools for repository and documentation content.
"""
from __future__ import annotations

import asyncio
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool

from agent.agent_builder import get_vector_store

DEFAULT_COLLECTION_NAME = "project"

# Create MCP server instance
server = Server("maiar-mcp")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="search_repo",
            description="Search through repository code and files",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for repository content"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="search_docs",
            description="Search through documentation content", 
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for documentation content"
                    }
                },
                "required": ["query"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[dict[str, Any]]:
    """Handle tool calls."""
    if name == "search_repo":
        return await search_repository(arguments["query"])
    elif name == "search_docs":
        return await search_documentation(arguments["query"])
    else:
        raise ValueError(f"Unknown tool: {name}")

async def search_repository(query: str) -> list[dict[str, Any]]:
    """Search repository content."""
    try:
        vs = get_vector_store(DEFAULT_COLLECTION_NAME)
        if vs is None:
            return [{"type": "text", "text": "No repository data found. Please run ingestion first."}]
        
        # Search for relevant documents
        docs = vs.similarity_search(query, k=5)
        
        if not docs:
            return [{"type": "text", "text": f"No repository content found for query: {query}"}]
        
        # Format results
        results = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Unknown")
            content = doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content
            results.append({
                "type": "text",
                "text": f"Result {i} from {source}:\n{content}\n"
            })
        
        return results
        
    except Exception as e:
        return [{"type": "text", "text": f"Error searching repository: {str(e)}"}]

async def search_documentation(query: str) -> list[dict[str, Any]]:
    """Search documentation content."""
    try:
        vs = get_vector_store(DEFAULT_COLLECTION_NAME)
        if vs is None:
            return [{"type": "text", "text": "No documentation data found. Please run documentation ingestion first."}]
        
        # Search for relevant documents with documentation filter
        docs = vs.similarity_search(query, k=5, filter={"type": "documentation"})
        
        if not docs:
            # Fallback to general search if no docs-specific content
            docs = vs.similarity_search(query, k=5)
            if not docs:
                return [{"type": "text", "text": f"No documentation content found for query: {query}"}]
        
        # Format results
        results = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Unknown")
            title = doc.metadata.get("title", "")
            content = doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content
            
            result_text = f"Result {i}"
            if title:
                result_text += f" - {title}"
            result_text += f" from {source}:\n{content}\n"
            
            results.append({
                "type": "text", 
                "text": result_text
            })
        
        return results
        
    except Exception as e:
        return [{"type": "text", "text": f"Error searching documentation: {str(e)}"}]

async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())