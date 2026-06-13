"""
TikTok MCP Tools - registro de ferramentas via FastMCP.

Cada ferramenta chama o cliente assincrono diretamente com `await`
(sem wrapper sincrono), evitando conflitos de event loop.
"""
import json
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP

from .tiktok_client import TikTokClient


def _format(result: Dict[str, Any]) -> str:
    """Converte o resultado do cliente em texto JSON ou levanta erro."""
    if result.get("success"):
        data = result.get("data", {})
        source = result.get("source")
        if source:
            data = {"source": source, **data} if isinstance(data, dict) else {"source": source, "data": data}
        return json.dumps(data, ensure_ascii=False, indent=2)
    # FastMCP captura a excecao e a retorna como erro de tool (isError=True)
    raise RuntimeError(result.get("error", "Erro desconhecido"))


def register_tools(mcp: FastMCP, client: TikTokClient) -> None:
    """Registra todas as ferramentas TikTok no servidor FastMCP."""

    @mcp.tool()
    async def search_videos(query: str, max_results: int = 20) -> str:
        """Busca videos do TikTok por palavra-chave."""
        return _format(await client.search_videos(query, max_results))

    @mcp.tool()
    async def get_trending_hashtags(region: str = "US") -> str:
        """Retorna hashtags em alta no TikTok por regiao (ex.: US, BR, GB)."""
        return _format(await client.get_trending_hashtags(region))

    @mcp.tool()
    async def get_trending_videos(region: str = "US", max_results: int = 20) -> str:
        """Retorna videos em alta/populares no TikTok por regiao."""
        return _format(await client.get_trending_videos(region, max_results))

    @mcp.tool()
    async def get_user_info(username: str) -> str:
        """Retorna informacoes de perfil de um usuario do TikTok (com ou sem @)."""
        return _format(await client.get_user_info(username))

    @mcp.tool()
    async def get_user_videos(username: str, max_results: int = 20) -> str:
        """Retorna videos do perfil de um usuario do TikTok."""
        return _format(await client.get_user_videos(username, max_results))

    @mcp.tool()
    async def get_video_details(video_id: str) -> str:
        """Retorna detalhes de um video especifico do TikTok pelo ID."""
        return _format(await client.get_video_details(video_id))

    @mcp.tool()
    async def search_hashtag(hashtag: str, max_results: int = 20) -> str:
        """Retorna videos de uma hashtag especifica (com ou sem #)."""
        return _format(await client.search_hashtag(hashtag, max_results))

    @mcp.tool()
    async def search_users(query: str, max_results: int = 20) -> str:
        """Busca usuarios do TikTok."""
        return _format(await client.search_user(query, max_results))
