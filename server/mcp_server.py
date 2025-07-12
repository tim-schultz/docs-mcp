"""
Expose the agent via Model Context Protocol so any MCP‑aware client can connect.
"""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent.agent_builder import build_agent
from config import DEFAULT_HOST, DEFAULT_PORT

app = FastAPI(title="GitRepo+Docs MCP Server")

# Global agent instance
_agent_executor = None


class QueryRequest(BaseModel):
    """Request model for queries."""
    query: str


class QueryResponse(BaseModel):
    """Response model for queries."""
    result: str


def get_agent() -> Any:
    """Get or create the agent executor."""
    global _agent_executor
    if _agent_executor is None:
        _agent_executor = build_agent()
    return _agent_executor


@app.post("/ask", response_model=QueryResponse)
async def ask(request: QueryRequest) -> QueryResponse:
    """
    Ask any question about the repository or its documentation.

    Args:
        request: Query request with the question

    Returns:
        Query response with the answer
    """
    try:
        agent = get_agent()
        result = agent.invoke({"input": request.query})
        return QueryResponse(result=result.get("output", "No response"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint with service information."""
    return {
        "service": "GitRepo+Docs MCP Server",
        "endpoints": {
            "ask": "POST /ask - Ask questions about the repository",
            "health": "GET /health - Health check",
        }
    }


def run_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    """
    Run the MCP server.

    Args:
        host: Host to bind to
        port: Port to bind to
    """
    import uvicorn
    uvicorn.run(app, host=host, port=port)
