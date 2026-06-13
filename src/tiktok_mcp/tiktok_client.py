"""
TikTok Client - Supports both Official API and Public Scraping
"""
import asyncio
import json
import os
import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup


class TikTokClient:
    """Client for TikTok - supports official API and public scraping."""
    
    def __init__(
        self,
        client_key: Optional[str] = None,
        client_secret: Optional[str] = None,
        access_token: Optional[str] = None,
    ):
        self.client_key = client_key
        self.client_secret = client_secret
        self.access_token = access_token
        self.use_official_api = bool(client_key and client_secret and access_token)
        
        # Base URLs
        self.official_base = "https://open.tiktokapis.com/v2"
        self.web_base = "https://www.tiktok.com"
        
        # HTTP client
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    # ==================== OFFICIAL API METHODS ====================
    
    async def _official_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make a request to the official TikTok API."""
        if not self.use_official_api:
            return {"success": False, "error": "Official API credentials not configured"}
        
        url = f"{self.official_base}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        
        try:
            response = await self.client.request(method, url, params=params, json=json_data, headers=headers)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except httpx.HTTPError as e:
            return {"success": False, "error": f"API request failed: {str(e)}"}
    
    async def official_search_videos(
        self,
        query: str,
        max_count: int = 20,
        cursor: int = 0,
    ) -> Dict[str, Any]:
        """Search videos using official API."""
        return await self._official_request(
            "POST",
            "/video/search/",
            json_data={
                "query": query,
                "max_count": max_count,
                "cursor": cursor,
            }
        )
    
    async def official_get_user_info(self, username: str) -> Dict[str, Any]:
        """Get user info using official API."""
        return await self._official_request(
            "GET",
            f"/user/info/",
            params={"username": username}
        )
    
    async def official_get_video_info(self, video_id: str) -> Dict[str, Any]:
        """Get video info using official API."""
        return await self._official_request(
            "GET",
            f"/video/info/",
            params={"video_id": video_id}
        )
    
    # ==================== PUBLIC SCRAPING METHODS ====================
    
    async def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch a page and return HTML content."""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError:
            return None
    
    def _extract_json_from_script(self, html: str, script_id: str) -> Optional[Dict]:
        """Extract JSON data from a script tag."""
        soup = BeautifulSoup(html, "lxml")
        script = soup.find("script", id=script_id)
        if script and script.string:
            try:
                return json.loads(script.string)
            except json.JSONDecodeError:
                pass
        return None
    
    async def search_videos(
        self,
        query: str,
        max_results: int = 20,
    ) -> Dict[str, Any]:
        """Search for TikTok videos (public scraping fallback)."""
        if self.use_official_api:
            return await self.official_search_videos(query, max_results)
        
        # Public scraping approach
        encoded_query = quote_plus(query)
        url = f"{self.web_base}/search/video?q={encoded_query}"
        
        html = await self._fetch_page(url)
        if not html:
            return {"success": False, "error": "Failed to fetch search page"}
        
        # Try to extract from __NEXT_DATA__ or similar
        data = self._extract_json_from_script(html, "__NEXT_DATA__")
        if not data:
            data = self._extract_json_from_script(html, "SIGI_STATE")
        
        if data:
            return {"success": True, "data": data, "source": "scraping"}
        
        # Fallback: parse HTML for video items
        videos = self._parse_search_html(html, max_results)
        return {"success": True, "data": {"videos": videos}, "source": "scraping"}
    
    def _parse_search_html(self, html: str, max_results: int) -> List[Dict]:
        """Parse search results from HTML."""
        soup = BeautifulSoup(html, "lxml")
        videos = []
        
        # TikTok search page structure varies, try multiple selectors
        items = soup.select('[data-e2e="search-video-item"]') or \
                soup.select('div[data-e2e="video-item"]') or \
                soup.select('a[href*="/video/"]')
        
        for item in items[:max_results]:
            try:
                link = item.find("a", href=True)
                if not link:
                    continue
                
                href = link["href"]
                video_id_match = re.search(r"/video/(\d+)", href)
                video_id = video_id_match.group(1) if video_id_match else None
                
                # Extract thumbnail
                img = item.find("img")
                thumbnail = img.get("src") if img else None
                
                # Extract description/caption
                caption_elem = item.find("span", {"data-e2e": "video-desc"}) or \
                              item.find("div", {"data-e2e": "video-desc"})
                caption = caption_elem.get_text(strip=True) if caption_elem else ""
                
                videos.append({
                    "video_id": video_id,
                    "url": f"https://www.tiktok.com{href}" if href.startswith("/") else href,
                    "thumbnail": thumbnail,
                    "caption": caption,
                })
            except Exception:
                continue
        
        return videos
    
    async def get_trending_hashtags(self, region: str = "US") -> Dict[str, Any]:
        """Get trending hashtags."""
        if self.use_official_api:
            # Official API endpoint would go here
            pass
        
        # Scrape discover page
        url = f"{self.web_base}/discover"
        html = await self._fetch_page(url)
        if not html:
            return {"success": False, "error": "Failed to fetch discover page"}
        
        data = self._extract_json_from_script(html, "__NEXT_DATA__")
        if data:
            return {"success": True, "data": data, "source": "scraping"}
        
        # Parse trending hashtags from HTML
        hashtags = self._parse_trending_hashtags(html)
        return {"success": True, "data": {"hashtags": hashtags}, "source": "scraping"}
    
    def _parse_trending_hashtags(self, html: str) -> List[Dict]:
        """Parse trending hashtags from discover page."""
        soup = BeautifulSoup(html, "lxml")
        hashtags = []
        
        # Try to find hashtag elements
        items = soup.select('[data-e2e="challenge-item"]') or \
                soup.select('a[href*="/tag/"]')
        
        for item in items[:30]:
            try:
                link = item.find("a", href=True)
                if not link:
                    continue
                
                href = link["href"]
                tag_match = re.search(r"/tag/([^/?]+)", href)
                tag_name = tag_match.group(1) if tag_match else None
                
                # Get view count if available
                views_elem = item.find("strong") or item.find("span", class_=re.compile(r"view|count"))
                views = views_elem.get_text(strip=True) if views_elem else "N/A"
                
                hashtags.append({
                    "name": tag_name,
                    "url": f"https://www.tiktok.com{href}" if href.startswith("/") else href,
                    "views": views,
                })
            except Exception:
                continue
        
        return hashtags
    
    async def get_trending_videos(self, region: str = "US", max_results: int = 20) -> Dict[str, Any]:
        """Get trending videos."""
        if self.use_official_api:
            # Official API endpoint would go here
            pass
        
        # Scrape trending page
        url = f"{self.web_base}/trending"
        html = await self._fetch_page(url)
        if not html:
            return {"success": False, "error": "Failed to fetch trending page"}
        
        data = self._extract_json_from_script(html, "__NEXT_DATA__")
        if data:
            return {"success": True, "data": data, "source": "scraping"}
        
        videos = self._parse_search_html(html, max_results)
        return {"success": True, "data": {"videos": videos}, "source": "scraping"}
    
    async def get_user_info(self, username: str) -> Dict[str, Any]:
        """Get user profile info."""
        # Remove @ if present
        username = username.lstrip("@")
        
        if self.use_official_api:
            return await self.official_get_user_info(username)
        
        url = f"{self.web_base}/@{username}"
        html = await self._fetch_page(url)
        if not html:
            return {"success": False, "error": "Failed to fetch user page"}
        
        data = self._extract_json_from_script(html, "__NEXT_DATA__")
        if data:
            return {"success": True, "data": data, "source": "scraping"}
        
        # Parse user info from HTML
        user_info = self._parse_user_html(html, username)
        return {"success": True, "data": user_info, "source": "scraping"}
    
    def _parse_user_html(self, html: str, username: str) -> Dict:
        """Parse user profile from HTML."""
        soup = BeautifulSoup(html, "lxml")
        
        # Try to find user stats
        stats = {}
        stat_items = soup.select('[data-e2e="following-count"], [data-e2e="followers-count"], [data-e2e="likes-count"]')
        for item in stat_items:
            label = item.get("data-e2e", "").replace("-count", "")
            value = item.find("strong") or item.find("span")
            if value:
                stats[label] = value.get_text(strip=True)
        
        # Bio
        bio_elem = soup.find("h2", {"data-e2e": "user-bio"}) or \
                   soup.select_one('[data-e2e="user-bio"]')
        bio = bio_elem.get_text(strip=True) if bio_elem else ""
        
        # Avatar
        avatar_elem = soup.find("img", {"data-e2e": "user-avatar"})
        avatar = avatar_elem.get("src") if avatar_elem else None
        
        return {
            "username": username,
            "display_name": username,  # Would need more parsing
            "bio": bio,
            "avatar": avatar,
            "stats": stats,
            "url": f"https://www.tiktok.com/@{username}",
        }
    
    async def get_user_videos(self, username: str, max_results: int = 20) -> Dict[str, Any]:
        """Get videos from a user's profile."""
        username = username.lstrip("@")
        url = f"{self.web_base}/@{username}"
        html = await self._fetch_page(url)
        if not html:
            return {"success": False, "error": "Failed to fetch user page"}
        
        data = self._extract_json_from_script(html, "__NEXT_DATA__")
        if data:
            return {"success": True, "data": data, "source": "scraping"}
        
        videos = self._parse_search_html(html, max_results)
        return {"success": True, "data": {"videos": videos}, "source": "scraping"}
    
    async def get_video_details(self, video_id: str) -> Dict[str, Any]:
        """Get detailed video info."""
        if self.use_official_api:
            return await self.official_get_video_info(video_id)
        
        url = f"{self.web_base}/@placeholder/video/{video_id}"
        html = await self._fetch_page(url)
        if not html:
            return {"success": False, "error": "Failed to fetch video page"}
        
        data = self._extract_json_from_script(html, "__NEXT_DATA__")
        if data:
            return {"success": True, "data": data, "source": "scraping"}
        
        # Parse video page
        video_info = self._parse_video_html(html, video_id)
        return {"success": True, "data": video_info, "source": "scraping"}
    
    def _parse_video_html(self, html: str, video_id: str) -> Dict:
        """Parse video details from HTML."""
        soup = BeautifulSoup(html, "lxml")
        
        # Extract metadata
        title_elem = soup.find("meta", property="og:title")
        title = title_elem.get("content", "") if title_elem else ""
        
        desc_elem = soup.find("meta", property="og:description")
        description = desc_elem.get("content", "") if desc_elem else ""
        
        thumbnail_elem = soup.find("meta", property="og:image")
        thumbnail = thumbnail_elem.get("content", "") if thumbnail_elem else ""
        
        # Stats
        stats = {}
        for stat_type in ["digg", "comment", "share"]:
            elem = soup.find("strong", {"data-e2e": f"{stat_type}-count"})
            if elem:
                stats[stat_type] = elem.get_text(strip=True)
        
        return {
            "video_id": video_id,
            "title": title,
            "description": description,
            "thumbnail": thumbnail,
            "stats": stats,
            "url": f"https://www.tiktok.com/@placeholder/video/{video_id}",
        }
    
    async def search_hashtag(self, hashtag: str, max_results: int = 20) -> Dict[str, Any]:
        """Search videos by hashtag."""
        hashtag = hashtag.lstrip("#")
        url = f"{self.web_base}/tag/{hashtag}"
        html = await self._fetch_page(url)
        if not html:
            return {"success": False, "error": "Failed to fetch hashtag page"}
        
        data = self._extract_json_from_script(html, "__NEXT_DATA__")
        if data:
            return {"success": True, "data": data, "source": "scraping"}
        
        videos = self._parse_search_html(html, max_results)
        return {"success": True, "data": {"videos": videos, "hashtag": hashtag}, "source": "scraping"}
    
    async def search_user(self, query: str, max_results: int = 20) -> Dict[str, Any]:
        """Search for users."""
        encoded_query = quote_plus(query)
        url = f"{self.web_base}/search/user?q={encoded_query}"
        html = await self._fetch_page(url)
        if not html:
            return {"success": False, "error": "Failed to fetch user search page"}
        
        data = self._extract_json_from_script(html, "__NEXT_DATA__")
        if data:
            return {"success": True, "data": data, "source": "scraping"}
        
        # Parse users from HTML
        users = self._parse_user_search_html(html, max_results)
        return {"success": True, "data": {"users": users}, "source": "scraping"}
    
    def _parse_user_search_html(self, html: str, max_results: int) -> List[Dict]:
        """Parse user search results."""
        soup = BeautifulSoup(html, "lxml")
        users = []
        
        items = soup.select('[data-e2e="search-user-item"]') or \
                soup.select('a[href*="/@"]')
        
        for item in items[:max_results]:
            try:
                link = item.find("a", href=True)
                if not link:
                    continue
                
                href = link["href"]
                username_match = re.search(r"/@([^/?]+)", href)
                username = username_match.group(1) if username_match else None
                
                # Display name
                name_elem = item.find("span", {"data-e2e": "user-title"}) or \
                           item.find("h3")
                display_name = name_elem.get_text(strip=True) if name_elem else username
                
                # Avatar
                img = item.find("img")
                avatar = img.get("src") if img else None
                
                # Verified badge
                verified = bool(item.find("svg", {"data-e2e": "verified-icon"}))
                
                users.append({
                    "username": username,
                    "display_name": display_name,
                    "avatar": avatar,
                    "verified": verified,
                    "url": f"https://www.tiktok.com{href}" if href.startswith("/") else href,
                })
            except Exception:
                continue
        
        return users


# Synchronous wrapper for MCP compatibility
class SyncTikTokClient:
    """Synchronous wrapper for TikTokClient."""
    
    def __init__(self, client_key: Optional[str] = None, client_secret: Optional[str] = None, access_token: Optional[str] = None):
        self._async_client = TikTokClient(client_key, client_secret, access_token)
        self._loop = None
    
    def _get_loop(self):
        """Get or create event loop."""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
    
    def _run_async(self, coro):
        """Run async coroutine synchronously."""
        loop = self._get_loop()
        return loop.run_until_complete(coro)
    
    # Delegate all methods
    def search_videos(self, query: str, max_results: int = 20) -> Dict[str, Any]:
        return self._run_async(self._async_client.search_videos(query, max_results))
    
    def get_trending_hashtags(self, region: str = "US") -> Dict[str, Any]:
        return self._run_async(self._async_client.get_trending_hashtags(region))
    
    def get_trending_videos(self, region: str = "US", max_results: int = 20) -> Dict[str, Any]:
        return self._run_async(self._async_client.get_trending_videos(region, max_results))
    
    def get_user_info(self, username: str) -> Dict[str, Any]:
        return self._run_async(self._async_client.get_user_info(username))
    
    def get_user_videos(self, username: str, max_results: int = 20) -> Dict[str, Any]:
        return self._run_async(self._async_client.get_user_videos(username, max_results))
    
    def get_video_details(self, video_id: str) -> Dict[str, Any]:
        return self._run_async(self._async_client.get_video_details(video_id))
    
    def search_hashtag(self, hashtag: str, max_results: int = 20) -> Dict[str, Any]:
        return self._run_async(self._async_client.search_hashtag(hashtag, max_results))
    
    def search_user(self, query: str, max_results: int = 20) -> Dict[str, Any]:
        return self._run_async(self._async_client.search_user(query, max_results))
    
    def close(self):
        """Close the client."""
        if self._async_client:
            self._run_async(self._async_client.close())