"""Common dependencies."""
from backend.services.movie_service import movie_service
from backend.services.tmdb_service import tmdb_service
from backend.ml.content_recommender import content_recommender
from backend.ml.prompt_recommender import prompt_recommender

def get_movie_service():
    return movie_service

def get_tmdb_service():
    return tmdb_service

def get_content_recommender():
    return content_recommender

def get_prompt_recommender():
    return prompt_recommender

