"""AI Prompt-Based Recommendation Engine using NLP, Semantic Embeddings and Hybrid Ranking."""
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from backend.ml.embeddings import embedding_service
from backend.ml.llm_parser import llm_parser
from backend.models.schemas import MediaItem, RecommendedItem, RecommendationExplanation

logger = logging.getLogger(__name__)

# Known genre keywords mapping to TMDB genres
GENRE_PATTERNS = {
    "action": ["action", "explosive", "martial arts", "gunfight", "adrenaline"],
    "adventure": ["adventure", "quest", "journey", "expedition", "explorer"],
    "animation": ["animation", "animated", "anime", "cartoon"],
    "comedy": ["comedy", "funny", "hilarious", "humorous", "laugh", "satire"],
    "crime": ["crime", "gangster", "heist", "mafia", "detective", "police", "investigation"],
    "documentary": ["documentary", "real life", "true story", "biography"],
    "drama": ["drama", "dramatic", "emotional", "character study", "heartbreaking"],
    "family": ["family", "kids", "children", "wholesome"],
    "fantasy": ["fantasy", "magic", "wizards", "dragons", "mythical"],
    "history": ["historical", "history", "period piece", "biographical"],
    "horror": ["horror", "scary", "terrifying", "creepy", "spooky", "monsters", "ghosts"],
    "music": ["music", "musical", "concert", "singing"],
    "mystery": ["mystery", "whodunit", "puzzle", "unsolved", "investigation"],
    "romance": ["romance", "romantic", "love story", "lovers", "relationship"],
    "science fiction": ["science fiction", "sci-fi", "scifi", "space", "future", "futuristic", "cyberpunk", "alien"],
    "thriller": ["thriller", "suspense", "tense", "psychological", "gripping", "edge of your seat"],
    "war": ["war", "military", "battlefield", "soldiers", "combat"],
    "western": ["western", "cowboy", "gunslinger", "saloon"]
}

# Mood and complexity attributes
MOOD_PATTERNS = {
    "mind-bending": ["mind-bending", "mind bending", "mess with my head", "trippy", "paradox", "complex plot", "intellectually challenging", "philosophical"],
    "unpredictable": ["unpredictable", "twist ending", "plot twist", "unexpected ending", "surprise ending", "shocking twist"],
    "dark": ["dark", "gritty", "bleak", "morbid", "grim", "nihilistic", "somber"],
    "suspenseful": ["suspenseful", "tense", "nail-biting", "high tension", "anxiety", "intense"],
    "emotional": ["emotional", "tearjerker", "touching", "heartfelt", "poignant", "melancholic", "grief"],
    "uplifting": ["uplifting", "inspiring", "feel good", "feel-good", "optimistic", "heartwarming"]
}

class PromptRecommender:
    def __init__(self):
        self.embedding_service = embedding_service

    def parse_prompt(self, prompt: str) -> Dict[str, Any]:
        """Extract structured preferences, filters, and reference titles from natural language prompt."""
        p_lower = prompt.lower()

        # 1. Media type preference
        media_type = "all"
        if re.search(r"\b(tv show|tv series|series|show|episodes|seasons)\b", p_lower):
            media_type = "tv"
        elif re.search(r"\b(movie|film|cinema|flick)\b", p_lower):
            media_type = "movie"

        # 2. Release year constraints
        min_year = None
        max_year = None
        after_match = re.search(r"\b(?:after|released after|since|post)\s+(\d{4})\b", p_lower)
        if after_match:
            min_year = int(after_match.group(1))

        before_match = re.search(r"\b(?:before|released before|prior to)\s+(\d{4})\b", p_lower)
        if before_match:
            max_year = int(before_match.group(1))

        if "90s" in p_lower or "nineties" in p_lower:
            min_year = 1990
            max_year = 1999
        elif "80s" in p_lower or "eighties" in p_lower:
            min_year = 1980
            max_year = 1989
        elif "classic" in p_lower and not max_year:
            max_year = 2000
        elif "recent" in p_lower or "new" in p_lower:
            min_year = 2018

        # 3. Target genres
        detected_genres = []
        for genre, keywords in GENRE_PATTERNS.items():
            if any(re.search(r"\b" + re.escape(kw) + r"\b", p_lower) for kw in keywords):
                detected_genres.append(genre)

        # 4. Target moods
        detected_moods = []
        for mood, keywords in MOOD_PATTERNS.items():
            if any(re.search(r"\b" + re.escape(kw) + r"\b", p_lower) for kw in keywords):
                detected_moods.append(mood)

        # 5. Reference titles
        reference_titles = []
        if self.embedding_service.catalogue is not None:
            catalogue_titles = self.embedding_service.catalogue["title"].tolist()
            for title in catalogue_titles:
                # Match title as a distinct phrase in prompt
                pattern = r"\b" + re.escape(title.lower()) + r"\b"
                if re.search(pattern, p_lower) and len(title) > 2:
                    reference_titles.append(title)

        # 6. Negative preferences (e.g. "less time travel", "without time travel", "not horror", "less violence")
        negative_features = []
        neg_matches = re.findall(r"\b(?:less|without|no|not|avoid|except)\s+([a-z\s]+?)(?:\.|\,|$|\band\b|\bbut\b)", p_lower)
        for neg in neg_matches:
            neg_clean = neg.strip().lower()
            if neg_clean and len(neg_clean) > 2:
                negative_features.append(neg_clean)

        return {
            "media_type": media_type,
            "min_year": min_year,
            "max_year": max_year,
            "detected_genres": detected_genres,
            "detected_moods": detected_moods,
            "reference_titles": reference_titles,
            "negative_features": negative_features
        }

    def _generate_ai_explanation(
        self,
        item: pd.Series,
        parsed_prefs: Dict[str, Any],
        raw_sim: float
    ) -> RecommendationExplanation:
        """Generate a grounded, informative explanation detailing why the recommendation matches the prompt."""
        matched = []
        title = item.get("title", "")
        item_genres = [g.strip().lower() for g in str(item.get("genres", "")).split(",") if g.strip()]
        item_kw = [k.strip().lower() for k in str(item.get("keywords", "")).split(",") if k.strip()]
        overview_lower = str(item.get("overview", "")).lower()

        # Mood alignment
        for mood in parsed_prefs["detected_moods"]:
            if mood == "mind-bending":
                if any(k in ["mind-bending", "dream", "time travel", "multiverse", "simulated reality", "causal loop", "quantum"] for k in item_kw):
                    matched.append("Features a mind-bending, reality-altering narrative")
            elif mood == "unpredictable":
                if any(k in ["twist ending", "conspiracy", "secrets", "mystery", "unreliable narrator"] for k in item_kw) or "twist" in overview_lower:
                    matched.append("Renowned for an unpredictable storyline with shocking revelations")
            elif mood == "dark":
                if any(k in ["dark", "nihilism", "grim", "bleak", "murder", "corruption", "dystopia"] for k in item_kw):
                    matched.append("Immerses you in a dark, atmospheric, morally complex tone")
            elif mood == "suspenseful":
                matched.append("High-stakes suspense that maintains relentless psychological tension")
            elif mood == "emotional":
                matched.append("Deep emotional resonance and profound character journeys")

        # Genre alignment
        matched_genres = [g for g in parsed_prefs["detected_genres"] if any(g in ig for ig in item_genres)]
        if matched_genres:
            matched.append(f"Direct match for your {', '.join(matched_genres).title()} preference")

        # Reference title resonance
        if parsed_prefs["reference_titles"]:
            ref_str = " & ".join(parsed_prefs["reference_titles"][:2])
            matched.append(f"Shares creative DNA, thematic complexity and narrative tone with {ref_str}")

        # Year constraint match
        if parsed_prefs.get("min_year") or parsed_prefs.get("max_year"):
            year = item.get("release_year")
            matched.append(f"Released in {year}, fitting your chronological criteria")

        if not matched:
            matched.append("Matches the semantic nuance, narrative complexity and vibe described in your prompt")

        summary = f"Selected because it seamlessly aligns with your request for {parsed_prefs.get('media_type', 'content')} with {item.get('genres')} qualities."

        return RecommendationExplanation(
            matched_features=matched,
            summary=summary,
            genre_alignment=", ".join(item_genres[:3]).title(),
            mood_alignment=", ".join(parsed_prefs["detected_moods"]).title() if parsed_prefs["detected_moods"] else "Engaging & Compelling"
        )

    async def recommend(
        self,
        prompt: str,
        media_type: str = "all",
        top_n: int = 10
    ) -> Tuple[List[RecommendedItem], Dict[str, Any]]:
        if not self.embedding_service.is_ready or self.embedding_service.embeddings is None:
            logger.warning("Embedding service not ready.")
            return [], {}

        catalogue = self.embedding_service.catalogue
        if catalogue is None:
            return [], {}

        # 1. Parse prompt into structured preferences (try LLM if configured, else local NLP)
        parsed = None
        if llm_parser.is_available:
            parsed = await llm_parser.parse_prompt_with_llm(prompt)
        
        if not parsed:
            parsed = self.parse_prompt(prompt)

        # Override parsed media_type if user explicitly set filter parameter
        effective_media_type = media_type if media_type != "all" else parsed["media_type"]

        # 2. Encode user prompt
        prompt_embedding = self.embedding_service.encode_text(prompt)

        # 3. Vector Similarity Search
        sim_scores = np.dot(self.embedding_service.embeddings, prompt_embedding)

        # 4. If reference titles exist, blend similarity with reference titles' embeddings
        if parsed["reference_titles"]:
            for ref_title in parsed["reference_titles"]:
                ref_match = catalogue[catalogue["title"].str.lower() == ref_title.lower()]
                if not ref_match.empty:
                    ref_idx = ref_match.index[0]
                    ref_emb = self.embedding_service.embeddings[ref_idx]
                    ref_sim = np.dot(self.embedding_service.embeddings, ref_emb)
                    # Blend 60% prompt embedding + 40% reference title embedding
                    sim_scores = 0.60 * sim_scores + 0.40 * ref_sim

        # 5. Apply negative feature penalties (e.g. "less time travel", "not horror")
        if parsed["negative_features"]:
            for neg in parsed["negative_features"]:
                neg_emb = self.embedding_service.encode_text(neg)
                neg_sim = np.dot(self.embedding_service.embeddings, neg_emb)
                # Penalize items with high similarity to negative feature
                penalty_mask = neg_sim > 0.35
                sim_scores[penalty_mask] -= (neg_sim[penalty_mask] * 0.4)

        # 6. Apply metadata boosts for explicit mood and genre alignment
        for idx in range(len(catalogue)):
            row = catalogue.iloc[idx]
            genres_lower = str(row.get("genres", "")).lower()
            kw_lower = str(row.get("keywords", "")).lower()

            # Genre boost
            if parsed["detected_genres"]:
                if any(dg in genres_lower for dg in parsed["detected_genres"]):
                    sim_scores[idx] += 0.08

            # Mood boost
            if parsed["detected_moods"]:
                if any(dm in kw_lower for dm in parsed["detected_moods"]):
                    sim_scores[idx] += 0.08

        # Exclude exact reference titles from recommendations (recommend similar, not the exact same)
        for ref_title in parsed["reference_titles"]:
            ref_match = catalogue[catalogue["title"].str.lower() == ref_title.lower()]
            if not ref_match.empty:
                sim_scores[ref_match.index[0]] = -1.0

        # Sort candidate indices
        ranked_indices = np.argsort(sim_scores)[::-1]

        results = []
        for idx in ranked_indices:
            if len(results) >= top_n:
                break

            score = float(sim_scores[idx])
            if score <= 0.0:
                break

            row = catalogue.iloc[idx]

            # Filter by media type
            if effective_media_type != "all" and row.get("media_type") != effective_media_type:
                continue

            # Year constraints
            release_year = int(row.get("release_year", 0))
            if parsed.get("min_year") and release_year < parsed["min_year"]:
                continue
            if parsed.get("max_year") and release_year > parsed["max_year"]:
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

            explanation = self._generate_ai_explanation(row, parsed, score)

            # Normalized bounded similarity score
            normalized_score = round(float(min(max(score * 1.25, 0.20), 0.99)), 3)

            results.append(RecommendedItem(
                media=media_item,
                similarity_score=normalized_score,
                explanation=explanation
            ))

        return results, parsed

prompt_recommender = PromptRecommender()

