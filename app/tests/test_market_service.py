"""Tests for market data service."""

import unittest
from unittest.mock import patch, MagicMock
from app.services.market_data import MarketDataService


class TestMarketDataService(unittest.TestCase):
    """Test cases for market data service."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = MarketDataService()
        self.sample_stocks = [
            {
                'symbol': 'NABIL',
                'securityName': 'Nabil Bank',
                'sector': 'Commercial Banks',
                'lastTradedPrice': 1200.0,
                'percentageChange': 5.5,
                'change': 62.5,
                'openPrice': 1150.0,
                'highPrice': 1210.0,
                'lowPrice': 1145.0,
                'previousClose': 1137.5,
                'totalTransactions': 500,
                'totalTradeQuantity': 10000.0,
                'totalTradeValue': 12000000.0,
                'lastTradedVolume': 100,
                'fiftyTwoWeekHigh': 1300.0,
                'fiftyTwoWeekLow': 900.0
            },
            {
                'symbol': 'ADBL',
                'securityName': 'Agriculture Development Bank',
                'sector': 'Development Banks',
                'lastTradedPrice': 300.0,
                'percentageChange': -3.2,
                'change': -10.0,
                'openPrice': 310.0,
                'highPrice': 312.0,
                'lowPrice': 298.0,
                'previousClose': 310.0,
                'totalTransactions': 800,
                'totalTradeQuantity': 50000.0,
                'totalTradeValue': 15000000.0,
                'lastTradedVolume': 200,
                'fiftyTwoWeekHigh': 400.0,
                'fiftyTwoWeekLow': 250.0
            },
            {
                'symbol': 'NMB',
                'securityName': 'NMB Bank',
                'sector': 'Commercial Banks',
                'lastTradedPrice': 450.0,
                'percentageChange': 0.0,
                'change': 0.0,
                'openPrice': 450.0,
                'highPrice': 455.0,
                'lowPrice': 448.0,
                'previousClose': 450.0,
                'totalTransactions': 200,
                'totalTradeQuantity': 5000.0,
                'totalTradeValue': 2250000.0,
                'lastTradedVolume': 50,
                'fiftyTwoWeekHigh': 500.0,
                'fiftyTwoWeekLow': 400.0
            }
        ]
    
    @patch('app.services.market_data.requests.get')
    def test_fetch_live_data_success(self, mock_get):
        """Test successful fetch of live data."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'success': True,
            'data': self.sample_stocks
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = self.service.fetch_live_data()
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['symbol'], 'NABIL')
        mock_get.assert_called_once()
    
    @patch('app.services.market_data.requests.get')
    def test_fetch_live_data_api_failure(self, mock_get):
        """Test handling of API failure."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'success': False}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        with self.assertRaises(Exception) as context:
            self.service.fetch_live_data()
        
        self.assertIn("Invalid or unsuccessful", str(context.exception))
    
    @patch.object(MarketDataService, 'fetch_live_data')
    def test_get_top_gainers(self, mock_fetch):
        """Test getting top gainers."""
        mock_fetch.return_value = self.sample_stocks
        
        result = self.service.get_top_gainers(limit=2)
        
        self.assertEqual(len(result), 1)  # Only 1 gainer in sample data
        self.assertEqual(result[0]['symbol'], 'NABIL')
        self.assertGreater(result[0]['percentageChange'], 0)
    
    @patch.object(MarketDataService, 'fetch_live_data')
    def test_get_top_losers(self, mock_fetch):
        """Test getting top losers."""
        mock_fetch.return_value = self.sample_stocks
        
        result = self.service.get_top_losers(limit=2)
        
        self.assertEqual(len(result), 1)  # Only 1 loser in sample data
        self.assertEqual(result[0]['symbol'], 'ADBL')
        self.assertLess(result[0]['percentageChange'], 0)
    
    @patch.object(MarketDataService, 'fetch_live_data')
    def test_get_most_active_by_volume(self, mock_fetch):
        """Test getting most active stocks by volume."""
        mock_fetch.return_value = self.sample_stocks
        
        result = self.service.get_most_active_by_volume(limit=2)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['symbol'], 'ADBL')  # Highest volume
        self.assertGreater(result[0]['totalTradeQuantity'], result[1]['totalTradeQuantity'])
    
    @patch.object(MarketDataService, 'fetch_live_data')
    def test_get_most_active_by_value(self, mock_fetch):
        """Test getting most active stocks by value."""
        mock_fetch.return_value = self.sample_stocks
        
        result = self.service.get_most_active_by_value(limit=2)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['symbol'], 'ADBL')  # Highest value
        self.assertGreater(result[0]['totalTradeValue'], result[1]['totalTradeValue'])
    
    @patch.object(MarketDataService, 'fetch_live_data')
    def test_get_most_active_by_transactions(self, mock_fetch):
        """Test getting most active stocks by transactions."""
        mock_fetch.return_value = self.sample_stocks
        
        result = self.service.get_most_active_by_transactions(limit=2)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['symbol'], 'ADBL')  # Highest transactions
        self.assertGreater(result[0]['totalTransactions'], result[1]['totalTransactions'])
    
    @patch.object(MarketDataService, 'fetch_live_data')
    def test_get_52_week_high(self, mock_fetch):
        """Test getting stocks near 52-week high."""
        mock_fetch.return_value = self.sample_stocks
        
        result = self.service.get_52_week_high(limit=3)
        
        self.assertEqual(len(result), 3)
        self.assertIn('percentageFrom52WeekHigh', result[0])
    
    @patch.object(MarketDataService, 'fetch_live_data')
    def test_get_52_week_low(self, mock_fetch):
        """Test getting stocks near 52-week low."""
        mock_fetch.return_value = self.sample_stocks
        
        result = self.service.get_52_week_low(limit=3)
        
        self.assertEqual(len(result), 3)
        self.assertIn('percentageFrom52WeekLow', result[0])
    
    @patch.object(MarketDataService, 'fetch_live_data')
    def test_get_by_sector(self, mock_fetch):
        """Test getting stocks by sector."""
        mock_fetch.return_value = self.sample_stocks
        
        result = self.service.get_by_sector('Commercial Banks')
        
        self.assertEqual(len(result), 2)
        for stock in result:
            self.assertEqual(stock['sector'], 'Commercial Banks')
    
    @patch.object(MarketDataService, 'fetch_live_data')
    def test_get_by_sector_case_insensitive(self, mock_fetch):
        """Test that sector search is case-insensitive."""
        mock_fetch.return_value = self.sample_stocks
        
        result = self.service.get_by_sector('commercial banks')
        
        self.assertEqual(len(result), 2)
    
    @patch.object(MarketDataService, 'fetch_live_data')
    def test_get_market_summary(self, mock_fetch):
        """Test getting market summary."""
        mock_fetch.return_value = self.sample_stocks
        
        result = self.service.get_market_summary()
        
        self.assertEqual(result['totalStocks'], 3)
        self.assertEqual(result['advancing'], 1)
        self.assertEqual(result['declining'], 1)
        self.assertEqual(result['unchanged'], 1)
        self.assertIn('totalTurnover', result)
        self.assertIn('totalVolume', result)
        self.assertIn('totalTransactions', result)
        self.assertIn('timestamp', result)


if __name__ == "__main__":
    unittest.main()
