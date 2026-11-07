# CineMind

> **AI-Powered Movie & TV Show Recommendation Platform**
> Discover Stories Beyond Imagination.

CineMind is an entertainment discovery and recommendation web application designed to help users discover movies and television shows based on their tastes, preferred titles, and natural-language descriptions.

---

## Key Highlights

- **Instant Use**: No user registration, no login accounts, no subscription paywalls, no persistent tracking, and no external database servers required.
- **Dual Independent Recommendation Engines**:
  1. **ML-Based Smart Recommendation Engine**: Content-based filtering via TF-IDF vectorization and cosine similarity over multi-attribute feature vectors (genres, overview, keywords, cast, directors, and creators).
  2. **AI-Powered Prompt-Based Recommendation Engine**: Natural-language semantic search powered by `SentenceTransformers` (`all-MiniLM-L6-v2`), dense vector similarity, reference-title blending, negative preference suppression, and metadata re-ranking.
- **Metadata-Grounded Explanations**: Every recommendation includes a dedicated *"Why We Recommended It"* explanation citing exact thematic, mood, and personnel overlaps.
- **Graceful Dual-Mode Data Operation**: Works seamlessly with live TMDB API v3 data when credentials are provided, or out-of-the-box with a high-fidelity local dataset of over 240+ iconic titles.
- **Cinematic Dark UI**: Built with React, Vite, Tailwind CSS, Lucide icons, and Framer Motion transitions.

---

## Architecture Overview

```
                        [ User / Browser ]
                                |
                   (Vite / React SPA - Port 5173)
                                |
                                v
               [ FastAPI Backend Server - Port 8000 ]
                     |                     |
     +---------------+                     +----------------+
     |                                                      |
     v                                                      v
[ ML Content Recommender ]                      [ AI Prompt Recommender ]
  - TF-IDF Vectorizer                             - SentenceTransformers (all-MiniLM-L6-v2)
  - Cosine Similarity                             - Natural Language Parser
  - Multi-Title Centroid Aggregation              - Intent & Mood Extraction
  - Feature Soup Representation                   - Dense Semantic Embeddings
  - Feature-Overlap Explanations                  - Reference Blending & Negation
     |                                                      |
     +-----------------------+------------------------------+
                             |
                             v
                [ Unified Data Access Layer ]
                  - Local Cleaned CSVs (Movies + TV)
                  - Precomputed Vector Artifacts (Joblib)
                  - TMDB API Service (with Retries & Caching)
```

---

## Technology Stack

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Animations**: Framer Motion
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Validation**: Pydantic v2 & Pydantic-Settings
- **HTTP Client**: HTTPX & Requests

### Machine Learning & NLP
- **Scikit-learn**: TF-IDF Vectorization, N-grams, Cosine Similarity
- **Sentence-Transformers**: `all-MiniLM-L6-v2` (384-dimensional dense semantic representations)
- **PyTorch**: Deep learning inference engine for sentence embeddings
- **Pandas & NumPy**: High-performance catalogue manipulation and vector math
- **Joblib**: Model and embedding vector serialization

---

## Project Structure

```
CineMind/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── Footer.jsx
│   │   │   ├── MediaCard.jsx
│   │   │   ├── MediaDetailsModal.jsx
│   │   │   └── ExplanationBadge.jsx
│   │   ├── pages/
│   │   │   ├── HomePage.jsx
│   │   │   ├── SmartRecommendationsPage.jsx
│   │   │   ├── AIFinderPage.jsx
│   │   │   └── ExplorePage.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py
│   │   │   ├── movies.py
│   │   │   ├── tv_shows.py
│   │   │   ├── search.py
│   │   │   └── recommendations.py
│   │   └── dependencies.py
│   │
│   ├── ml/
│   │   ├── content_recommender.py
│   │   ├── prompt_recommender.py
│   │   └── embeddings.py
│   │
│   ├── services/
│   │   ├── tmdb_service.py
│   │   └── movie_service.py
│   │
│   ├── data/
│   │   ├── raw/
│   │   │   ├── movies.csv
│   │   │   └── tv_shows.csv
│   │   └── processed/
│   │       ├── movies_cleaned.csv
│   │       └── tv_shows_cleaned.csv
│   │
│   ├── models/
│   │   ├── schemas.py
│   │   ├── tfidf_model.joblib
│   │   └── embeddings.joblib
│   │
│   ├── config/
│   │   └── settings.py
│   │
│   ├── main.py
│   └── requirements.txt
│
├── scripts/
│   ├── seed_data.py
│   ├── collect_movies.py
│   ├── collect_tv.py
│   └── preprocess.py
│
├── tests/
│   └── test_backend.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Getting Started

### 1. Prerequisites
- **Python**: Version 3.10+ (tested with Python 3.13)
- **Node.js**: Version 18+ (tested with Node.js v24 & npm 11)

### 2. Clone and Setup Environment

```bash
# Clone or open the repository
cd CineMind

# Create and activate Python virtual environment
python -m venv .venv

# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On macOS / Linux:
source .venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt
```

### 3. TMDB API Credentials (Optional but Recommended)

Create a `.env` file in the project root:

```env
# TMDB API Credentials (optional for live data expansion)
TMDB_API_KEY=YOUR_TMDB_API_KEY
TMDB_ACCESS_TOKEN=YOUR_TMDB_ACCESS_TOKEN

# Server Settings
HOST=127.0.0.1
PORT=8000
DEBUG=True
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

> **Note**: Even without TMDB credentials, CineMind includes a pre-seeded, preprocessed dataset of over 240+ iconic movies and shows ready to explore immediately.

### 4. Data Collection & Model Training (Optional - Precomputed on Disk)

To collect additional records or re-train models from scratch:

```bash
# Collect movie and TV records
python scripts/collect_movies.py
python scripts/collect_tv.py

# Preprocess and train TF-IDF & SentenceTransformer embeddings
python scripts/preprocess.py
```

### 5. Running the Application

#### Option 1: One-Click Startup (Recommended on Windows)

Simply double-click:
```powershell
start.bat
```
This automated batch script will:
1. Detect or initialize the Python virtual environment and dependencies.
2. Verify the precomputed recommendation models and semantic vector embeddings.
3. Verify the frontend production build.
4. Launch the FastAPI server at `http://127.0.0.1:8000`.
5. Open your default web browser directly to CineMind.

For live development with hot module reloading (HMR):
```powershell
dev.bat
```

---

#### Option 2: Unified Mode (FastAPI serves both API and React Frontend)

Build the frontend once:
```bash
cd frontend
npm install
npm run build
cd ..
```

Then start the server:
```bash
python backend/main.py
```
Open **`http://127.0.0.1:8000`** in your browser.

---

#### Option B: Full-Stack Dev Mode (Live Reloading)

**Terminal 1 (Backend API):**
```bash
python backend/main.py
# Running on http://127.0.0.1:8000
```

**Terminal 2 (Frontend with Vite HMR):**
```bash
cd frontend
npm install
npm run dev
# Running on http://localhost:5173
```
Open **`http://localhost:5173`** in your browser.

---

## Recommendation Engines Explained

### 1. ML-Based Smart Recommendation Engine (`content_recommender.py`)
- **Feature Soup**: Combines genres (weighted 2x), keywords (weighted 2x), director / creators, top cast members, original language, and plot overview.
- **Vector Representation**: Unigram and bigram TF-IDF vectorization with English stopword suppression (`max_features=10000`).
- **Centroid Aggregation**: When multiple favourite titles are chosen (e.g. *Inception* + *Interstellar* + *The Prestige*), their vector representations are averaged into a centroid preference vector.
- **Cosine Similarity**: Calculates angular similarity against all catalogue vectors, removes already-selected titles, applies runtime filters (genres, year, rating, media type), and ranks top candidates.
- **Score Representation**: Displays similarity scores as content feature overlap metrics.

### 2. AI Prompt-Based Recommendation Engine (`prompt_recommender.py`)
- **Semantic Embeddings**: Encodes catalogue items using `SentenceTransformer('all-MiniLM-L6-v2')` into 384-dimensional unit-normalized dense vectors.
- **NLP Intent Extraction**:
  - Media format detection (`movie` vs `tv show`)
  - Year constraints (e.g. `"after 2015"`, `"90s"`, `"classic"`)
  - Mood & vibe detection (`mind-bending`, `unpredictable`, `dark`, `suspenseful`, `emotional`)
  - Reference title extraction (e.g. `"similar to Dark and Severance"`)
  - Negative preference extraction (e.g. `"with less time travel"`, `"not horror"`)
- **Hybrid Vector Re-Ranking**:
  - Computes dense inner product against user query vector.
  - Blends reference title vectors (60% query + 40% reference title embedding).
  - Applies negative feature penalties against unwanted traits.
  - Applies metadata boosts for matching mood and genre affinities.
- **Explanations**: Deterministically explains why each recommended title was selected using actual metadata (e.g. *"Shares creative DNA, thematic complexity and narrative tone with Dark & Severance"*).

---

## API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health, dataset counts, and ML model statuses |
| `GET` | `/api/movies` | List movies with pagination, genre, and sort filtering |
| `GET` | `/api/movies/{id}` | Retrieve comprehensive movie details, cast, and director |
| `GET` | `/api/tv-shows` | List TV shows with seasons, air dates, and creators |
| `GET` | `/api/tv-shows/{id}` | Retrieve comprehensive TV show details |
| `GET` | `/api/search` | Multi-field search across titles, overviews, actors, and directors |
| `GET` | `/api/trending` | Current trending movies and TV series |
| `GET` | `/api/popular` | Most popular media |
| `GET` | `/api/top-rated` | Highest rated titles |
| `GET` | `/api/genres` | List of all unique genres across catalogue |
| `GET` | `/api/similar/{type}/{id}` | Find titles similar to a specified media item |
| `POST` | `/api/recommendations/smart` | ML content-based recommendations from favourite titles |
| `POST` | `/api/recommendations/ai` | AI natural-language prompt recommendation engine |

---

## Running the Automated Test Suite

To verify backend connectivity, recommendation accuracy, and API status codes:

```bash
python tests/test_backend.py
```

Expected output:
```
--- Testing CineMind Backend ---
Health status code: 200
Loaded sample movies and TV shows...
Search results for 'inception': > 0
--- Testing ML-Based Smart Recommendation Engine ---
Smart recommendations generated with feature explanations.
--- Testing AI Prompt-Based Recommendation Engine ---
All sample natural-language prompts parsed and resolved.
ALL BACKEND & ML RECOMMENDATION TESTS PASSED SUCCESSFULLY!
```

---

## TMDB Attribution & Data Policy

- This product uses the TMDB API but is not endorsed or certified by TMDB.
- TMDB API terms do not permit mass unauthorized re-distribution or persistent automated scraper harvesting of the entire TMDB catalogue. CineMind uses focused discover and search endpoints with caching and rate-limiting.
- For more information, visit [The Movie Database (TMDB)](https://www.themoviedb.org/).

