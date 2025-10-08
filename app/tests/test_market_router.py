"""Tests for market data router."""

import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestMarketRouter(unittest.TestCase):
    """Test cases for market data endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_stocks = [
            {
                'symbol': 'NABIL',
                'securityName': 'Nabil Bank',
                'sector': 'Commercial Banks',
                'lastTradedPrice': 1200.0,
                'percentageChange': 5.5,
                'totalTradeQuantity': 10000.0,
                'totalTradeValue': 12000000.0,
                'totalTransactions': 500
            },
            {
                'symbol': 'ADBL',
                'securityName': 'Agriculture Development Bank',
                'sector': 'Development Banks',
                'lastTradedPrice': 300.0,
                'percentageChange': -3.2,
                'totalTradeQuantity': 50000.0,
                'totalTradeValue': 15000000.0,
                'totalTransactions': 800
            }
        ]
    
    @patch('app.routers.market.market_service.fetch_live_data')
    def test_get_live_data(self, mock_fetch):
        """Test get live data endpoint."""
        mock_fetch.return_value = self.sample_stocks
        
        response = client.get("/api/market/live")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['symbol'], 'NABIL')
    
    @patch('app.routers.market.market_service.get_market_summary')
    def test_get_market_summary(self, mock_summary):
        """Test market summary endpoint."""
        mock_summary.return_value = {
            'totalStocks': 100,
            'advancing': 60,
            'declining': 30,
            'unchanged': 10,
            'totalTurnover': 5000000000.0,
            'totalVolume': 10000000,
            'totalTransactions': 50000,
            'timestamp': '2025-10-08T12:00:00'
        }
        
        response = client.get("/api/market/summary")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['totalStocks'], 100)
        self.assertEqual(data['advancing'], 60)
    
    @patch('app.routers.market.market_service.get_top_gainers')
    def test_get_top_gainers(self, mock_gainers):
        """Test top gainers endpoint."""
        mock_gainers.return_value = [self.sample_stocks[0]]
        
        response = client.get("/api/market/gainers?limit=5")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['symbol'], 'NABIL')
        mock_gainers.assert_called_once_with(5)
    
    @patch('app.routers.market.market_service.get_top_losers')
    def test_get_top_losers(self, mock_losers):
        """Test top losers endpoint."""
        mock_losers.return_value = [self.sample_stocks[1]]
        
        response = client.get("/api/market/losers?limit=5")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['symbol'], 'ADBL')
        mock_losers.assert_called_once_with(5)
    
    @patch('app.routers.market.market_service.get_most_active_by_volume')
    def test_get_most_active_by_volume(self, mock_active):
        """Test most active by volume endpoint."""
        mock_active.return_value = self.sample_stocks
        
        response = client.get("/api/market/active/volume")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
    
    @patch('app.routers.market.market_service.get_most_active_by_value')
    def test_get_most_active_by_value(self, mock_active):
        """Test most active by value endpoint."""
        mock_active.return_value = self.sample_stocks
        
        response = client.get("/api/market/active/value")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
    
    @patch('app.routers.market.market_service.get_most_active_by_transactions')
    def test_get_most_active_by_transactions(self, mock_active):
        """Test most active by transactions endpoint."""
        mock_active.return_value = self.sample_stocks
        
        response = client.get("/api/market/active/transactions")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
    
    @patch('app.routers.market.market_service.get_52_week_high')
    def test_get_52_week_high(self, mock_high):
        """Test 52-week high endpoint."""
        mock_high.return_value = [self.sample_stocks[0]]
        
        response = client.get("/api/market/52week/high")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
    
    @patch('app.routers.market.market_service.get_52_week_low')
    def test_get_52_week_low(self, mock_low):
        """Test 52-week low endpoint."""
        mock_low.return_value = [self.sample_stocks[0]]
        
        response = client.get("/api/market/52week/low")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
    
    @patch('app.routers.market.market_service.get_by_sector')
    def test_get_sector_stocks(self, mock_sector):
        """Test get stocks by sector endpoint."""
        mock_sector.return_value = [self.sample_stocks[0]]
        
        response = client.get("/api/market/sector/Commercial%20Banks")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['sector'], 'Commercial Banks')
    
    @patch('app.routers.market.market_service.get_by_sector')
    def test_get_sector_stocks_not_found(self, mock_sector):
        """Test sector not found."""
        mock_sector.return_value = []
        
        response = client.get("/api/market/sector/InvalidSector")
        
        self.assertEqual(response.status_code, 404)
    
    def test_get_gainers_limit_validation(self):
        """Test limit parameter validation."""
        # Test with limit > 100
        response = client.get("/api/market/gainers?limit=150")
        self.assertEqual(response.status_code, 422)
        
        # Test with limit < 1
        response = client.get("/api/market/gainers?limit=0")
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
