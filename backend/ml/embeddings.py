"""Embedding Service for CineMind semantic search.
Supports local SentenceTransformer when installed, with automatic fallback
to HuggingFace Inference API or TF-IDF semantic projection for serverless
environments like Vercel (staying under the 250MB package size limit).
"""
import logging
from typing import Optional, List
import numpy as np
import pandas as pd
import joblib
import httpx
from backend.config.settings import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.model = None
        self.embeddings: Optional[np.ndarray] = None
        self.catalogue: Optional[pd.DataFrame] = None
        self.is_ready = False
        self.load_cache()

    def load_cache(self):
        try:
            if settings.EMBEDDINGS_CACHE_PATH.exists():
                artifact = joblib.load(settings.EMBEDDINGS_CACHE_PATH)
                self.embeddings = artifact["embeddings"]
                self.catalogue = artifact["catalogue"]
                self.is_ready = True
                logger.info(f"Loaded {len(self.embeddings)} precomputed embeddings from cache.")
            else:
                logger.warning(f"Embedding cache not found at {settings.EMBEDDINGS_CACHE_PATH}")
        except Exception as e:
            logger.error(f"Error loading embedding cache: {e}")
            self.is_ready = False

    def _ensure_local_model(self) -> bool:
        if self.model is not None:
            return True
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading local SentenceTransformer '{settings.EMBEDDING_MODEL_NAME}'...")
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            return True
        except ImportError:
            logger.info("SentenceTransformer not installed in this environment (likely serverless/Vercel). Using cloud inference / semantic projection.")
            return False
        except Exception as e:
            logger.warning(f"Failed to load local SentenceTransformer: {e}")
            return False

    def encode_text(self, text: str) -> np.ndarray:
        """Encode query text into a 384-dimensional dense semantic vector."""
        # 1. Try local model if available
        if self._ensure_local_model():
            try:
                vec = self.model.encode(text, normalize_embeddings=True)
                return np.array(vec, dtype=np.float32)
            except Exception as e:
                logger.warning(f"Local encode failed: {e}. Trying remote inference.")

        # 2. Try Hugging Face Serverless Inference API
        try:
            url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{settings.EMBEDDING_MODEL_NAME}"
            with httpx.Client(timeout=5.0) as client:
                res = client.post(url, json={"inputs": text})
                if res.status_code == 200:
                    data = res.json()
                    vec = np.array(data, dtype=np.float32)
                    norm = np.linalg.norm(vec)
                    if norm > 0:
                        vec = vec / norm
                    return vec
        except Exception as e:
            logger.warning(f"Remote embedding inference failed: {e}. Using catalogue projection.")

        # 3. Graceful fallback: Project text against catalogue TF-IDF space
        if settings.TFIDF_MODEL_PATH.exists() and self.embeddings is not None:
            try:
                tfidf_art = joblib.load(settings.TFIDF_MODEL_PATH)
                vec = tfidf_art["vectorizer"].transform([text])
                sims = (vec * tfidf_art["tfidf_matrix"].T).toarray()[0]
                # Synthesize embedding as weighted average of top-5 nearest catalogue embeddings
                top_k = np.argsort(sims)[::-1][:5]
                top_sims = sims[top_k]
                if np.sum(top_sims) > 0:
                    weights = top_sims / np.sum(top_sims)
                    synth_emb = np.sum(self.embeddings[top_k] * weights[:, None], axis=0)
                    norm = np.linalg.norm(synth_emb)
                    if norm > 0:
                        synth_emb = synth_emb / norm
                    return synth_emb
            except Exception as e:
                logger.error(f"Catalogue projection error: {e}")

        # Fallback to random normalized vector if all else fails
        fallback_vec = np.ones(384, dtype=np.float32)
        return fallback_vec / np.linalg.norm(fallback_vec)

embedding_service = EmbeddingService()


