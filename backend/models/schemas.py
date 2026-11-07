"""Data schemas for CineMind."""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field

class CastMember(BaseModel):
    id: Optional[int] = None
    name: str
    character: Optional[str] = None
    profile_path: Optional[str] = None

class MediaItem(BaseModel):
    id: int
    title: str
    original_title: Optional[str] = None
    media_type: str = "movie"  # "movie" or "tv"
    overview: str = ""
    genres: List[str] = Field(default_factory=list)
    release_date: Optional[str] = None
    first_air_date: Optional[str] = None
    original_language: Optional[str] = "en"
    vote_average: float = 0.0
    vote_count: int = 0
    popularity: float = 0.0
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    cast: List[str] = Field(default_factory=list)
    director: Optional[str] = None  # for movies
    creators: List[str] = Field(default_factory=list)  # for TV
    keywords: List[str] = Field(default_factory=list)
    runtime: Optional[int] = None  # for movies
    number_of_seasons: Optional[int] = None  # for TV
    number_of_episodes: Optional[int] = None  # for TV
    status: Optional[str] = None
    origin_country: List[str] = Field(default_factory=list)
    trailer_key: Optional[str] = None
    trailer_url: Optional[str] = None

class RecommendationExplanation(BaseModel):
    matched_features: List[str] = Field(default_factory=list)
    summary: str = ""
    genre_alignment: Optional[str] = None
    mood_alignment: Optional[str] = None
    theme_alignment: Optional[str] = None

class RecommendedItem(BaseModel):
    media: MediaItem
    similarity_score: float = Field(..., description="Calculated similarity metric [0.0 - 1.0]")
    explanation: RecommendationExplanation

class SmartRecommendationRequest(BaseModel):
    selected_titles: List[str] = Field(..., min_items=1, description="Titles of selected movies/shows")
    media_type: Optional[str] = Field(default="all", description="'movie', 'tv', or 'all'")
    genres: Optional[List[str]] = Field(default=None, description="Optional genre filters")
    language: Optional[str] = Field(default=None, description="Optional ISO language filter")
    min_year: Optional[int] = Field(default=None, description="Minimum release year")
    max_year: Optional[int] = Field(default=None, description="Maximum release year")
    min_rating: Optional[float] = Field(default=None, description="Minimum TMDB rating [0-10]")
    top_n: int = Field(default=10, ge=1, le=50, description="Number of recommendations to return")

class SmartRecommendationResponse(BaseModel):
    selected_titles: List[str]
    total_results: int
    recommendations: List[RecommendedItem]
    disclaimer: str = "Similarity scores indicate content characteristic overlap and do not predict absolute subjective preference."

class AIRecommendationRequest(BaseModel):
    prompt: str = Field(..., min_length=3, description="Natural language description of desired content")
    media_type: Optional[str] = Field(default="all", description="'movie', 'tv', or 'all'")
    top_n: int = Field(default=10, ge=1, le=30, description="Number of recommendations")

class AIRecommendationResponse(BaseModel):
    prompt: str
    extracted_preferences: Dict[str, Any]
    total_results: int
    recommendations: List[RecommendedItem]

class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[MediaItem]

class GenreItem(BaseModel):
    id: int
    name: str

class HealthResponse(BaseModel):
    status: str
    project: str
    version: str
    dataset_movies_count: int
    dataset_tv_count: int
    tmdb_configured: bool
    ml_models_ready: bool

