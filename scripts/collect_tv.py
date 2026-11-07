"""Script to collect TV show data from TMDB API or seed data and write to data/raw/tv_shows.csv."""
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
from scripts.seed_data import SEED_TV_SHOWS

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

RAW_FILE = ROOT_DIR / "backend" / "data" / "raw" / "tv_shows.csv"

def fetch_tv_from_tmdb(pages: int = 5) -> List[Dict[str, Any]]:
    """Fetch popular and top rated TV shows from TMDB API."""
    if not settings.TMDB_API_KEY and not settings.TMDB_ACCESS_TOKEN:
        logger.warning("No TMDB API credentials provided. Using seed TV show data.")
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
        "/tv/top_rated",
        "/tv/popular",
        "/discover/tv?sort_by=vote_count.desc"
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
                        tvid = item.get("id")
                        if tvid and tvid not in seen_ids:
                            seen_ids.add(tvid)
                            details_url = f"{settings.TMDB_BASE_URL}/tv/{tvid}"
                            details_params = {**params_auth, "append_to_response": "credits,keywords"}
                            d_res = requests.get(details_url, headers=headers, params=details_params, timeout=10)
                            if d_res.status_code == 200:
                                d = d_res.json()
                                genres = ", ".join([g["name"] for g in d.get("genres", [])])
                                credits = d.get("credits", {})
                                cast_list = [c["name"] for c in credits.get("cast", [])[:8]]
                                creators = [c["name"] for c in d.get("created_by", [])]
                                keywords_obj = d.get("keywords", {}).get("results", [])
                                kw_list = [k["name"] for k in keywords_obj[:10]]
                                runtimes = d.get("episode_run_time", [])
                                ep_runtime = runtimes[0] if runtimes else 45

                                collected.append({
                                    "id": tvid,
                                    "title": d.get("name", ""),
                                    "original_title": d.get("original_name", ""),
                                    "overview": d.get("overview", ""),
                                    "genres": genres,
                                    "first_air_date": d.get("first_air_date", ""),
                                    "last_air_date": d.get("last_air_date", ""),
                                    "original_language": d.get("original_language", "en"),
                                    "vote_average": d.get("vote_average", 0.0),
                                    "vote_count": d.get("vote_count", 0),
                                    "popularity": d.get("popularity", 0.0),
                                    "poster_path": d.get("poster_path", ""),
                                    "backdrop_path": d.get("backdrop_path", ""),
                                    "cast": ", ".join(cast_list),
                                    "creators": ", ".join(creators),
                                    "keywords": ", ".join(kw_list),
                                    "number_of_seasons": d.get("number_of_seasons", 1),
                                    "number_of_episodes": d.get("number_of_episodes", 1),
                                    "episode_run_time": ep_runtime,
                                    "status": d.get("status", "Ended"),
                                    "origin_country": ", ".join(d.get("origin_country", []))
                                })
                                logger.info(f"Fetched TMDB TV Show: {d.get('name')}")
                else:
                    logger.warning(f"TMDB request failed with code {res.status_code}")
                    break
            except Exception as e:
                logger.error(f"Error fetching from TMDB: {e}")
                break

    return collected

def main():
    RAW_FILE.parent.mkdir(parents=True, exist_ok=True)
    tv_shows = []

    # Attempt TMDB fetch if configured
    tmdb_tv = fetch_tv_from_tmdb(pages=2)
    tv_shows.extend(tmdb_tv)

    # Always ensure high-quality seed TV shows are present
    seed_ids = {t["id"] for t in tv_shows}
    for seed in SEED_TV_SHOWS:
        if seed["id"] not in seed_ids:
            tv_shows.append(seed)

    fieldnames = [
        "id", "title", "original_title", "overview", "genres",
        "first_air_date", "last_air_date", "original_language", "vote_average",
        "vote_count", "popularity", "poster_path", "backdrop_path", "cast",
        "creators", "keywords", "number_of_seasons", "number_of_episodes",
        "episode_run_time", "status", "origin_country"
    ]

    with open(RAW_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for tv in tv_shows:
            writer.writerow(tv)

    logger.info(f"Saved {len(tv_shows)} TV shows to {RAW_FILE}")

if __name__ == "__main__":
    main()

