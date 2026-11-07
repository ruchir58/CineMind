"""TMDB API Service with caching, retries, and rate-limit handling."""
import time
import logging
from typing import Dict, Any, Optional, List
import httpx
from backend.config.settings import settings

logger = logging.getLogger(__name__)

class TMDBService:
    def __init__(self):
        self.base_url = settings.TMDB_BASE_URL
        self.api_key = settings.TMDB_API_KEY
        self.access_token = settings.TMDB_ACCESS_TOKEN
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 3600  # 1 hour cache TTL

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key or self.access_token)

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": "CineMind-App/1.0"
        }
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def _get_params(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        p = params.copy() if params else {}
        if not self.access_token and self.api_key:
            p["api_key"] = self.api_key
        return p

    def _get_from_cache(self, key: str) -> Optional[Any]:
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["timestamp"] < self.cache_ttl:
                return entry["data"]
            del self._cache[key]
        return None

    def _set_cache(self, key: str, data: Any):
        self._cache[key] = {
            "timestamp": time.time(),
            "data": data
        }

    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None, retries: int = 3) -> Optional[Dict[str, Any]]:
        if not self.is_configured:
            logger.warning("TMDB API credentials are not configured. Falling back to local data.")
            return None

        url = f"{self.base_url}{endpoint}"
        req_params = self._get_params(params)
        headers = self._get_headers()

        cache_key = f"{endpoint}:{sorted(req_params.items())}"
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        backoff = 1.0
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url, params=req_params, headers=headers)

                    if response.status_code == 200:
                        data = response.json()
                        self._set_cache(cache_key, data)
                        return data
                    elif response.status_code == 429:
                        # Rate limited
                        retry_after = int(response.headers.get("Retry-After", backoff))
                        logger.warning(f"TMDB Rate Limit reached. Retrying after {retry_after}s...")
                        await httpx.AsyncClient().sleep(retry_after)
                        backoff *= 2
                    elif response.status_code == 404:
                        logger.info(f"TMDB resource not found: {endpoint}")
                        return None
                    else:
                        logger.error(f"TMDB API error {response.status_code}: {response.text}")
                        if attempt == retries - 1:
                            return None
            except Exception as e:
                logger.error(f"Error connecting to TMDB API on attempt {attempt+1}: {e}")
                if attempt == retries - 1:
                    return None
            time.sleep(backoff)
            backoff *= 2

        return None

    async def search_multi(self, query: str, page: int = 1) -> Optional[Dict[str, Any]]:
        return await self._make_request("/search/multi", {"query": query, "page": page, "include_adult": False})

    async def search_movies(self, query: str, page: int = 1) -> Optional[Dict[str, Any]]:
        return await self._make_request("/search/movie", {"query": query, "page": page, "include_adult": False})

    async def search_tv(self, query: str, page: int = 1) -> Optional[Dict[str, Any]]:
        return await self._make_request("/search/tv", {"query": query, "page": page, "include_adult": False})

    async def get_movie_details(self, movie_id: int) -> Optional[Dict[str, Any]]:
        return await self._make_request(f"/movie/{movie_id}", {"append_to_response": "credits,keywords,similar,videos"})

    async def get_tv_details(self, tv_id: int) -> Optional[Dict[str, Any]]:
        return await self._make_request(f"/tv/{tv_id}", {"append_to_response": "credits,keywords,similar,videos"})

    async def get_movie_videos(self, movie_id: int) -> Optional[Dict[str, Any]]:
        return await self._make_request(f"/movie/{movie_id}/videos")

    async def get_tv_videos(self, tv_id: int) -> Optional[Dict[str, Any]]:
        return await self._make_request(f"/tv/{tv_id}/videos")

    async def get_trending(self, media_type: str = "all", time_window: str = "week") -> Optional[Dict[str, Any]]:
        return await self._make_request(f"/trending/{media_type}/{time_window}")

    async def get_popular_movies(self, page: int = 1) -> Optional[Dict[str, Any]]:
        return await self._make_request("/movie/popular", {"page": page})

    async def get_popular_tv(self, page: int = 1) -> Optional[Dict[str, Any]]:
        return await self._make_request("/tv/popular", {"page": page})

    async def get_top_rated_movies(self, page: int = 1) -> Optional[Dict[str, Any]]:
        return await self._make_request("/movie/top_rated", {"page": page})

    async def get_top_rated_tv(self, page: int = 1) -> Optional[Dict[str, Any]]:
        return await self._make_request("/tv/top_rated", {"page": page})

    async def get_movie_genres(self) -> Optional[Dict[str, Any]]:
        return await self._make_request("/genre/movie/list")

    async def get_tv_genres(self) -> Optional[Dict[str, Any]]:
        return await self._make_request("/genre/tv/list")

    async def get_similar_movies(self, movie_id: int) -> Optional[Dict[str, Any]]:
        return await self._make_request(f"/movie/{movie_id}/similar")

    async def get_similar_tv(self, tv_id: int) -> Optional[Dict[str, Any]]:
        return await self._make_request(f"/tv/{tv_id}/similar")

tmdb_service = TMDBService()

