"""Search, genres, trending and catalogue browse routes."""
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from backend.services.movie_service import movie_service
from backend.services.tmdb_service import tmdb_service
from backend.models.schemas import MediaItem, SearchResponse, GenreItem

router = APIRouter(tags=["Discovery & Search"])

@router.get("/search", response_model=SearchResponse)
async def search_media(query: str = Query(..., min_length=1), limit: int = Query(20, ge=1, le=50)):
    results = await movie_service.search(query, limit=limit)
    return SearchResponse(query=query, total_results=len(results), results=results)

@router.get("/genres", response_model=List[GenreItem])
async def list_genres():
    return movie_service.get_genres()

@router.get("/trending", response_model=List[MediaItem])
async def get_trending(media_type: str = Query("all", pattern="^(all|movie|tv)$")):
    # Try TMDB first
    if tmdb_service.is_configured:
        tmdb_res = await tmdb_service.get_trending(media_type=media_type)
        if tmdb_res and "results" in tmdb_res:
            items = []
            for item in tmdb_res["results"][:16]:
                mtype = item.get("media_type", media_type)
                if mtype == "all":
                    mtype = "movie" if "title" in item else "tv"
                items.append(MediaItem(
                    id=item.get("id"),
                    title=item.get("title") or item.get("name", ""),
                    original_title=item.get("original_title") or item.get("original_name", ""),
                    media_type=mtype,
                    overview=item.get("overview", ""),
                    genres=[],
                    release_date=item.get("release_date") or item.get("first_air_date"),
                    vote_average=item.get("vote_average", 0.0),
                    vote_count=item.get("vote_count", 0),
                    popularity=item.get("popularity", 0.0),
                    poster_path=item.get("poster_path"),
                    backdrop_path=item.get("backdrop_path")
                ))
            if items:
                return items

    # Local fallback
    if media_type == "movie":
        return movie_service.get_movies(page=1, page_size=16, sort_by="popularity")
    elif media_type == "tv":
        return movie_service.get_tv_shows(page=1, page_size=16, sort_by="popularity")
    else:
        movies = movie_service.get_movies(page=1, page_size=8, sort_by="popularity")
        tv = movie_service.get_tv_shows(page=1, page_size=8, sort_by="popularity")
        return movies + tv

@router.get("/popular", response_model=List[MediaItem])
async def get_popular(media_type: str = Query("all", pattern="^(all|movie|tv)$")):
    if media_type == "movie":
        return movie_service.get_movies(page=1, page_size=16, sort_by="popularity")
    elif media_type == "tv":
        return movie_service.get_tv_shows(page=1, page_size=16, sort_by="popularity")
    else:
        movies = movie_service.get_movies(page=1, page_size=8, sort_by="popularity")
        tv = movie_service.get_tv_shows(page=1, page_size=8, sort_by="popularity")
        return movies + tv

@router.get("/top-rated", response_model=List[MediaItem])
async def get_top_rated(media_type: str = Query("all", pattern="^(all|movie|tv)$")):
    if media_type == "movie":
        return movie_service.get_movies(page=1, page_size=16, sort_by="rating")
    elif media_type == "tv":
        return movie_service.get_tv_shows(page=1, page_size=16, sort_by="rating")
    else:
        movies = movie_service.get_movies(page=1, page_size=8, sort_by="rating")
        tv = movie_service.get_tv_shows(page=1, page_size=8, sort_by="rating")
        return movies + tv

@router.get("/similar/{media_type}/{media_id}", response_model=List[MediaItem])
async def get_similar(media_type: str, media_id: int):
    # Try TMDB
    if tmdb_service.is_configured:
        if media_type == "movie":
            sim_res = await tmdb_service.get_similar_movies(media_id)
        else:
            sim_res = await tmdb_service.get_similar_tv(media_id)

        if sim_res and "results" in sim_res:
            items = []
            for item in sim_res["results"][:10]:
                items.append(MediaItem(
                    id=item.get("id"),
                    title=item.get("title") or item.get("name", ""),
                    original_title=item.get("original_title") or item.get("original_name", ""),
                    media_type=media_type,
                    overview=item.get("overview", ""),
                    genres=[],
                    release_date=item.get("release_date") or item.get("first_air_date"),
                    vote_average=item.get("vote_average", 0.0),
                    vote_count=item.get("vote_count", 0),
                    popularity=item.get("popularity", 0.0),
                    poster_path=item.get("poster_path"),
                    backdrop_path=item.get("backdrop_path")
                ))
            if items:
                return items

    # Fallback to local similarity search
    # Find title of current item
    target_item = None
    if media_type == "movie":
        target_item = await movie_service.get_movie_by_id(media_id)
    else:
        target_item = await movie_service.get_tv_by_id(media_id)

    if not target_item:
        raise HTTPException(status_code=404, detail="Media item not found.")

    from backend.ml.content_recommender import content_recommender
    sim_recs = content_recommender.recommend(
        selected_titles=[target_item.title],
        media_type=media_type,
        top_n=10
    )
    return [rec.media for rec in sim_recs]
