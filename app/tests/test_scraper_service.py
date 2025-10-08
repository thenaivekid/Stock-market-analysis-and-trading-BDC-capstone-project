"""Tests for scraper service."""

import unittest
from unittest.mock import patch, MagicMock
from app.services.scraper import ScraperService


class TestScraperService(unittest.TestCase):
    """Test cases for scraper service."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = ScraperService()
    
    def test_selenium_url_default(self):
        """Test default Selenium URL construction."""
        # In Docker, env vars are set, so we get selenium-chrome
        # This test checks that URL is constructed properly from env or defaults
        expected_host = self.service.selenium_host
        expected_port = self.service.selenium_port
        expected_url = f"http://{expected_host}:{expected_port}/wd/hub"
        self.assertEqual(self.service.selenium_url, expected_url)
    
    @patch.dict('os.environ', {'SELENIUM_HOST': 'selenium-chrome', 'SELENIUM_PORT': '4444'})
    def test_selenium_url_from_env(self):
        """Test Selenium URL construction from environment variables."""
        service = ScraperService()
        self.assertEqual(service.selenium_url, "http://selenium-chrome:4444/wd/hub")
    
    @patch('app.services.scraper.webdriver.Remote')
    def test_get_driver_configuration(self, mock_webdriver):
        """Test that driver is configured correctly."""
        mock_driver = MagicMock()
        mock_webdriver.return_value = mock_driver
        
        driver = self.service._get_driver()
        
        mock_webdriver.assert_called_once()
        call_args = mock_webdriver.call_args
        
        # Check that options are passed
        self.assertIn('options', call_args.kwargs)
        self.assertEqual(call_args.kwargs['command_executor'], self.service.selenium_url)
    
    @patch('app.services.scraper.webdriver.Remote')
    @patch('app.services.scraper.WebDriverWait')
    def test_scrape_floorsheet_success(self, mock_wait, mock_webdriver):
        """Test successful floorsheet scraping."""
        # Mock driver and elements
        mock_driver = MagicMock()
        mock_webdriver.return_value = mock_driver
        
        # Mock wait and elements
        mock_wait_instance = MagicMock()
        mock_wait.return_value = mock_wait_instance
        
        # Mock expand button
        mock_expand_btn = MagicMock()
        # Mock floorsheet tab
        mock_floorsheet_tab = MagicMock()
        # Mock table
        mock_table = MagicMock()
        
        # Mock table headers
        mock_header1 = MagicMock()
        mock_header1.text = "Time"
        mock_header2 = MagicMock()
        mock_header2.text = "Symbol"
        mock_table.find_elements.return_value = [mock_header1, mock_header2]
        
        # Set up wait.until to return mocked elements in sequence
        mock_wait_instance.until.side_effect = [
            mock_expand_btn,
            mock_floorsheet_tab,
            mock_table
        ]
        
        # Mock table rows
        mock_row = MagicMock()
        mock_cell1 = MagicMock()
        mock_cell1.text = "10:00:00"
        mock_cell2 = MagicMock()
        mock_cell2.text = "NABIL"
        mock_row.find_elements.return_value = [mock_cell1, mock_cell2]
        
        def find_elements_side_effect(by, value):
            if "thead" in value:
                return [mock_header1, mock_header2]
            elif "tbody" in value:
                return [mock_row]
            return []
        
        mock_table.find_elements.side_effect = find_elements_side_effect
        
        result = self.service.scrape_floorsheet("NABIL")
        
        # Verify result structure
        self.assertIn("headers", result)
        self.assertIn("rows", result)
        self.assertIsInstance(result["headers"], list)
        self.assertIsInstance(result["rows"], list)
        
        # Verify driver.quit was called
        mock_driver.quit.assert_called_once()
    
    @patch('app.services.scraper.webdriver.Remote')
    def test_scrape_floorsheet_driver_quits_on_error(self, mock_webdriver):
        """Test that driver quits even when error occurs."""
        mock_driver = MagicMock()
        mock_webdriver.return_value = mock_driver
        mock_driver.get.side_effect = Exception("Connection error")
        
        with self.assertRaises(Exception):
            self.service.scrape_floorsheet("NABIL")
        
        # Ensure driver.quit is called even on error
        mock_driver.quit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
