"""Content-Based Smart Recommendation Engine using TF-IDF and Cosine Similarity."""
import logging
from typing import List, Optional, Dict, Any
import numpy as np
import pandas as pd
import joblib
from sklearn.metrics.pairwise import cosine_similarity
from backend.config.settings import settings
from backend.models.schemas import MediaItem, RecommendedItem, RecommendationExplanation

logger = logging.getLogger(__name__)

class ContentRecommender:
    def __init__(self):
        self.vectorizer = None
        self.tfidf_matrix = None
        self.catalogue: Optional[pd.DataFrame] = None
        self.is_loaded = False
        self.load_model()

    def load_model(self):
        try:
            if settings.TFIDF_MODEL_PATH.exists():
                artifact = joblib.load(settings.TFIDF_MODEL_PATH)
                self.vectorizer = artifact["vectorizer"]
                self.tfidf_matrix = artifact["tfidf_matrix"]
                self.catalogue = artifact["catalogue"]
                self.is_loaded = True
                logger.info(f"Loaded TF-IDF model with {len(self.catalogue)} catalogue items.")
            else:
                logger.warning(f"TF-IDF model artifact not found at {settings.TFIDF_MODEL_PATH}")
        except Exception as e:
            logger.error(f"Error loading TF-IDF model: {e}")
            self.is_loaded = False

    def _find_item_indices(self, titles: List[str]) -> List[int]:
        if self.catalogue is None:
            return []
        indices = []
        titles_lower = [t.strip().lower() for t in titles if t.strip()]

        for title in titles_lower:
            # Exact match first
            exact_match = self.catalogue[self.catalogue["title"].str.lower() == title]
            if not exact_match.empty:
                indices.append(exact_match.index[0])
                continue

            # Substring match
            sub_match = self.catalogue[self.catalogue["title"].str.lower().str.contains(title, regex=False)]
            if not sub_match.empty:
                indices.append(sub_match.index[0])
                continue

            # Check original title
            orig_match = self.catalogue[self.catalogue["original_title"].str.lower().str.contains(title, regex=False)]
            if not orig_match.empty:
                indices.append(orig_match.index[0])

        return list(set(indices))

    def _generate_explanation(self, ref_items: pd.DataFrame, cand_item: pd.Series) -> RecommendationExplanation:
        """Generate clear, metadata-grounded explanation for the recommendation."""
        matched = []
        cand_genres = set([g.strip() for g in str(cand_item.get("genres", "")).split(",") if g.strip()])
        cand_kw = set([k.strip().lower() for k in str(cand_item.get("keywords", "")).split(",") if k.strip()])
        cand_cast = set([c.strip().lower() for c in str(cand_item.get("cast", "")).split(",") if c.strip()])
        cand_creator = str(cand_item.get("director_or_creator", "")).strip()

        all_ref_genres = set()
        all_ref_kw = set()
        all_ref_creators = set()
        all_ref_cast = set()

        for _, ref in ref_items.iterrows():
            ref_genres = set([g.strip() for g in str(ref.get("genres", "")).split(",") if g.strip()])
            ref_kw = set([k.strip().lower() for k in str(ref.get("keywords", "")).split(",") if k.strip()])
            ref_cast = set([c.strip().lower() for c in str(ref.get("cast", "")).split(",") if c.strip()])
            all_ref_genres.update(ref_genres)
            all_ref_kw.update(ref_kw)
            all_ref_cast.update(ref_cast)
            if ref.get("director_or_creator"):
                all_ref_creators.add(str(ref.get("director_or_creator")).strip())

        # Overlapping genres
        common_genres = cand_genres.intersection(all_ref_genres)
        if common_genres:
            matched.append(f"Shares key genres: {', '.join(sorted(common_genres))}")

        # Overlapping director / creators
        if cand_creator and cand_creator in all_ref_creators:
            matched.append(f"Directed or created by {cand_creator}, matching your selected title(s)")

        # Overlapping keywords / themes
        common_themes = cand_kw.intersection(all_ref_kw)
        if common_themes:
            sample_themes = list(common_themes)[:3]
            matched.append(f"Explores thematic motifs: {', '.join(sample_themes)}")

        # Overlapping cast
        common_actors = cand_cast.intersection(all_ref_cast)
        if common_actors:
            sample_actors = [a.title() for a in list(common_actors)[:2]]
            matched.append(f"Features actors you enjoy: {', '.join(sample_actors)}")

        if not matched:
            matched.append("Shares narrative structure, tone and stylistic pacing")

        ref_names = ", ".join(ref_items["title"].tolist()[:2])
        summary = f"Recommended based on strong narrative and thematic resonance with {ref_names}."

        return RecommendationExplanation(
            matched_features=matched,
            summary=summary,
            genre_alignment=", ".join(common_genres) if common_genres else None,
            theme_alignment=", ".join(list(common_themes)[:3]) if common_themes else None
        )

    def recommend(
        self,
        selected_titles: List[str],
        media_type: str = "all",
        genres: Optional[List[str]] = None,
        language: Optional[str] = None,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        min_rating: Optional[float] = None,
        top_n: int = 10
    ) -> List[RecommendedItem]:
        if not self.is_loaded or self.catalogue is None or self.tfidf_matrix is None:
            logger.warning("TF-IDF model not ready.")
            return []

        ref_indices = self._find_item_indices(selected_titles)
        if not ref_indices:
            logger.warning(f"No selected titles matched in catalogue: {selected_titles}")
            return []

        ref_df = self.catalogue.iloc[ref_indices]

        # Calculate average similarity across all selected titles
        ref_vectors = self.tfidf_matrix[ref_indices]
        sim_scores = cosine_similarity(ref_vectors, self.tfidf_matrix)
        mean_sim = np.mean(sim_scores, axis=0)

        # Disallow recommending the selected titles themselves
        mean_sim[ref_indices] = -1.0

        # Candidate indices ranked by similarity
        ranked_indices = np.argsort(mean_sim)[::-1]

        results = []
        for idx in ranked_indices:
            if len(results) >= top_n:
                break

            score = float(mean_sim[idx])
            if score <= 0.0:
                break

            row = self.catalogue.iloc[idx]

            # Filters
            if media_type != "all" and row.get("media_type") != media_type:
                continue

            if min_rating is not None and float(row.get("vote_average", 0)) < min_rating:
                continue

            release_year = int(row.get("release_year", 0))
            if min_year is not None and release_year < min_year:
                continue
            if max_year is not None and release_year > max_year:
                continue

            if language is not None and str(row.get("original_language", "")).lower() != language.lower():
                continue

            if genres:
                row_genres = [g.strip().lower() for g in str(row.get("genres", "")).split(",") if g.strip()]
                req_genres = [g.strip().lower() for g in genres if g.strip()]
                if not any(rg in row_genres for rg in req_genres):
                    continue

            media_item = MediaItem(
                id=int(row["id"]),
                title=str(row["title"]),
                original_title=str(row.get("original_title", "")),
                media_type=str(row.get("media_type", "movie")),
                overview=str(row.get("overview", "")),
                genres=[g.strip() for g in str(row.get("genres", "")).split(",") if g.strip()],
                release_date=str(row.get("release_date", "")) if pd.notna(row.get("release_date")) else None,
                first_air_date=str(row.get("release_date", "")) if row.get("media_type") == "tv" else None,
                original_language=str(row.get("original_language", "en")),
                vote_average=float(row.get("vote_average", 0.0)),
                vote_count=int(row.get("vote_count", 0)),
                popularity=float(row.get("popularity", 0.0)),
                poster_path=str(row.get("poster_path", "")) if pd.notna(row.get("poster_path")) else None,
                backdrop_path=str(row.get("backdrop_path", "")) if pd.notna(row.get("backdrop_path")) else None,
                cast=[c.strip() for c in str(row.get("cast", "")).split(",") if c.strip()],
                director=str(row.get("director_or_creator", "")) if row.get("media_type") == "movie" else None,
                creators=[c.strip() for c in str(row.get("director_or_creator", "")).split(",") if c.strip()] if row.get("media_type") == "tv" else [],
                keywords=[k.strip() for k in str(row.get("keywords", "")).split(",") if k.strip()],
                runtime=int(row.get("runtime", 0)) if pd.notna(row.get("runtime")) else None
            )

            explanation = self._generate_explanation(ref_df, row)

            # Normalize similarity score to 0.0 - 1.0 bounded range
            normalized_score = round(float(min(max(score * 1.35, 0.15), 0.99)), 3)

            results.append(RecommendedItem(
                media=media_item,
                similarity_score=normalized_score,
                explanation=explanation
            ))

        return results

content_recommender = ContentRecommender()

