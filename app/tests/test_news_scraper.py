"""Tests for news scraper service."""

import unittest
from unittest.mock import patch, MagicMock
from app.services.news_scraper import NewsScraperService


class TestNewsScraperService(unittest.TestCase):
    """Test cases for news scraper service."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = NewsScraperService()
    
    def test_base_url_configuration(self):
        """Test that base URLs are configured correctly."""
        self.assertEqual(self.service.BASE_URL, "https://www.sharesansar.com")
        self.assertEqual(self.service.NEWS_PAGE_URL, "https://www.sharesansar.com/news-page")
    
    def test_headers_configured(self):
        """Test that request headers are configured."""
        self.assertIn('User-Agent', self.service.headers)
        self.assertTrue(len(self.service.headers['User-Agent']) > 0)
    
    @patch('app.services.news_scraper.requests.get')
    def test_scrape_news_success(self, mock_get):
        """Test successful news scraping."""
        # Mock HTML response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html>
            <div class="featured-news-item">
                <a href="/news/test-news-1">Test News 1</a>
                <span class="textOrg">2025-10-08</span>
                <span class="category">Finance</span>
                <p class="short-desc">Test description 1</p>
            </div>
            <div class="featured-news-item">
                <a href="/news/test-news-2">Test News 2</a>
                <span class="textOrg">2025-10-07</span>
                <span class="category">Banking</span>
                <p class="short-desc">Test description 2</p>
            </div>
        </html>
        '''
        mock_get.return_value = mock_response
        
        result = self.service.scrape_news(limit=10, max_pages=1)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['title'], 'Test News 1')
        self.assertEqual(result[0]['category'], 'Finance')
        self.assertIn('sharesansar.com/news/test-news-1', result[0]['link'])
    
    @patch('app.services.news_scraper.requests.get')
    def test_scrape_news_with_limit(self, mock_get):
        """Test that limit parameter works correctly."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html>
            <div class="featured-news-item">
                <a href="/news/1">News 1</a>
                <span class="textOrg">2025-10-08</span>
                <span class="category">Finance</span>
                <p class="short-desc">Desc 1</p>
            </div>
            <div class="featured-news-item">
                <a href="/news/2">News 2</a>
                <span class="textOrg">2025-10-08</span>
                <span class="category">Banking</span>
                <p class="short-desc">Desc 2</p>
            </div>
            <div class="featured-news-item">
                <a href="/news/3">News 3</a>
                <span class="textOrg">2025-10-08</span>
                <span class="category">Market</span>
                <p class="short-desc">Desc 3</p>
            </div>
        </html>
        '''
        mock_get.return_value = mock_response
        
        result = self.service.scrape_news(limit=2, max_pages=1)
        
        self.assertEqual(len(result), 2)
    
    @patch('app.services.news_scraper.requests.get')
    def test_scrape_news_request_failure(self, mock_get):
        """Test handling of request failures."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = self.service.scrape_news(limit=10, max_pages=1)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)
    
    @patch('app.services.news_scraper.requests.get')
    def test_scrape_news_exception_handling(self, mock_get):
        """Test handling of exceptions during scraping."""
        mock_get.side_effect = Exception("Connection error")
        
        result = self.service.scrape_news(limit=10, max_pages=1)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)
    
    @patch('app.services.news_scraper.requests.get')
    def test_find_next_page(self, mock_get):
        """Test pagination next page detection."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html>
            <div class="featured-news-item">
                <a href="/news/1">News 1</a>
                <span class="textOrg">2025-10-08</span>
                <span class="category">Finance</span>
                <p class="short-desc">Desc 1</p>
            </div>
            <a rel="next" href="/news-page?page=2">Next</a>
        </html>
        '''
        mock_get.return_value = mock_response
        
        # This will try to get page 2 but we'll limit to 1 page
        result = self.service.scrape_news(limit=100, max_pages=1)
        
        self.assertEqual(len(result), 1)
        # Verify only one request was made (max_pages=1)
        self.assertEqual(mock_get.call_count, 1)


if __name__ == "__main__":
    unittest.main()
