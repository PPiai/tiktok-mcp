"""
TikTok MCP Tools Registration
"""
import json
from typing import Any, Dict, List

from mcp.server import Server
from mcp.types import Tool, TextContent, CallToolResult

from .tiktok_client import SyncTikTokClient


def register_tools(server: Server, tiktok_client: SyncTikTokClient):
    """Register all TikTok MCP tools."""
    
    @server.list_tools()
    async def list_tools() -> List[Tool]:
        return [
            Tool(
                name="search_videos",
                description="Search for TikTok videos by keyword",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "max_results": {"type": "integer", "default": 20, "description": "Maximum number of results"},
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="get_trending_hashtags",
                description="Get trending hashtags on TikTok",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "region": {"type": "string", "default": "US", "description": "Region code (e.g., US, BR, GB)"},
                    },
                    "required": ["region"],
                },
            ),
            Tool(
                name="get_trending_videos",
                description="Get trending/popular videos on TikTok",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "region": {"type": "string", "default": "US", "description": "Region code"},
                        "max_results": {"type": "integer", "default": 20, "description": "Maximum number of results"},
                    },
                    "required": ["region"],
                },
            ),
            Tool(
                name="get_user_info",
                description="Get TikTok user profile information",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "description": "TikTok username (with or without @)"},
                    },
                    "required": ["username"],
                },
            ),
            Tool(
                name="get_user_videos",
                description="Get videos from a TikTok user's profile",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "description": "TikTok username (with or without @)"},
                        "max_results": {"type": "integer", "default": 20, "description": "Maximum number of results"},
                    },
                    "required": ["username"],
                },
            ),
            Tool(
                name="get_video_details",
                description="Get detailed information about a specific TikTok video",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "video_id": {"type": "string", "description": "TikTok video ID"},
                    },
                    "required": ["video_id"],
                },
            ),
            Tool(
                name="search_hashtag",
                description="Search videos by hashtag",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "hashtag": {"type": "string", "description": "Hashtag (with or without #)"},
                        "max_results": {"type": "integer", "default": 20, "description": "Maximum number of results"},
                    },
                    "required": ["hashtag"],
                },
            ),
            Tool(
                name="search_users",
                description="Search for TikTok users",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "max_results": {"type": "integer", "default": 20, "description": "Maximum number of results"},
                    },
                    "required": ["query"],
                },
            ),
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
        try:
            if name == "search_videos":
                result = tiktok_client.search_videos(
                    query=arguments["query"],
                    max_results=arguments.get("max_results", 20),
                )
            
            elif name == "get_trending_hashtags":
                result = tiktok_client.get_trending_hashtags(
                    region=arguments.get("region", "US"),
                )
            
            elif name == "get_trending_videos":
                result = tiktok_client.get_trending_videos(
                    region=arguments.get("region", "US"),
                    max_results=arguments.get("max_results", 20),
                )
            
            elif name == "get_user_info":
                result = tiktok_client.get_user_info(arguments["username"])
            
            elif name == "get_user_videos":
                result = tiktok_client.get_user_videos(
                    username=arguments["username"],
                    max_results=arguments.get("max_results", 20),
                )
            
            elif name == "get_video_details":
                result = tiktok_client.get_video_details(arguments["video_id"])
            
            elif name == "search_hashtag":
                result = tiktok_client.search_hashtag(
                    hashtag=arguments["hashtag"],
                    max_results=arguments.get("max_results", 20),
                )
            
            elif name == "search_users":
                result = tiktok_client.search_user(
                    query=arguments["query"],
                    max_results=arguments.get("max_results", 20),
                )
            
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Unknown tool: {name}")],
                    isError=True,
                )
            
            if result["success"]:
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(result["data"], ensure_ascii=False, indent=2))],
                )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {result['error']}")],
                    isError=True,
                )
        
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error executing tool {name}: {str(e)}")],
                isError=True,
            )