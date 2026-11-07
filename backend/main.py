"""Main FastAPI application for CineMind."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config.settings import settings
from backend.services.movie_service import movie_service
from backend.ml.content_recommender import content_recommender
from backend.ml.embeddings import embedding_service
from backend.api.routes import health, movies, tv_shows, search, recommendations

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("cinemind")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing CineMind Backend...")
    # Load data and models
    movie_service.load_local_data()
    content_recommender.load_model()
    embedding_service.load_cache()
    logger.info("CineMind Engine ready.")
    yield
    logger.info("Shutting down CineMind Backend.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="CineMind: AI-Powered Movie & TV Show Recommendation Platform",
    lifespan=lifespan
)

# CORS Configuration
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."}
    )

# Mount Routes
app.include_router(health.router, prefix="/api")
app.include_router(movies.router, prefix="/api")
app.include_router(tv_shows.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")

# Mount Frontend static files if built
frontend_dist = settings.BASE_PATH.parent / "frontend" / "dist"
if frontend_dist.exists():
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")
else:
    @app.get("/")
    async def root():
        return {
            "app": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "online",
            "documentation": "/docs",
            "description": "Discover Stories Beyond Imagination - AI Movie & TV Discovery Platform"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)

