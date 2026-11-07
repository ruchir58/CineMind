"""Unit and integration test for CineMind backend and recommendation engines."""
import sys
from pathlib import Path

# Add root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from fastapi.testclient import TestClient
from backend.main import app

def run_tests():
    print("--- Testing CineMind Backend ---")
    with TestClient(app) as client:
        # 1. Health check
        res = client.get("/api/health")
        print("Health status code:", res.status_code)
        assert res.status_code == 200, "Health check failed"
        health_data = res.json()
        print("Health Response:", health_data)
        assert health_data["status"] == "healthy"
        assert health_data["dataset_movies_count"] > 0
        assert health_data["dataset_tv_count"] > 0
        assert health_data["ml_models_ready"] is True

        # 2. Movies list
        res = client.get("/api/movies?page=1&page_size=5")
        assert res.status_code == 200
        movies = res.json()
        print(f"Loaded {len(movies)} sample movies:")
        for m in movies[:3]:
            print(f" - [{m['id']}] {m['title']} ({m.get('release_date')}) - Rating: {m['vote_average']}")

        # 3. TV Shows list
        res = client.get("/api/tv-shows?page=1&page_size=5")
        assert res.status_code == 200
        shows = res.json()
        print(f"Loaded {len(shows)} sample TV shows:")
        for s in shows[:3]:
            print(f" - [{s['id']}] {s['title']} - Rating: {s['vote_average']}")

        # 4. Search endpoint
        res = client.get("/api/search?query=inception")
        assert res.status_code == 200
        search_data = res.json()
        print("Search results for 'inception':", len(search_data["results"]))
        assert len(search_data["results"]) > 0

        # 5. Smart Recommendation Engine test (Inception + Interstellar + The Prestige)
        print("\n--- Testing ML-Based Smart Recommendation Engine ---")
        smart_payload = {
            "selected_titles": ["Inception", "Interstellar", "The Prestige"],
            "media_type": "all",
            "top_n": 5
        }
        res = client.post("/api/recommendations/smart", json=smart_payload)
        assert res.status_code == 200
        smart_data = res.json()
        print(f"Smart recommendations for {smart_payload['selected_titles']}: {len(smart_data['recommendations'])}")
        for rec in smart_data["recommendations"]:
            print(f" * {rec['media']['title']} ({rec['media']['media_type']}) - Sim: {rec['similarity_score']}")
            print(f"   Explanation: {rec['explanation']['summary']}")
            for feat in rec['explanation']['matched_features']:
                print(f"    - {feat}")

        # 6. AI Prompt-Based Recommendation Engine test
        print("\n--- Testing AI Prompt-Based Recommendation Engine ---")
        ai_prompts = [
            "I want a psychological thriller with an unpredictable ending.",
            "Suggest a TV show similar to Dark and Severance.",
            "I want a science-fiction movie with time travel, mystery and emotional depth.",
            "Something like Dark but with less time travel."
        ]

        for prompt in ai_prompts:
            print(f"\n[Prompt]: \"{prompt}\"")
            ai_payload = {
                "prompt": prompt,
                "media_type": "all",
                "top_n": 4
            }
            res = client.post("/api/recommendations/ai", json=ai_payload)
            assert res.status_code == 200
            ai_data = res.json()
            print("Extracted preferences:", ai_data["extracted_preferences"])
            for rec in ai_data["recommendations"]:
                print(f" * {rec['media']['title']} ({rec['media']['media_type']}, {rec['media'].get('release_date')}) - Sim: {rec['similarity_score']}")
                for feat in rec['explanation']['matched_features']:
                    print(f"    - {feat}")

    print("\nALL BACKEND & ML RECOMMENDATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()

