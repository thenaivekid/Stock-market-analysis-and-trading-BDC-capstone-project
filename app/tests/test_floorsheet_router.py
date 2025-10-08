"""Tests for floorsheet router."""

import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestFloorsheetRouter(unittest.TestCase):
    """Test cases for floorsheet endpoints."""
    
    @patch('app.routers.floorsheet.scraper_service.scrape_floorsheet')
    def test_get_floorsheet_success(self, mock_scrape):
        """Test successful floorsheet scraping."""
        # Mock the scraper service response
        mock_scrape.return_value = {
            "headers": ["Time", "Contract No", "Symbol", "Buyer", "Seller", "Quantity", "Rate", "Amount"],
            "rows": [
                ["10:00:00", "12345", "NABIL", "Buyer1", "Seller1", "100", "1200", "120000"],
                ["10:01:00", "12346", "NABIL", "Buyer2", "Seller2", "50", "1201", "60050"]
            ]
        }
        
        response = client.post(
            "/api/floorsheet/",
            json={"symbol": "NABIL"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["symbol"], "NABIL")
        self.assertIn("headers", data)
        self.assertIn("rows", data)
        self.assertEqual(len(data["rows"]), 2)
        mock_scrape.assert_called_once_with("NABIL")
    
    @patch('app.routers.floorsheet.scraper_service.scrape_floorsheet')
    def test_get_floorsheet_lowercase_symbol(self, mock_scrape):
        """Test that lowercase symbols are converted to uppercase."""
        mock_scrape.return_value = {
            "headers": ["Time", "Symbol"],
            "rows": [["10:00:00", "ADBL"]]
        }
        
        response = client.post(
            "/api/floorsheet/",
            json={"symbol": "adbl"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["symbol"], "ADBL")
        mock_scrape.assert_called_once_with("ADBL")
    
    @patch('app.routers.floorsheet.scraper_service.scrape_floorsheet')
    def test_get_floorsheet_scraper_error(self, mock_scrape):
        """Test handling of scraper errors."""
        mock_scrape.side_effect = Exception("Selenium timeout")
        
        response = client.post(
            "/api/floorsheet/",
            json={"symbol": "INVALID"}
        )
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn("detail", data)
        self.assertIn("Failed to scrape", data["detail"])
    
    def test_get_floorsheet_missing_symbol(self):
        """Test validation error when symbol is missing."""
        response = client.post(
            "/api/floorsheet/",
            json={}
        )
        
        self.assertEqual(response.status_code, 422)
    
    def test_get_floorsheet_empty_symbol(self):
        """Test validation error when symbol is empty."""
        response = client.post(
            "/api/floorsheet/",
            json={"symbol": ""}
        )
        
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
