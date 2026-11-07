"""Movie and TV Show Data Service."""
import logging
from typing import List, Optional, Dict, Any
import pandas as pd
from backend.config.settings import settings
from backend.services.tmdb_service import tmdb_service
from backend.models.schemas import MediaItem, GenreItem

logger = logging.getLogger(__name__)

class MovieService:
    def __init__(self):
        self.movies_df: Optional[pd.DataFrame] = None
        self.tv_df: Optional[pd.DataFrame] = None
        self.load_local_data()

    def load_local_data(self):
        try:
            if settings.MOVIES_CLEANED_PATH.exists():
                self.movies_df = pd.read_csv(settings.MOVIES_CLEANED_PATH)
                logger.info(f"Loaded {len(self.movies_df)} local movies.")
            if settings.TV_CLEANED_PATH.exists():
                self.tv_df = pd.read_csv(settings.TV_CLEANED_PATH)
                logger.info(f"Loaded {len(self.tv_df)} local TV shows.")
        except Exception as e:
            logger.error(f"Error loading local cleaned datasets: {e}")

    def _row_to_media_item(self, row: pd.Series, media_type: str = "movie") -> MediaItem:
        return MediaItem(
            id=int(row["id"]),
            title=str(row["title"]),
            original_title=str(row.get("original_title", "")),
            media_type=media_type,
            overview=str(row.get("overview", "")),
            genres=[g.strip() for g in str(row.get("genres", "")).split(",") if g.strip()],
            release_date=str(row.get("release_date", "")) if pd.notna(row.get("release_date")) else None,
            first_air_date=str(row.get("first_air_date", "")) if pd.notna(row.get("first_air_date")) else None,
            original_language=str(row.get("original_language", "en")),
            vote_average=float(row.get("vote_average", 0.0)),
            vote_count=int(row.get("vote_count", 0)),
            popularity=float(row.get("popularity", 0.0)),
            poster_path=str(row.get("poster_path", "")) if pd.notna(row.get("poster_path")) else None,
            backdrop_path=str(row.get("backdrop_path", "")) if pd.notna(row.get("backdrop_path")) else None,
            cast=[c.strip() for c in str(row.get("cast", "")).split(",") if c.strip()],
            director=str(row.get("director", "")) if media_type == "movie" else None,
            creators=[c.strip() for c in str(row.get("creators", "")).split(",") if c.strip()] if media_type == "tv" else [],
            keywords=[k.strip() for k in str(row.get("keywords", "")).split(",") if k.strip()],
            runtime=int(row.get("runtime", 0)) if media_type == "movie" and pd.notna(row.get("runtime")) else None,
            number_of_seasons=int(row.get("number_of_seasons", 1)) if media_type == "tv" and pd.notna(row.get("number_of_seasons")) else None,
            number_of_episodes=int(row.get("number_of_episodes", 1)) if media_type == "tv" and pd.notna(row.get("number_of_episodes")) else None,
            status=str(row.get("status", "")) if media_type == "tv" else None,
            origin_country=[c.strip() for c in str(row.get("origin_country", "")).split(",") if c.strip()]
        )

    def get_movies(self, page: int = 1, page_size: int = 20, genre: Optional[str] = None, sort_by: str = "popularity") -> List[MediaItem]:
        if self.movies_df is None or self.movies_df.empty:
            return []
        df = self.movies_df.copy()
        if genre:
            df = df[df["genres"].str.lower().str.contains(genre.lower(), na=False)]

        if sort_by == "rating":
            df = df.sort_values(by="vote_average", ascending=False)
        elif sort_by == "recent":
            df = df.sort_values(by="release_year", ascending=False)
        else:
            df = df.sort_values(by="popularity", ascending=False)

        start = (page - 1) * page_size
        end = start + page_size
        slice_df = df.iloc[start:end]

        return [self._row_to_media_item(row, "movie") for _, row in slice_df.iterrows()]

    def get_tv_shows(self, page: int = 1, page_size: int = 20, genre: Optional[str] = None, sort_by: str = "popularity") -> List[MediaItem]:
        if self.tv_df is None or self.tv_df.empty:
            return []
        df = self.tv_df.copy()
        if genre:
            df = df[df["genres"].str.lower().str.contains(genre.lower(), na=False)]

        if sort_by == "rating":
            df = df.sort_values(by="vote_average", ascending=False)
        elif sort_by == "recent":
            df = df.sort_values(by="release_year", ascending=False)
        else:
            df = df.sort_values(by="popularity", ascending=False)

        start = (page - 1) * page_size
        end = start + page_size
        slice_df = df.iloc[start:end]

        return [self._row_to_media_item(row, "tv") for _, row in slice_df.iterrows()]

    async def get_movie_by_id(self, movie_id: int) -> Optional[MediaItem]:
        # Check local dataset first
        if self.movies_df is not None:
            match = self.movies_df[self.movies_df["id"] == movie_id]
            if not match.empty:
                return self._row_to_media_item(match.iloc[0], "movie")

        # Fallback to TMDB API
        tmdb_data = await tmdb_service.get_movie_details(movie_id)
        if tmdb_data:
            genres = [g["name"] for g in tmdb_data.get("genres", [])]
            credits = tmdb_data.get("credits", {})
            cast = [c["name"] for c in credits.get("cast", [])[:8]]
            directors = [c["name"] for c in credits.get("crew", []) if c.get("job") == "Director"]
            keywords = [k["name"] for k in tmdb_data.get("keywords", {}).get("keywords", [])]
            
            # Extract YouTube trailer
            trailer_key = None
            videos = tmdb_data.get("videos", {}).get("results", [])
            for v in videos:
                if v.get("site") == "YouTube" and v.get("type") in ["Trailer", "Teaser"]:
                    trailer_key = v.get("key")
                    break

            return MediaItem(
                id=tmdb_data.get("id"),
                title=tmdb_data.get("title", ""),
                original_title=tmdb_data.get("original_title", ""),
                media_type="movie",
                overview=tmdb_data.get("overview", ""),
                genres=genres,
                release_date=tmdb_data.get("release_date"),
                original_language=tmdb_data.get("original_language", "en"),
                vote_average=tmdb_data.get("vote_average", 0.0),
                vote_count=tmdb_data.get("vote_count", 0),
                popularity=tmdb_data.get("popularity", 0.0),
                poster_path=tmdb_data.get("poster_path"),
                backdrop_path=tmdb_data.get("backdrop_path"),
                cast=cast,
                director=directors[0] if directors else None,
                keywords=keywords,
                runtime=tmdb_data.get("runtime"),
                trailer_key=trailer_key,
                trailer_url=f"https://www.youtube.com/watch?v={trailer_key}" if trailer_key else None
            )
        return None

    async def get_tv_by_id(self, tv_id: int) -> Optional[MediaItem]:
        # Check local dataset first
        if self.tv_df is not None:
            match = self.tv_df[self.tv_df["id"] == tv_id]
            if not match.empty:
                return self._row_to_media_item(match.iloc[0], "tv")

        # Fallback to TMDB API
        tmdb_data = await tmdb_service.get_tv_details(tv_id)
        if tmdb_data:
            genres = [g["name"] for g in tmdb_data.get("genres", [])]
            credits = tmdb_data.get("credits", {})
            cast = [c["name"] for c in credits.get("cast", [])[:8]]
            creators = [c["name"] for c in tmdb_data.get("created_by", [])]
            keywords = [k["name"] for k in tmdb_data.get("keywords", {}).get("results", [])]

            # Extract YouTube trailer
            trailer_key = None
            videos = tmdb_data.get("videos", {}).get("results", [])
            for v in videos:
                if v.get("site") == "YouTube" and v.get("type") in ["Trailer", "Teaser"]:
                    trailer_key = v.get("key")
                    break

            return MediaItem(
                id=tmdb_data.get("id"),
                title=tmdb_data.get("name", ""),
                original_title=tmdb_data.get("original_name", ""),
                media_type="tv",
                overview=tmdb_data.get("overview", ""),
                genres=genres,
                first_air_date=tmdb_data.get("first_air_date"),
                original_language=tmdb_data.get("original_language", "en"),
                vote_average=tmdb_data.get("vote_average", 0.0),
                vote_count=tmdb_data.get("vote_count", 0),
                popularity=tmdb_data.get("popularity", 0.0),
                poster_path=tmdb_data.get("poster_path"),
                backdrop_path=tmdb_data.get("backdrop_path"),
                cast=cast,
                creators=creators,
                keywords=keywords,
                number_of_seasons=tmdb_data.get("number_of_seasons"),
                number_of_episodes=tmdb_data.get("number_of_episodes"),
                status=tmdb_data.get("status"),
                trailer_key=trailer_key,
                trailer_url=f"https://www.youtube.com/watch?v={trailer_key}" if trailer_key else None
            )
        return None

    async def search(self, query: str, limit: int = 20) -> List[MediaItem]:
        q = query.strip().lower()
        if not q:
            return []

        results = []
        seen_ids = set()

        # 1. Search local catalogue
        if self.movies_df is not None:
            m_matches = self.movies_df[
                self.movies_df["title"].str.lower().str.contains(q, na=False) |
                self.movies_df["overview"].str.lower().str.contains(q, na=False) |
                self.movies_df["cast"].str.lower().str.contains(q, na=False) |
                self.movies_df["director"].str.lower().str.contains(q, na=False)
            ]
            for _, row in m_matches.iterrows():
                mid = int(row["id"])
                if mid not in seen_ids:
                    seen_ids.add(mid)
                    results.append(self._row_to_media_item(row, "movie"))

        if self.tv_df is not None:
            t_matches = self.tv_df[
                self.tv_df["title"].str.lower().str.contains(q, na=False) |
                self.tv_df["overview"].str.lower().str.contains(q, na=False) |
                self.tv_df["cast"].str.lower().str.contains(q, na=False) |
                self.tv_df["creators"].str.lower().str.contains(q, na=False)
            ]
            for _, row in t_matches.iterrows():
                tid = int(row["id"])
                if tid not in seen_ids:
                    seen_ids.add(tid)
                    results.append(self._row_to_media_item(row, "tv"))

        # 2. TMDB search fallback or enrichment
        if tmdb_service.is_configured and len(results) < limit:
            tmdb_results = await tmdb_service.search_multi(query)
            if tmdb_results and "results" in tmdb_results:
                for item in tmdb_results["results"]:
                    media_type = item.get("media_type")
                    if media_type not in ["movie", "tv"]:
                        continue
                    item_id = item.get("id")
                    if item_id in seen_ids:
                        continue
                    seen_ids.add(item_id)
                    results.append(MediaItem(
                        id=item_id,
                        title=item.get("title") or item.get("name", ""),
                        original_title=item.get("original_title") or item.get("original_name", ""),
                        media_type=media_type,
                        overview=item.get("overview", ""),
                        genres=[],
                        release_date=item.get("release_date") or item.get("first_air_date"),
                        original_language=item.get("original_language", "en"),
                        vote_average=item.get("vote_average", 0.0),
                        vote_count=item.get("vote_count", 0),
                        popularity=item.get("popularity", 0.0),
                        poster_path=item.get("poster_path"),
                        backdrop_path=item.get("backdrop_path")
                    ))
                    if len(results) >= limit:
                        break

        return results[:limit]

    def get_genres(self) -> List[GenreItem]:
        genres_set = set()
        if self.movies_df is not None:
            for g_str in self.movies_df["genres"].dropna():
                for g in str(g_str).split(","):
                    if g.strip():
                        genres_set.add(g.strip())

        if self.tv_df is not None:
            for g_str in self.tv_df["genres"].dropna():
                for g in str(g_str).split(","):
                    if g.strip():
                        genres_set.add(g.strip())

        return [GenreItem(id=i+1, name=name) for i, name in enumerate(sorted(genres_set))]

movie_service = MovieService()

