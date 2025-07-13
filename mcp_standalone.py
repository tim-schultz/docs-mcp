#!/usr/bin/env python3
"""
Standalone MCP server entry point for Claude Desktop integration using stdio.
"""
import sys
import os
import asyncio

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import and run the stdio MCP server
from server.mcp_stdio_server import main

if __name__ == "__main__":
    asyncio.run(main())