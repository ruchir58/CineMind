"""Script to collect movie data from TMDB API or seed data and write to data/raw/movies.csv."""
import os
import sys
import csv
import logging
from pathlib import Path
from typing import List, Dict, Any
import requests

# Add root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from backend.config.settings import settings
from scripts.seed_data import SEED_MOVIES

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

RAW_FILE = ROOT_DIR / "backend" / "data" / "raw" / "movies.csv"

def fetch_movies_from_tmdb(pages: int = 5) -> List[Dict[str, Any]]:
    """Fetch popular and top rated movies from TMDB API."""
    if not settings.TMDB_API_KEY and not settings.TMDB_ACCESS_TOKEN:
        logger.warning("No TMDB API credentials provided. Using seed movie data.")
        return []

    headers = {"Accept": "application/json"}
    if settings.TMDB_ACCESS_TOKEN:
        headers["Authorization"] = f"Bearer {settings.TMDB_ACCESS_TOKEN}"
    
    params_auth = {}
    if not settings.TMDB_ACCESS_TOKEN and settings.TMDB_API_KEY:
        params_auth["api_key"] = settings.TMDB_API_KEY

    collected = []
    seen_ids = set()

    endpoints = [
        "/movie/top_rated",
        "/movie/popular",
        "/discover/movie?sort_by=vote_count.desc"
    ]

    for ep in endpoints:
        for page in range(1, pages + 1):
            url = f"{settings.TMDB_BASE_URL}{ep}"
            params = {**params_auth, "page": page, "include_adult": False, "language": "en-US"}
            try:
                res = requests.get(url, headers=headers, params=params, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    results = data.get("results", [])
                    for item in results:
                        mid = item.get("id")
                        if mid and mid not in seen_ids:
                            seen_ids.add(mid)
                            # Fetch details including credits and keywords
                            details_url = f"{settings.TMDB_BASE_URL}/movie/{mid}"
                            details_params = {**params_auth, "append_to_response": "credits,keywords"}
                            d_res = requests.get(details_url, headers=headers, params=details_params, timeout=10)
                            if d_res.status_code == 200:
                                d = d_res.json()
                                genres = ", ".join([g["name"] for g in d.get("genres", [])])
                                credits = d.get("credits", {})
                                cast_list = [c["name"] for c in credits.get("cast", [])[:8]]
                                directors = [c["name"] for c in credits.get("crew", []) if c.get("job") == "Director"]
                                keywords_obj = d.get("keywords", {}).get("keywords", [])
                                kw_list = [k["name"] for k in keywords_obj[:10]]

                                collected.append({
                                    "id": mid,
                                    "title": d.get("title", ""),
                                    "original_title": d.get("original_title", ""),
                                    "overview": d.get("overview", ""),
                                    "genres": genres,
                                    "release_date": d.get("release_date", ""),
                                    "original_language": d.get("original_language", "en"),
                                    "vote_average": d.get("vote_average", 0.0),
                                    "vote_count": d.get("vote_count", 0),
                                    "popularity": d.get("popularity", 0.0),
                                    "poster_path": d.get("poster_path", ""),
                                    "backdrop_path": d.get("backdrop_path", ""),
                                    "cast": ", ".join(cast_list),
                                    "director": ", ".join(directors),
                                    "keywords": ", ".join(kw_list),
                                    "runtime": d.get("runtime", 0),
                                    "origin_country": ", ".join(d.get("origin_country", []))
                                })
                                logger.info(f"Fetched TMDB Movie: {d.get('title')}")
                else:
                    logger.warning(f"TMDB request failed with code {res.status_code}")
                    break
            except Exception as e:
                logger.error(f"Error fetching from TMDB: {e}")
                break

    return collected

def main():
    RAW_FILE.parent.mkdir(parents=True, exist_ok=True)
    movies = []

    # Attempt TMDB fetch if configured
    tmdb_movies = fetch_movies_from_tmdb(pages=2)
    movies.extend(tmdb_movies)

    # Always ensure high-quality seed movies are present
    seed_ids = {m["id"] for m in movies}
    for seed in SEED_MOVIES:
        if seed["id"] not in seed_ids:
            movies.append(seed)

    fieldnames = [
        "id", "title", "original_title", "overview", "genres",
        "release_date", "original_language", "vote_average", "vote_count",
        "popularity", "poster_path", "backdrop_path", "cast", "director",
        "keywords", "runtime", "origin_country"
    ]

    with open(RAW_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for movie in movies:
            writer.writerow(movie)

    logger.info(f"Saved {len(movies)} movies to {RAW_FILE}")

if __name__ == "__main__":
    main()

