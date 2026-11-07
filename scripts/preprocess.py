"""Data preprocessing and ML feature extraction pipeline for CineMind."""
import os
import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from backend.config.settings import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def clean_text(text: any) -> str:
    if pd.isna(text) or text is None:
        return ""
    return str(text).strip()

def normalize_genres(genre_str: any) -> str:
    if pd.isna(genre_str) or not genre_str:
        return ""
    genres = [g.strip() for g in str(genre_str).split(",") if g.strip()]
    return ", ".join(sorted(set(genres)))

def preprocess_movies(raw_path: Path, cleaned_path: Path) -> pd.DataFrame:
    logger.info(f"Preprocessing movies from {raw_path}")
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw movies file not found at {raw_path}")

    df = pd.read_csv(raw_path)

    # Deduplicate by TMDB ID
    df = df.drop_duplicates(subset=["id"])

    # Clean text columns
    text_cols = ["title", "original_title", "overview", "genres", "original_language", "cast", "director", "keywords", "origin_country"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_text)
        else:
            df[col] = ""

    # Normalize genres
    df["genres"] = df["genres"].apply(normalize_genres)

    # Standardize release date & year
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["release_year"] = pd.to_datetime(df["release_date"], errors="coerce").dt.year.fillna(2000).astype(int)

    # Handle numerical columns
    df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce").fillna(0.0).round(1)
    df["vote_count"] = pd.to_numeric(df["vote_count"], errors="coerce").fillna(0).astype(int)
    df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce").fillna(0.0).round(1)
    df["runtime"] = pd.to_numeric(df.get("runtime", 0), errors="coerce").fillna(0).astype(int)

    # Fill poster / backdrop
    df["poster_path"] = df["poster_path"].fillna("")
    df["backdrop_path"] = df["backdrop_path"].fillna("")
    df["media_type"] = "movie"

    # Filter out empty titles
    df = df[df["title"] != ""]

    cleaned_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(cleaned_path, index=False)
    logger.info(f"Saved {len(df)} cleaned movies to {cleaned_path}")
    return df

def preprocess_tv(raw_path: Path, cleaned_path: Path) -> pd.DataFrame:
    logger.info(f"Preprocessing TV shows from {raw_path}")
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw TV shows file not found at {raw_path}")

    df = pd.read_csv(raw_path)

    # Deduplicate by TMDB ID
    df = df.drop_duplicates(subset=["id"])

    # Clean text columns
    text_cols = ["title", "original_title", "overview", "genres", "original_language", "cast", "creators", "keywords", "origin_country", "status"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_text)
        else:
            df[col] = ""

    # Normalize genres
    df["genres"] = df["genres"].apply(normalize_genres)

    # Standardize air dates
    df["first_air_date"] = pd.to_datetime(df["first_air_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["release_year"] = pd.to_datetime(df["first_air_date"], errors="coerce").dt.year.fillna(2000).astype(int)

    # Handle numerical columns
    df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce").fillna(0.0).round(1)
    df["vote_count"] = pd.to_numeric(df["vote_count"], errors="coerce").fillna(0).astype(int)
    df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce").fillna(0.0).round(1)
    df["number_of_seasons"] = pd.to_numeric(df.get("number_of_seasons", 1), errors="coerce").fillna(1).astype(int)
    df["number_of_episodes"] = pd.to_numeric(df.get("number_of_episodes", 1), errors="coerce").fillna(1).astype(int)
    df["episode_run_time"] = pd.to_numeric(df.get("episode_run_time", 45), errors="coerce").fillna(45).astype(int)

    # Fill poster / backdrop
    df["poster_path"] = df["poster_path"].fillna("")
    df["backdrop_path"] = df["backdrop_path"].fillna("")
    df["media_type"] = "tv"

    # Filter out empty titles
    df = df[df["title"] != ""]

    cleaned_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(cleaned_path, index=False)
    logger.info(f"Saved {len(df)} cleaned TV shows to {cleaned_path}")
    return df

def build_combined_catalogue(movies_df: pd.DataFrame, tv_df: pd.DataFrame) -> pd.DataFrame:
    """Create a unified catalogue dataframe for both ML and AI recommendation engines."""
    m_copy = movies_df.copy()
    m_copy["director_or_creator"] = m_copy["director"]

    t_copy = tv_df.copy()
    t_copy["director_or_creator"] = t_copy["creators"]
    t_copy["release_date"] = t_copy["first_air_date"]
    t_copy["runtime"] = t_copy["episode_run_time"]

    common_cols = [
        "id", "title", "original_title", "media_type", "overview", "genres",
        "release_date", "release_year", "original_language", "vote_average",
        "vote_count", "popularity", "poster_path", "backdrop_path", "cast",
        "director_or_creator", "keywords", "runtime", "origin_country"
    ]

    for col in common_cols:
        if col not in m_copy.columns:
            m_copy[col] = ""
        if col not in t_copy.columns:
            t_copy[col] = ""

    combined = pd.concat([m_copy[common_cols], t_copy[common_cols]], ignore_index=True)
    return combined

def create_feature_soup(row: pd.Series) -> str:
    """Combine genres, keywords, overview, cast, director/creator, and language into a rich text representation."""
    genres = str(row.get("genres", "")).replace(",", " ")
    keywords = str(row.get("keywords", "")).replace(",", " ")
    cast = " ".join([c.strip().replace(" ", "") for c in str(row.get("cast", "")).split(",")[:5]])
    creator = str(row.get("director_or_creator", "")).replace(" ", "")
    overview = str(row.get("overview", ""))
    media_type = str(row.get("media_type", ""))
    language = str(row.get("original_language", ""))

    # Repeat genres and keywords for higher TF-IDF weighting
    soup = f"{genres} {genres} {keywords} {keywords} {cast} {creator} {media_type} {language} {overview}"
    return soup.lower()

def create_semantic_text(row: pd.Series) -> str:
    """Create a high-fidelity natural language summary for sentence embeddings."""
    title = row.get("title", "")
    media_type = "TV show" if row.get("media_type") == "tv" else "movie"
    genres = row.get("genres", "")
    overview = row.get("overview", "")
    keywords = row.get("keywords", "")
    creator = row.get("director_or_creator", "")
    year = row.get("release_year", "")

    return (
        f"{title} is a {year} {genres} {media_type} created by {creator}. "
        f"Synopsis: {overview} "
        f"Themes and elements: {keywords}."
    )

def train_and_export_models(combined_df: pd.DataFrame):
    """Fit TF-IDF matrix and compute semantic embeddings, saving artifacts via joblib."""
    settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. TF-IDF Model
    logger.info("Computing TF-IDF feature matrix...")
    combined_df["soup"] = combined_df.apply(create_feature_soup, axis=1)
    tfidf = TfidfVectorizer(stop_words="english", max_features=10000, ngram_range=(1, 2))
    tfidf_matrix = tfidf.fit_transform(combined_df["soup"])

    tfidf_artifact = {
        "vectorizer": tfidf,
        "tfidf_matrix": tfidf_matrix,
        "catalogue": combined_df
    }
    joblib.dump(tfidf_artifact, settings.TFIDF_MODEL_PATH)
    logger.info(f"TF-IDF model and matrix saved to {settings.TFIDF_MODEL_PATH}")

    # 2. Semantic Embeddings
    logger.info(f"Loading SentenceTransformer model '{settings.EMBEDDING_MODEL_NAME}'...")
    embedder = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    
    logger.info("Generating semantic embeddings for the catalogue...")
    semantic_texts = combined_df.apply(create_semantic_text, axis=1).tolist()
    embeddings = embedder.encode(semantic_texts, show_progress_bar=True, normalize_embeddings=True)

    embeddings_artifact = {
        "embeddings": embeddings,
        "model_name": settings.EMBEDDING_MODEL_NAME,
        "catalogue": combined_df
    }
    joblib.dump(embeddings_artifact, settings.EMBEDDINGS_CACHE_PATH)
    logger.info(f"Semantic embeddings saved to {settings.EMBEDDINGS_CACHE_PATH}")

def main():
    movies_df = preprocess_movies(settings.MOVIES_RAW_PATH, settings.MOVIES_CLEANED_PATH)
    tv_df = preprocess_tv(settings.TV_RAW_PATH, settings.TV_CLEANED_PATH)
    combined_df = build_combined_catalogue(movies_df, tv_df)
    train_and_export_models(combined_df)
    logger.info("Preprocessing and model training completed successfully.")

if __name__ == "__main__":
    main()

