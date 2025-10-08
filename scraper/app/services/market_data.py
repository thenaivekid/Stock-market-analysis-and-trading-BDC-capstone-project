"""Market data service for fetching and processing live NEPSE data."""

from typing import List, Dict, Optional
import requests
from datetime import datetime


class MarketDataService:
    """Service for fetching and analyzing live market data."""
    
    API_URL = "https://sharehubnepal.com/live/api/v2/nepselive/live-nepse"
    
    KEY_COLUMNS = [
        'symbol',
        'securityName',
        'sector',
        'lastTradedPrice',
        'percentageChange',
        'change',
        'openPrice',
        'highPrice',
        'lowPrice',
        'previousClose',
        'totalTransactions',
        'totalTradeQuantity',
        'totalTradeValue',
        'lastTradedVolume',
        'lastUpdatedDateTime'
    ]
    
    def fetch_live_data(self) -> List[Dict]:
        """
        Fetch live market data from ShareHub Nepal API.
        
        Returns:
            List of stock data dictionaries
            
        Raises:
            Exception: If API request fails
        """
        try:
            response = requests.get(self.API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data or not data.get('success'):
                raise Exception("Invalid or unsuccessful API response")
            
            stocks = data.get('data', [])
            if not stocks:
                raise Exception("No stock data available")
            
            # Filter and return only key columns
            filtered_stocks = []
            for stock in stocks:
                filtered_stock = {
                    key: stock.get(key) for key in self.KEY_COLUMNS if key in stock
                }
                # Add all available data even if not in key columns
                filtered_stock.update(stock)
                filtered_stocks.append(filtered_stock)
            
            return filtered_stocks
            
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch market data: {str(e)}")
    
    def get_top_gainers(self, limit: int = 10) -> List[Dict]:
        """
        Get top gainers by percentage change.
        
        Args:
            limit: Number of stocks to return
            
        Returns:
            List of top gaining stocks
        """
        stocks = self.fetch_live_data()
        
        # Filter stocks with positive change and sort by percentageChange
        gainers = [s for s in stocks if s.get('percentageChange', 0) > 0]
        gainers.sort(key=lambda x: float(x.get('percentageChange', 0)), reverse=True)
        
        return gainers[:limit]
    
    def get_top_losers(self, limit: int = 10) -> List[Dict]:
        """
        Get top losers by percentage change.
        
        Args:
            limit: Number of stocks to return
            
        Returns:
            List of top losing stocks
        """
        stocks = self.fetch_live_data()
        
        # Filter stocks with negative change and sort by percentageChange
        losers = [s for s in stocks if s.get('percentageChange', 0) < 0]
        losers.sort(key=lambda x: float(x.get('percentageChange', 0)))
        
        return losers[:limit]
    
    def get_most_active_by_volume(self, limit: int = 10) -> List[Dict]:
        """
        Get most active stocks by trading volume.
        
        Args:
            limit: Number of stocks to return
            
        Returns:
            List of most actively traded stocks by volume
        """
        stocks = self.fetch_live_data()
        
        # Sort by totalTradeQuantity
        stocks.sort(key=lambda x: float(x.get('totalTradeQuantity', 0) or 0), reverse=True)
        
        return stocks[:limit]
    
    def get_most_active_by_value(self, limit: int = 10) -> List[Dict]:
        """
        Get most active stocks by trading value.
        
        Args:
            limit: Number of stocks to return
            
        Returns:
            List of most actively traded stocks by value
        """
        stocks = self.fetch_live_data()
        
        # Sort by totalTradeValue
        stocks.sort(key=lambda x: float(x.get('totalTradeValue', 0) or 0), reverse=True)
        
        return stocks[:limit]
    
    def get_most_active_by_transactions(self, limit: int = 10) -> List[Dict]:
        """
        Get most active stocks by number of transactions.
        
        Args:
            limit: Number of stocks to return
            
        Returns:
            List of most actively traded stocks by transaction count
        """
        stocks = self.fetch_live_data()
        
        # Sort by totalTransactions
        stocks.sort(key=lambda x: int(x.get('totalTransactions', 0) or 0), reverse=True)
        
        return stocks[:limit]
    
    def get_52_week_high(self, limit: int = 10) -> List[Dict]:
        """
        Get stocks near or at 52-week high.
        
        Args:
            limit: Number of stocks to return
            
        Returns:
            List of stocks at 52-week high
        """
        stocks = self.fetch_live_data()
        
        # Filter stocks where lastTradedPrice is close to or at fiftyTwoWeekHigh
        near_high = []
        for stock in stocks:
            ltp = float(stock.get('lastTradedPrice', 0) or 0)
            high_52 = float(stock.get('fiftyTwoWeekHigh', 0) or 0)
            
            if high_52 > 0 and ltp > 0:
                # Calculate percentage from 52-week high
                pct_from_high = ((ltp - high_52) / high_52) * 100
                stock['percentageFrom52WeekHigh'] = round(pct_from_high, 2)
                near_high.append(stock)
        
        # Sort by how close to 52-week high (closest to 0 or positive)
        near_high.sort(key=lambda x: x.get('percentageFrom52WeekHigh', -100), reverse=True)
        
        return near_high[:limit]
    
    def get_52_week_low(self, limit: int = 10) -> List[Dict]:
        """
        Get stocks near or at 52-week low.
        
        Args:
            limit: Number of stocks to return
            
        Returns:
            List of stocks at 52-week low
        """
        stocks = self.fetch_live_data()
        
        # Filter stocks where lastTradedPrice is close to or at fiftyTwoWeekLow
        near_low = []
        for stock in stocks:
            ltp = float(stock.get('lastTradedPrice', 0) or 0)
            low_52 = float(stock.get('fiftyTwoWeekLow', 0) or 0)
            
            if low_52 > 0 and ltp > 0:
                # Calculate percentage from 52-week low
                pct_from_low = ((ltp - low_52) / low_52) * 100
                stock['percentageFrom52WeekLow'] = round(pct_from_low, 2)
                near_low.append(stock)
        
        # Sort by how close to 52-week low (closest to 0)
        near_low.sort(key=lambda x: abs(x.get('percentageFrom52WeekLow', 100)))
        
        return near_low[:limit]
    
    def get_by_sector(self, sector: str) -> List[Dict]:
        """
        Get all stocks in a specific sector.
        
        Args:
            sector: Sector name
            
        Returns:
            List of stocks in the sector
        """
        stocks = self.fetch_live_data()
        
        # Filter by sector (case-insensitive)
        sector_stocks = [
            s for s in stocks 
            if s.get('sector', '').lower() == sector.lower()
        ]
        
        # Sort by percentageChange descending
        sector_stocks.sort(key=lambda x: float(x.get('percentageChange', 0) or 0), reverse=True)
        
        return sector_stocks
    
    def get_market_summary(self) -> Dict:
        """
        Get overall market summary statistics.
        
        Returns:
            Dictionary with market summary data
        """
        stocks = self.fetch_live_data()
        
        if not stocks:
            return {}
        
        total_stocks = len(stocks)
        advancing = len([s for s in stocks if s.get('percentageChange', 0) > 0])
        declining = len([s for s in stocks if s.get('percentageChange', 0) < 0])
        unchanged = total_stocks - advancing - declining
        
        total_turnover = sum(float(s.get('totalTradeValue', 0) or 0) for s in stocks)
        total_volume = sum(float(s.get('totalTradeQuantity', 0) or 0) for s in stocks)
        total_transactions = sum(int(s.get('totalTransactions', 0) or 0) for s in stocks)
        
        return {
            "totalStocks": total_stocks,
            "advancing": advancing,
            "declining": declining,
            "unchanged": unchanged,
            "totalTurnover": round(total_turnover, 2),
            "totalVolume": int(total_volume),
            "totalTransactions": total_transactions,
            "timestamp": datetime.now().isoformat()
        }
