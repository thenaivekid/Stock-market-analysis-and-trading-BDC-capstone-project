"""Market data router for live stock market endpoints."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from app.services.market_data import MarketDataService

router = APIRouter(prefix="/market", tags=["market"])

market_service = MarketDataService()


class StockData(BaseModel):
    """Stock data model."""
    symbol: str
    securityName: Optional[str] = None
    sector: Optional[str] = None
    lastTradedPrice: Optional[float] = None
    percentageChange: Optional[float] = None
    change: Optional[float] = None
    openPrice: Optional[float] = None
    highPrice: Optional[float] = None
    lowPrice: Optional[float] = None
    previousClose: Optional[float] = None
    totalTransactions: Optional[int] = None
    totalTradeQuantity: Optional[float] = None
    totalTradeValue: Optional[float] = None
    lastTradedVolume: Optional[int] = None
    lastUpdatedDateTime: Optional[str] = None


class MarketSummary(BaseModel):
    """Market summary model."""
    totalStocks: int
    advancing: int
    declining: int
    unchanged: int
    totalTurnover: float
    totalVolume: int
    totalTransactions: int
    timestamp: str


@router.get("/live", response_model=List[dict])
async def get_live_data():
    """
    Get live market data for all stocks.
    
    Returns complete real-time data for all listed securities.
    """
    try:
        return market_service.fetch_live_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary", response_model=MarketSummary)
async def get_market_summary():
    """
    Get overall market summary statistics.
    
    Includes:
    - Total stocks
    - Advancing/declining/unchanged counts
    - Total turnover, volume, transactions
    """
    try:
        return market_service.get_market_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gainers", response_model=List[dict])
async def get_top_gainers(
    limit: int = Query(10, ge=1, le=100, description="Number of stocks to return")
):
    """
    Get top gainers by percentage change.
    
    - **limit**: Number of stocks to return (1-100, default: 10)
    
    Sorted by highest positive percentage change.
    """
    try:
        return market_service.get_top_gainers(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/losers", response_model=List[dict])
async def get_top_losers(
    limit: int = Query(10, ge=1, le=100, description="Number of stocks to return")
):
    """
    Get top losers by percentage change.
    
    - **limit**: Number of stocks to return (1-100, default: 10)
    
    Sorted by largest negative percentage change.
    """
    try:
        return market_service.get_top_losers(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active/volume", response_model=List[dict])
async def get_most_active_by_volume(
    limit: int = Query(10, ge=1, le=100, description="Number of stocks to return")
):
    """
    Get most active stocks by trading volume.
    
    - **limit**: Number of stocks to return (1-100, default: 10)
    
    Sorted by highest total trade quantity.
    """
    try:
        return market_service.get_most_active_by_volume(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active/value", response_model=List[dict])
async def get_most_active_by_value(
    limit: int = Query(10, ge=1, le=100, description="Number of stocks to return")
):
    """
    Get most active stocks by trading value (turnover).
    
    - **limit**: Number of stocks to return (1-100, default: 10)
    
    Sorted by highest total trade value in NPR.
    """
    try:
        return market_service.get_most_active_by_value(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active/transactions", response_model=List[dict])
async def get_most_active_by_transactions(
    limit: int = Query(10, ge=1, le=100, description="Number of stocks to return")
):
    """
    Get most active stocks by number of transactions.
    
    - **limit**: Number of stocks to return (1-100, default: 10)
    
    Sorted by highest number of transactions.
    """
    try:
        return market_service.get_most_active_by_transactions(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/52week/high", response_model=List[dict])
async def get_52_week_high(
    limit: int = Query(10, ge=1, le=100, description="Number of stocks to return")
):
    """
    Get stocks near or at 52-week high.
    
    - **limit**: Number of stocks to return (1-100, default: 10)
    
    Sorted by proximity to 52-week high price.
    """
    try:
        return market_service.get_52_week_high(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/52week/low", response_model=List[dict])
async def get_52_week_low(
    limit: int = Query(10, ge=1, le=100, description="Number of stocks to return")
):
    """
    Get stocks near or at 52-week low.
    
    - **limit**: Number of stocks to return (1-100, default: 10)
    
    Sorted by proximity to 52-week low price.
    """
    try:
        return market_service.get_52_week_low(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sector/{sector_name}", response_model=List[dict])
async def get_sector_stocks(sector_name: str):
    """
    Get all stocks in a specific sector.
    
    - **sector_name**: Name of the sector (e.g., "Commercial Banks", "Hydropower")
    
    Returns all stocks in the sector sorted by percentage change.
    """
    try:
        stocks = market_service.get_by_sector(sector_name)
        if not stocks:
            raise HTTPException(
                status_code=404, 
                detail=f"No stocks found in sector: {sector_name}"
            )
        return stocks
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
