"""Tests for news router."""

import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestNewsRouter(unittest.TestCase):
    """Test cases for news endpoints."""
    
    @patch('app.routers.news.news_service.scrape_news')
    def test_get_news_success(self, mock_scrape):
        """Test successful news retrieval."""
        # Mock the news scraper response
        mock_scrape.return_value = [
            {
                'title': 'NEPSE reaches new high',
                'date': '2025-10-08',
                'category': 'Market',
                'description': 'Nepal Stock Exchange index hits record high',
                'link': 'https://www.sharesansar.com/news/nepse-high'
            },
            {
                'title': 'Banking sector shows growth',
                'date': '2025-10-07',
                'category': 'Banking',
                'description': 'Commercial banks report strong quarterly results',
                'link': 'https://www.sharesansar.com/news/banking-growth'
            }
        ]
        
        response = client.get("/api/news/?limit=20")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 2)
        self.assertIn('news', data)
        self.assertEqual(len(data['news']), 2)
        self.assertEqual(data['news'][0]['title'], 'NEPSE reaches new high')
        mock_scrape.assert_called_once()
    
    @patch('app.routers.news.news_service.scrape_news')
    def test_get_news_with_limit(self, mock_scrape):
        """Test news retrieval with custom limit."""
        mock_scrape.return_value = [
            {'title': f'News {i}', 'date': '2025-10-08', 'category': 'Finance', 
             'description': f'Description {i}', 'link': f'https://example.com/news/{i}'}
            for i in range(5)
        ]
        
        response = client.get("/api/news/?limit=5&max_pages=1")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 5)
        # Verify limit and max_pages were passed to service
        mock_scrape.assert_called_once_with(limit=5, max_pages=1)
    
    @patch('app.routers.news.news_service.scrape_news')
    def test_get_news_empty_result(self, mock_scrape):
        """Test news endpoint when no news found."""
        mock_scrape.return_value = []
        
        response = client.get("/api/news/")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 0)
        self.assertEqual(len(data['news']), 0)
        self.assertIn('message', data)
    
    @patch('app.routers.news.news_service.scrape_news')
    def test_get_news_service_error(self, mock_scrape):
        """Test handling of service errors."""
        mock_scrape.side_effect = Exception("Scraping failed")
        
        response = client.get("/api/news/")
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn('detail', data)
        self.assertIn('Failed to scrape news', data['detail'])
    
    @patch('app.routers.news.news_service.scrape_news')
    def test_get_latest_news_success(self, mock_scrape):
        """Test latest news endpoint."""
        mock_scrape.return_value = [
            {
                'title': 'Latest News',
                'date': '2025-10-08',
                'category': 'Breaking',
                'description': 'Latest update',
                'link': 'https://www.sharesansar.com/news/latest'
            }
        ]
        
        response = client.get("/api/news/latest?limit=10")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
        # Verify max_pages is set to 1 for latest news
        mock_scrape.assert_called_once_with(limit=10, max_pages=1)
    
    def test_get_news_limit_validation(self):
        """Test that limit parameter is validated."""
        # Test limit too high
        response = client.get("/api/news/?limit=200")
        self.assertEqual(response.status_code, 422)
        
        # Test limit too low
        response = client.get("/api/news/?limit=0")
        self.assertEqual(response.status_code, 422)
    
    def test_get_latest_news_limit_validation(self):
        """Test latest news limit validation."""
        # Test limit too high
        response = client.get("/api/news/latest?limit=100")
        self.assertEqual(response.status_code, 422)
        
        # Test limit too low
        response = client.get("/api/news/latest?limit=0")
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
