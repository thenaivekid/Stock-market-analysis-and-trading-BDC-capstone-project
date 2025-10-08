
from fastapi import FastAPI
from app.api import router as api_router
from app.routers.floorsheet import router as floorsheet_router
from app.routers.market import router as market_router
from app.routers.news import router as news_router

app = FastAPI(
    title="NEPSE Data API",
    description="API for scraping and managing NEPSE stock market data",
    version="1.0.0"
)

# Include routers
app.include_router(api_router, prefix="/api", tags=["metadata"])
app.include_router(floorsheet_router, prefix="/api")
app.include_router(market_router, prefix="/api")
app.include_router(news_router, prefix="/api")


@app.get("/", tags=["health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "NEPSE Data API is running",
        "docs": "/docs"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "service": "nepse-scraper",
        "version": "1.0.0"
    }
