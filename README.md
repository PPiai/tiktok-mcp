# TikTok MCP Server

Model Context Protocol (MCP) server for TikTok. Provides tools for searching videos, users, hashtags, getting trending content, user profiles, video details, and more.

## Features

- **Video Search** - Search TikTok videos by keyword
- **Trending Hashtags** - Get currently trending hashtags by region
- **Trending Videos** - Get popular/trending videos
- **User Info** - Get user profile details (followers, following, likes, bio, etc.)
- **User Videos** - Get videos from a specific user's profile
- **Video Details** - Get detailed video information (stats, description, etc.)
- **Hashtag Search** - Get videos for a specific hashtag
- **User Search** - Search for TikTok users

## API Access

This server supports two modes:

1. **Official TikTok API** (recommended) - Requires approved developer access with:
   - `TIKTOK_CLIENT_KEY`
   - `TIKTOK_CLIENT_SECRET`
   - `TIKTOK_ACCESS_TOKEN`

2. **Public Scraping** (fallback) - Works without API credentials but may be rate-limited or break if TikTok changes their frontend.

## Transport

The server runs over **streamable-HTTP** by default, exposing the MCP endpoint at
`/mcp` so it can be hosted as a network service (Easypanel/Docker). Set
`MCP_TRANSPORT=stdio` to run over stdio for local subprocess use instead.

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_TRANSPORT` | `streamable-http` | `streamable-http` (hosted) or `stdio` (local) |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8000` | Listen port |
| `TIKTOK_CLIENT_KEY` | — | Official API key (optional) |
| `TIKTOK_CLIENT_SECRET` | — | Official API secret (optional) |
| `TIKTOK_ACCESS_TOKEN` | — | Official API token (optional) |

### Official API (Recommended)

Get credentials from [TikTok Developers](https://developers.tiktok.com/) and set the
three `TIKTOK_*` variables. If they are not set, the server falls back to public scraping.

## Local Development

```bash
# Install (editable) with uv
uv pip install -e .

# Run (streamable-HTTP on http://0.0.0.0:8000/mcp)
tiktok-mcp

# Or over stdio
MCP_TRANSPORT=stdio tiktok-mcp
```

## Docker

```bash
docker build -t tiktok-mcp .
docker run -p 8000:8000 \
  -e TIKTOK_CLIENT_KEY=... \
  -e TIKTOK_CLIENT_SECRET=... \
  -e TIKTOK_ACCESS_TOKEN=... \
  tiktok-mcp
```

The MCP endpoint will be available at `http://localhost:8000/mcp`.

## Deploy on Easypanel

1. Create an **App** service pointing to this repository (or the GHCR image built by
   the included CI workflow).
2. Build method: **Dockerfile** (already in the repo root).
3. Set the exposed/container port to **8000** and add a domain (Easypanel handles SSL).
4. Add the `TIKTOK_*` environment variables under the service's **Environment** tab
   (leave them empty to use public scraping).
5. Deploy. The MCP endpoint will be served at `https://<your-domain>/mcp`.

### Connecting an MCP client

For a hosted HTTP server, connect via URL (not a spawned command). The exact config
file depends on the client; the shape is the same:

```json
{
  "mcpServers": {
    "tiktok": {
      "url": "https://<your-domain>/mcp"
    }
  }
}
```

- **Claude Desktop / Claude Code**: add the block above to the MCP config and restart.
- **Hermes Agent**: point the `tiktok` server at the same `url`.

Once connected, the tools appear to the model (e.g. `mcp_tiktok_search_videos`) and can
be triggered with natural language — see [Example Queries](#example-queries).

## Verify the endpoint

After running locally or deploying, confirm the server is up with a raw MCP handshake.
The streamable-HTTP endpoint requires both `application/json` and `text/event-stream`
in the `Accept` header:

```bash
curl -i -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"curl","version":"1.0"}}}'
```

A healthy server returns `HTTP/1.1 200 OK` and an SSE `data:` line containing
`"serverInfo":{"name":"tiktok-mcp",...}`.

## Available Tools

All tools return a JSON text payload. When scraping is used (no official API
credentials), responses include a `"source": "scraping"` field.

| Tool | Parameters | Description |
|------|-----------|-------------|
| `search_videos` | `query` (str, required), `max_results` (int, default 20) | Search videos by keyword |
| `get_trending_hashtags` | `region` (str, default `US`) | Get trending hashtags by region |
| `get_trending_videos` | `region` (str, default `US`), `max_results` (int, default 20) | Get trending videos |
| `get_user_info` | `username` (str, required — with or without `@`) | Get user profile details |
| `get_user_videos` | `username` (str, required), `max_results` (int, default 20) | Get a user's videos |
| `get_video_details` | `video_id` (str, required) | Get video details by ID |
| `search_hashtag` | `hashtag` (str, required — with or without `#`), `max_results` (int, default 20) | Get videos for a hashtag |
| `search_users` | `query` (str, required), `max_results` (int, default 20) | Search for users |

## Example Queries

- "Search for videos about AI automation"
- "Get trending hashtags in Brazil"
- "Find trending videos in the US"
- "Get profile info for @username"
- "Get videos from @username's profile"
- "Search for #marketing hashtag videos"
- "Find users about 'dark fantasy art'"

## Development

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"
```

> Note: an automated test suite is not included yet. Use the
> [Verify the endpoint](#verify-the-endpoint) handshake to smoke-test changes.

## Important Notes

- **Rate Limits**: Public scraping is subject to TikTok's rate limits. Use official API for production.
- **Legal**: Respect TikTok's Terms of Service and robots.txt
- **Stability**: Public scraping may break if TikTok changes their frontend structure
- **Official API**: Requires TikTok developer approval - apply at developers.tiktok.com

## License

MIT