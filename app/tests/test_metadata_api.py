"""Tests for metadata API endpoints."""

import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
import pandas as pd


client = TestClient(app)


class TestMetadataAPI(unittest.TestCase):
    """Test cases for metadata API endpoints."""
    
    @patch('app.api.load_company_metadata')
    def test_get_companies(self, mock_load):
        """Test get companies endpoint."""
        # Mock the company data
        mock_df = pd.DataFrame([
            {"symbol": "NABIL", "securityName": "Nabil Bank", "sector": "Commercial Banks"},
            {"symbol": "ADBL", "securityName": "Agriculture Development Bank", "sector": "Development Banks"}
        ])
        mock_load.return_value = mock_df
        
        response = client.get("/api/metadata/companies")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["symbol"], "NABIL")
    
    @patch('app.api.load_sector_metadata')
    def test_get_sectors(self, mock_load):
        """Test get sectors endpoint."""
        # Mock the sector data
        mock_df = pd.DataFrame([
            {"sector": "Commercial Banks"},
            {"sector": "Development Banks"},
            {"sector": "Finance"}
        ])
        mock_load.return_value = mock_df
        
        response = client.get("/api/metadata/sectors")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertIn("Commercial Banks", data)
        self.assertIn("Development Banks", data)
    
    @patch('app.api.requests.get')
    @patch('app.api.save_company_metadata')
    @patch('app.api.save_sector_metadata')
    def test_update_metadata_success(self, mock_save_sector, mock_save_company, mock_get):
        """Test successful metadata update."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {"symbol": "NABIL", "securityName": "Nabil Bank", "sector": "Commercial Banks"},
                {"symbol": "ADBL", "securityName": "Agriculture Development Bank", "sector": "Development Banks"}
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        response = client.post("/api/metadata/update")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertEqual(data["companies"], 2)
        self.assertEqual(data["sectors"], 2)
        mock_save_company.assert_called_once()
        mock_save_sector.assert_called_once()
    
    @patch('app.api.requests.get')
    def test_update_metadata_api_failure(self, mock_get):
        """Test metadata update when external API fails."""
        # Mock API failure
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": False}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        response = client.post("/api/metadata/update")
        
        # The error gets caught by the general exception handler, returning 500
        self.assertEqual(response.status_code, 500)


if __name__ == "__main__":
    unittest.main()
