"""Scraper service for web scraping operations."""

from typing import Dict, List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os


class ScraperService:
    """Service for web scraping operations using Selenium."""
    
    def __init__(self):
        self.selenium_host = os.getenv("SELENIUM_HOST", "localhost")
        self.selenium_port = os.getenv("SELENIUM_PORT", "4444")
        self.selenium_url = f"http://{self.selenium_host}:{self.selenium_port}/wd/hub"
    
    def _get_driver(self) -> webdriver.Remote:
        """Create and configure a Selenium WebDriver instance."""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        return webdriver.Remote(
            command_executor=self.selenium_url,
            options=options
        )
    
    def scrape_floorsheet(self, symbol: str) -> Dict[str, List]:
        """
        Scrape floorsheet data for a given stock symbol.
        
        Args:
            symbol: Stock symbol to scrape (e.g., "NABIL")
        
        Returns:
            Dictionary containing headers and rows of the floorsheet table
        
        Raises:
            Exception: If scraping fails
        """
        driver = self._get_driver()
        wait = WebDriverWait(driver, 30)
        
        try:
            # Navigate to the page
            driver.get(f"https://chukul.com/nepse-charts?symbol={symbol}")
            
            # Click expand button
            expand_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Expand')]"))
            )
            expand_btn.click()
            
            # Click floorsheet tab
            floorsheet_tab = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'q-tab__label') and contains(., 'Floorsheet')]"))
            )
            floorsheet_tab.click()
            
            # Wait for table to load
            table = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.q-table__middle.scroll table.q-table"))
            )
            
            # Extract headers
            headers = [th.text.strip() for th in table.find_elements(By.XPATH, ".//thead/tr/th")]
            
            # Extract rows
            rows = []
            for tr in table.find_elements(By.XPATH, ".//tbody/tr"):
                cols = [td.text.strip() for td in tr.find_elements(By.TAG_NAME, "td")]
                if cols:
                    rows.append(cols)
            
            return {"headers": headers, "rows": rows}
        
        finally:
            driver.quit()
