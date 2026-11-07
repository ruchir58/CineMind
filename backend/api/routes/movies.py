"""Movie endpoints."""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from backend.services.movie_service import movie_service
from backend.models.schemas import MediaItem

router = APIRouter(prefix="/movies", tags=["Movies"])

@router.get("", response_model=List[MediaItem])
async def list_movies(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    genre: Optional[str] = Query(None),
    sort_by: str = Query("popularity", pattern="^(popularity|rating|recent)$")
):
    return movie_service.get_movies(page=page, page_size=page_size, genre=genre, sort_by=sort_by)

@router.get("/{movie_id}", response_model=MediaItem)
async def get_movie(movie_id: int):
    movie = await movie_service.get_movie_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with id {movie_id} not found.")
    return movie
