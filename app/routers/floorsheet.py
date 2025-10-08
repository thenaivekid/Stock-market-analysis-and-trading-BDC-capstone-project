"""Floorsheet router for stock scraping endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.scraper import ScraperService

router = APIRouter(prefix="/floorsheet", tags=["floorsheet"])

scraper_service = ScraperService()


class SymbolRequest(BaseModel):
    """Request model for stock symbol."""
    symbol: str = Field(..., min_length=1, max_length=10, description="Stock symbol (e.g., NABIL)")


class FloorsheetResponse(BaseModel):
    """Response model for floorsheet data."""
    symbol: str
    headers: list
    rows: list


@router.post("/", response_model=FloorsheetResponse)
async def get_floorsheet(data: SymbolRequest):
    """
    Scrape floorsheet data for a given stock symbol.
    
    - **symbol**: Stock symbol to scrape (e.g., "NABIL", "ADBL")
    """
    try:
        result = scraper_service.scrape_floorsheet(data.symbol.upper())
        return {
            "symbol": data.symbol.upper(),
            "headers": result["headers"],
            "rows": result["rows"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to scrape floorsheet for {data.symbol}: {str(e)}"
        )
