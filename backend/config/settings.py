"""CineMind Backend Configuration"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "CineMind"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # TMDB API
    TMDB_API_KEY: str = Field(default="", env="TMDB_API_KEY")
    TMDB_ACCESS_TOKEN: str = Field(default="", env="TMDB_ACCESS_TOKEN")
    TMDB_BASE_URL: str = "https://api.themoviedb.org/3"
    TMDB_IMAGE_BASE_URL: str = "https://image.tmdb.org/t/p"

    # Server settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"

    # Paths
    BASE_PATH: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DATA_DIR: Path = BASE_DIR / "data" / "raw"
    PROCESSED_DATA_DIR: Path = BASE_DIR / "data" / "processed"
    MODELS_DIR: Path = BASE_DIR / "models"

    MOVIES_RAW_PATH: Path = BASE_DIR / "data" / "raw" / "movies.csv"
    TV_RAW_PATH: Path = BASE_DIR / "data" / "raw" / "tv_shows.csv"
    MOVIES_CLEANED_PATH: Path = BASE_DIR / "data" / "processed" / "movies_cleaned.csv"
    TV_CLEANED_PATH: Path = BASE_DIR / "data" / "processed" / "tv_shows_cleaned.csv"

    TFIDF_MODEL_PATH: Path = BASE_DIR / "models" / "tfidf_model.joblib"
    EMBEDDINGS_CACHE_PATH: Path = BASE_DIR / "models" / "embeddings.joblib"

    # Embedding model name
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"

    # Optional LLM integration (Gemini / OpenAI)
    GEMINI_API_KEY: str = Field(default="", env="GEMINI_API_KEY")
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")

    class Config:
        env_file = ROOT_DIR / ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

