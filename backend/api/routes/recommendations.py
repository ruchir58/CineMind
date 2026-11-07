"""Recommendation endpoints for CineMind."""
from fastapi import APIRouter, HTTPException
from backend.models.schemas import (
    SmartRecommendationRequest,
    SmartRecommendationResponse,
    AIRecommendationRequest,
    AIRecommendationResponse
)
from backend.ml.content_recommender import content_recommender
from backend.ml.prompt_recommender import prompt_recommender

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.post("/smart", response_model=SmartRecommendationResponse)
async def get_smart_recommendations(req: SmartRecommendationRequest):
    """
    ML-Based Smart Recommendation Engine:
    Content-based filtering using TF-IDF vectorization and cosine similarity
    over selected titles, genres, overview, keywords, cast, and directors.
    """
    if not req.selected_titles:
        raise HTTPException(status_code=400, detail="At least one favourite title must be provided.")

    recs = content_recommender.recommend(
        selected_titles=req.selected_titles,
        media_type=req.media_type or "all",
        genres=req.genres,
        language=req.language,
        min_year=req.min_year,
        max_year=req.max_year,
        min_rating=req.min_rating,
        top_n=req.top_n
    )

    return SmartRecommendationResponse(
        selected_titles=req.selected_titles,
        total_results=len(recs),
        recommendations=recs
    )

@router.post("/ai", response_model=AIRecommendationResponse)
async def get_ai_recommendations(req: AIRecommendationRequest):
    """
    AI Prompt-Based Recommendation Engine:
    Understands natural-language prompts, extracts preferences,
    and performs semantic vector similarity search via SentenceTransformers.
    """
    cleaned_prompt = req.prompt.strip()
    if len(cleaned_prompt) < 3:
        raise HTTPException(status_code=400, detail="Prompt must be at least 3 characters.")

    recs, extracted = await prompt_recommender.recommend(
        prompt=cleaned_prompt,
        media_type=req.media_type or "all",
        top_n=req.top_n
    )

    return AIRecommendationResponse(
        prompt=cleaned_prompt,
        extracted_preferences=extracted,
        total_results=len(recs),
        recommendations=recs
    )

