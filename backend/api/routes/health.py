"""Health check route."""
from fastapi import APIRouter
from backend.config.settings import settings
from backend.services.tmdb_service import tmdb_service
from backend.services.movie_service import movie_service
from backend.ml.content_recommender import content_recommender
from backend.ml.embeddings import embedding_service
from backend.models.schemas import HealthResponse

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
async def check_health():
    movies_count = len(movie_service.movies_df) if movie_service.movies_df is not None else 0
    tv_count = len(movie_service.tv_df) if movie_service.tv_df is not None else 0
    ml_ready = bool(content_recommender.is_loaded and embedding_service.is_ready)

    return HealthResponse(
        status="healthy",
        project=settings.PROJECT_NAME,
        version=settings.VERSION,
        dataset_movies_count=movies_count,
        dataset_tv_count=tv_count,
        tmdb_configured=tmdb_service.is_configured,
        ml_models_ready=ml_ready
    )

