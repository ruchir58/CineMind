"""TV Show endpoints."""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from backend.services.movie_service import movie_service
from backend.models.schemas import MediaItem

router = APIRouter(prefix="/tv-shows", tags=["TV Shows"])

@router.get("", response_model=List[MediaItem])
async def list_tv_shows(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    genre: Optional[str] = Query(None),
    sort_by: str = Query("popularity", pattern="^(popularity|rating|recent)$")
):
    return movie_service.get_tv_shows(page=page, page_size=page_size, genre=genre, sort_by=sort_by)

@router.get("/{show_id}", response_model=MediaItem)
async def get_tv_show(show_id: int):
    show = await movie_service.get_tv_by_id(show_id)
    if not show:
        raise HTTPException(status_code=404, detail=f"TV Show with id {show_id} not found.")
    return show
