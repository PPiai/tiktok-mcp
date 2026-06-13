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

## Installation

```bash
cd /opt/data/mcp-servers/tiktok-mcp
pip install -e .
```

Or with uv:
```bash
uv pip install -e /opt/data/mcp-servers/tiktok-mcp
```

## Configuration

### Official API (Recommended)

Get credentials from [TikTok Developers](https://developers.tiktok.com/):

```bash
export TIKTOK_CLIENT_KEY="your_client_key"
export TIKTOK_CLIENT_SECRET="your_client_secret"
export TIKTOK_ACCESS_TOKEN="your_access_token"
```

### Public Scraping (No credentials needed)

Just don't set the environment variables - the server will automatically use public scraping.

## Usage with Hermes Agent

Add to your `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  tiktok:
    command: "uvx"
    args: ["tiktok-mcp"]
    env:
      TIKTOK_CLIENT_KEY: "your_client_key"
      TIKTOK_CLIENT_SECRET: "your_client_secret"
      TIKTOK_ACCESS_TOKEN: "your_access_token"
    timeout: 120
    connect_timeout: 60
```

For public scraping mode (no credentials):

```yaml
mcp_servers:
  tiktok:
    command: "uvx"
    args: ["tiktok-mcp"]
    timeout: 120
    connect_timeout: 60
```

Then restart Hermes Agent. The tools will be available as `mcp_tiktok_*`.

## Available Tools

| Tool | Description |
|------|-------------|
| `search_videos` | Search videos by keyword |
| `get_trending_hashtags` | Get trending hashtags by region |
| `get_trending_videos` | Get trending videos |
| `get_user_info` | Get user profile details |
| `get_user_videos` | Get user's videos |
| `get_video_details` | Get video details by ID |
| `search_hashtag` | Get videos for a hashtag |
| `search_users` | Search for users |

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
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Important Notes

- **Rate Limits**: Public scraping is subject to TikTok's rate limits. Use official API for production.
- **Legal**: Respect TikTok's Terms of Service and robots.txt
- **Stability**: Public scraping may break if TikTok changes their frontend structure
- **Official API**: Requires TikTok developer approval - apply at developers.tiktok.com

## License

MIT