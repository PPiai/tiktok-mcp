"""
TikTok MCP Server - Main entry point.

Por padrao roda sobre streamable-HTTP, de modo que pode ser hospedado como
servico de rede (Easypanel/Docker). Para uso local via stdio, defina a
variavel de ambiente MCP_TRANSPORT=stdio.
"""
import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from .tiktok_client import TikTokClient
from .tools import register_tools

# Carrega .env em desenvolvimento local (em producao usa env vars do container)
load_dotenv()


def build_server() -> FastMCP:
    """Cria e configura a instancia do servidor MCP."""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    mcp = FastMCP(
        "tiktok-mcp",
        host=host,
        port=port,
        # Stateless: cada request e independente, ideal para deploy atras de
        # proxy/load balancer (Easypanel) sem sessoes persistentes.
        stateless_http=True,
    )

    client = TikTokClient(
        client_key=os.getenv("TIKTOK_CLIENT_KEY"),
        client_secret=os.getenv("TIKTOK_CLIENT_SECRET"),
        access_token=os.getenv("TIKTOK_ACCESS_TOKEN"),
    )

    register_tools(mcp, client)
    return mcp


def main():
    """Entry point do console script."""
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")
    mcp = build_server()
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
