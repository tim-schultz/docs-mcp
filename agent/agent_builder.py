"""
LangChain agent with two tools:
  • search_repo  – semantic search across code chunks
  • search_docs  – semantic search across documentation chunks
"""
from __future__ import annotations

from typing import Any

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from config import LLM_MODEL_NAME
from vectordb.vector_store import load_vector_store

# Global variable for lazy loading
_vectorstore: Any | None = None


@tool("search_repo", return_direct=True)
def search_repo(query: str) -> str:
    """Searches code chunks only."""
    return _search(query, filter_dict={"source_type": "repo"})


@tool("search_docs", return_direct=True)
def search_docs(query: str) -> str:
    """Searches documentation chunks only."""
    return _search(query, filter_dict={"source_type": "docs"})


def _search(query: str, filter_dict: dict[str, str]) -> str:
    """Internal search function with filtering."""
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = load_vector_store("project")

    retriever = _vectorstore.as_retriever(
        search_kwargs={"k": 6, "filter": filter_dict}
    )
    docs = retriever.get_relevant_documents(query)
    return "\n---\n".join(d.page_content for d in docs)


TOOLS = [search_repo, search_docs]


def build_agent() -> AgentExecutor:
    """
    Build a LangChain agent with repo and docs search tools.

    Returns:
        AgentExecutor instance ready to handle queries
    """
    llm = ChatOpenAI(model=LLM_MODEL_NAME, temperature=0.0)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You answer questions about a GitHub project. "
            "Use `search_repo` for code questions and `search_docs` for usage "
            "or conceptual questions. Be concise and helpful.",
        ),
        ("user", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, TOOLS, prompt)
    return AgentExecutor(agent=agent, tools=TOOLS, verbose=True)
