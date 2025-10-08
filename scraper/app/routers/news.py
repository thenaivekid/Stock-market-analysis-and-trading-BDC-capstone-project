"""News router for ShareSansar news scraping."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.news_scraper import NewsScraperService

router = APIRouter(prefix="/news", tags=["news"])

news_service = NewsScraperService()


@router.get("/")
async def get_news(
    limit: Optional[int] = Query(20, ge=1, le=100, description="Number of news items to return"),
    max_pages: int = Query(3, ge=1, le=10, description="Maximum pages to scrape")
):
    """
    Get latest news from ShareSansar.
    
    - **limit**: Number of news items to return (1-100, default: 20)
    - **max_pages**: Maximum pages to scrape (1-10, default: 3)
    
    Returns a list of news items with:
    - title: News headline
    - date: Publication date
    - category: News category
    - description: Short description
    - link: Full article URL
    """
    try:
        news_items = news_service.scrape_news(limit=limit, max_pages=max_pages)
        
        if not news_items:
            return {
                "message": "No news items found. The website structure may have changed.",
                "count": 0,
                "news": []
            }
        
        return {
            "count": len(news_items),
            "news": news_items
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to scrape news: {str(e)}"
        )


@router.get("/latest")
async def get_latest_news(limit: int = Query(10, ge=1, le=50, description="Number of latest news items")):
    """
    Get the latest news items (optimized - scrapes only first page).
    
    - **limit**: Number of news items to return (1-50, default: 10)
    """
    try:
        news_items = news_service.scrape_news(limit=limit, max_pages=1)
        
        if not news_items:
            return {
                "message": "No news items found",
                "count": 0,
                "news": []
            }
        
        return {
            "count": len(news_items),
            "news": news_items
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch latest news: {str(e)}"
        )
