"""
TikTok MCP Server - Main entry point
"""
import asyncio
import os
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
)

from .tiktok_client import SyncTikTokClient
from .tools import register_tools


async def _async_main():
    """Main async entry point for the TikTok MCP server."""
    # Get credentials from environment
    # Official API credentials (if available)
    client_key = os.getenv("TIKTOK_CLIENT_KEY")
    client_secret = os.getenv("TIKTOK_CLIENT_SECRET")
    access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
    
    # Initialize TikTok client (sync wrapper for MCP compatibility)
    tiktok_client = SyncTikTokClient(
        client_key=client_key,
        client_secret=client_secret,
        access_token=access_token,
    )
    
    # Create MCP server
    server = Server("tiktok-mcp")
    
    # Register tools
    register_tools(server, tiktok_client)
    
    # Run server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def main():
    """Synchronous entry point for console script."""
    asyncio.run(_async_main())


if __name__ == "__main__":
    main()