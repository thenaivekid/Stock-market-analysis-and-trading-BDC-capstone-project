"""Tests for main application and health endpoints."""

import unittest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestMainApp(unittest.TestCase):
    """Test cases for main application endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct response."""
        response = client.get("/")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("NEPSE Data API", data["message"])
        self.assertEqual(data["docs"], "/docs")
    
    def test_health_check_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "nepse-scraper")
        self.assertEqual(data["version"], "1.0.0")
    
    def test_docs_available(self):
        """Test that API documentation is available."""
        response = client.get("/docs")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
    
    def test_openapi_json_available(self):
        """Test that OpenAPI JSON schema is available."""
        response = client.get("/openapi.json")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["info"]["title"], "NEPSE Data API")
        self.assertEqual(data["info"]["version"], "1.0.0")


if __name__ == "__main__":
    unittest.main()
