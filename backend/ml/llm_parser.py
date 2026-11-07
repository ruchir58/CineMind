"""Optional LLM Intent Parser for advanced natural language prompt understanding.
Supports Gemini or OpenAI API when configured in .env, falling back seamlessly
to local NLP parser when no LLM key is present or when offline.
"""
import json
import logging
from typing import Dict, Any, Optional
import httpx
from backend.config.settings import settings

logger = logging.getLogger(__name__)

class LLMParser:
    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY
        self.openai_key = settings.OPENAI_API_KEY

    @property
    def is_available(self) -> bool:
        return bool(self.gemini_key or self.openai_key)

    async def parse_prompt_with_llm(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Attempt to extract structured preferences using configured LLM API."""
        if not self.is_available:
            return None

        system_instruction = (
            "You are an expert movie and TV show recommendation intent parser. "
            "Analyze the user's natural language request and extract their preferences into a strict JSON object with these keys: "
            "media_type ('movie', 'tv', or 'all'), "
            "detected_genres (list of strings like ['action', 'thriller', 'sci-fi']), "
            "detected_moods (list of strings like ['mind-bending', 'dark', 'emotional', 'suspenseful']), "
            "min_year (integer or null), "
            "max_year (integer or null), "
            "reference_titles (list of mentioned existing movie or TV show titles like ['Dark', 'Severance']), "
            "negative_features (list of things the user explicitly wants to avoid or have less of like ['time travel', 'horror']). "
            "Do NOT recommend movies. Only return the JSON object."
        )

        # 1. Try Gemini REST API
        if self.gemini_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": f"{system_instruction}\n\nUser request: \"{prompt}\""}
                        ]
                    }],
                    "generationConfig": {
                        "response_mime_type": "application/json"
                    }
                }
                async with httpx.AsyncClient(timeout=6.0) as client:
                    res = await client.post(url, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                        parsed = json.loads(raw_text)
                        logger.info("Successfully parsed prompt via Gemini API.")
                        return parsed
            except Exception as e:
                logger.warning(f"Gemini API parse failed: {e}. Falling back to local NLP parser.")

        # 2. Try OpenAI REST API
        if self.openai_key:
            try:
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {self.openai_key}"}
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ],
                    "response_format": {"type": "json_object"}
                }
                async with httpx.AsyncClient(timeout=6.0) as client:
                    res = await client.post(url, json=payload, headers=headers)
                    if res.status_code == 200:
                        data = res.json()
                        raw_text = data["choices"][0]["message"]["content"]
                        parsed = json.loads(raw_text)
                        logger.info("Successfully parsed prompt via OpenAI API.")
                        return parsed
            except Exception as e:
                logger.warning(f"OpenAI API parse failed: {e}. Falling back to local NLP parser.")

        return None

llm_parser = LLMParser()

