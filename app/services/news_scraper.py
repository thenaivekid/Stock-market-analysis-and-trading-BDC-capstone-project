"""News scraping service for ShareSansar."""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class NewsScraperService:
    """Service for scraping news from ShareSansar."""
    
    BASE_URL = "https://www.sharesansar.com"
    NEWS_PAGE_URL = f"{BASE_URL}/news-page"
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def scrape_news(self, limit: Optional[int] = None, max_pages: int = 5) -> List[Dict[str, str]]:
        """
        Scrape news from ShareSansar.
        
        Args:
            limit: Maximum number of news items to return
            max_pages: Maximum number of pages to scrape
        
        Returns:
            List of news items with title, date, category, description, and link
        """
        all_news = []
        url = self.NEWS_PAGE_URL
        pages_scraped = 0
        
        while url and pages_scraped < max_pages:
            try:
                logger.info(f"Scraping page: {url}")
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code != 200:
                    logger.error(f"Failed to fetch {url}: Status {response.status_code}")
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try multiple selectors to find news items
                news_items = self._extract_news_items(soup)
                
                all_news.extend(news_items)
                pages_scraped += 1
                
                # Check if we've reached the limit
                if limit and len(all_news) >= limit:
                    all_news = all_news[:limit]
                    break
                
                # Find next page link
                url = self._find_next_page(soup)
                
            except Exception as e:
                logger.error(f"Error scraping page {url}: {str(e)}")
                break
        
        return all_news
    
    def _extract_news_items(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract news items from BeautifulSoup object."""
        news_items = []
        
        # Try different selectors based on ShareSansar's structure
        # Method 1: Look for featured-news-item divs
        featured_items = soup.find_all('div', class_='featured-news-item')
        
        if featured_items:
            news_items = self._parse_featured_items(featured_items)
        else:
            # Method 2: Look for news-item class
            news_divs = soup.find_all('div', class_='news-item')
            if news_divs:
                news_items = self._parse_news_divs(news_divs)
            else:
                # Method 3: Look for article tags
                articles = soup.find_all('article')
                if articles:
                    news_items = self._parse_articles(articles)
                else:
                    # Method 4: Fallback - find links with substantial text
                    news_items = self._parse_links_fallback(soup)
        
        return news_items
    
    def _parse_featured_items(self, items) -> List[Dict[str, str]]:
        """Parse featured news items."""
        news_list = []
        for item in items:
            try:
                title_tag = item.find('a')
                title = title_tag.text.strip() if title_tag else 'N/A'
                link = self.BASE_URL + title_tag.get('href', '') if title_tag and title_tag.get('href') else ''
                
                date_tag = item.find('span', class_='textOrg')
                date_text = date_tag.text.strip() if date_tag else 'N/A'
                
                category_tag = item.find('span', class_='category')
                category_text = category_tag.text.strip() if category_tag else 'N/A'
                
                desc_tag = item.find('p', class_='short-desc')
                desc_text = desc_tag.text.strip() if desc_tag else ''
                
                news_list.append({
                    'title': title,
                    'date': date_text,
                    'category': category_text,
                    'description': desc_text,
                    'link': link
                })
            except Exception as e:
                logger.warning(f"Error parsing featured item: {str(e)}")
                continue
        
        return news_list
    
    def _parse_news_divs(self, divs) -> List[Dict[str, str]]:
        """Parse news-item divs."""
        news_list = []
        for div in divs:
            try:
                title_tag = div.find('h2') or div.find('h3') or div.find('a')
                title = title_tag.text.strip() if title_tag else 'N/A'
                
                link_tag = div.find('a')
                link = self.BASE_URL + link_tag.get('href', '') if link_tag and link_tag.get('href') else ''
                
                date_tag = div.find('time') or div.find('span', class_=['date', 'textOrg'])
                date_text = date_tag.text.strip() if date_tag else 'N/A'
                
                category_tag = div.find('span', class_='category') or div.find('a', class_='category')
                category_text = category_tag.text.strip() if category_tag else 'N/A'
                
                desc_tag = div.find('p')
                desc_text = desc_tag.text.strip() if desc_tag else ''
                
                news_list.append({
                    'title': title,
                    'date': date_text,
                    'category': category_text,
                    'description': desc_text,
                    'link': link
                })
            except Exception as e:
                logger.warning(f"Error parsing news div: {str(e)}")
                continue
        
        return news_list
    
    def _parse_articles(self, articles) -> List[Dict[str, str]]:
        """Parse article tags."""
        news_list = []
        for article in articles:
            try:
                title_tag = article.find('h2') or article.find('h3') or article.find('a')
                title = title_tag.text.strip() if title_tag else 'N/A'
                
                link_tag = article.find('a')
                link = self.BASE_URL + link_tag.get('href', '') if link_tag and link_tag.get('href') else ''
                
                date_tag = article.find('time') or article.find('span', class_=['date', 'textOrg'])
                date_text = date_tag.get('datetime', date_tag.text.strip()) if date_tag else 'N/A'
                
                category_tag = article.find('span', class_='category') or article.find('a', class_='category')
                category_text = category_tag.text.strip() if category_tag else 'N/A'
                
                desc_tag = article.find('p')
                desc_text = desc_tag.text.strip() if desc_tag else ''
                
                news_list.append({
                    'title': title,
                    'date': date_text,
                    'category': category_text,
                    'description': desc_text,
                    'link': link
                })
            except Exception as e:
                logger.warning(f"Error parsing article: {str(e)}")
                continue
        
        return news_list
    
    def _parse_links_fallback(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Fallback method: find links with substantial text."""
        news_list = []
        links = soup.find_all('a', href=True)
        
        for link in links:
            try:
                title = link.text.strip()
                # Only consider links with substantial text (likely titles)
                if len(title) < 20 or len(title) > 200:
                    continue
                
                href = link.get('href', '')
                if not href or href.startswith('#'):
                    continue
                
                news_link = self.BASE_URL + href if href.startswith('/') else href
                
                # Try to find date and category in parent elements
                parent = link.find_parent(['div', 'article', 'li'])
                
                date_tag = parent.find('span', class_='textOrg') if parent else None
                date_text = date_tag.text.strip() if date_tag else 'N/A'
                
                category_tag = parent.find('span', class_='category') if parent else None
                category_text = category_tag.text.strip() if category_tag else 'N/A'
                
                desc_tag = parent.find('p') if parent else None
                desc_text = desc_tag.text.strip() if desc_tag else ''
                
                news_list.append({
                    'title': title,
                    'date': date_text,
                    'category': category_text,
                    'description': desc_text,
                    'link': news_link
                })
            except Exception as e:
                continue
        
        return news_list
    
    def _find_next_page(self, soup: BeautifulSoup) -> Optional[str]:
        """Find the next page URL."""
        # Try different selectors for pagination
        next_button = soup.find('a', rel='next')
        if not next_button:
            next_button = soup.find('a', class_='next')
        if not next_button:
            next_button = soup.find('a', string='Next')
        if not next_button:
            # Look for pagination links
            pagination = soup.find('div', class_='pagination') or soup.find('ul', class_='pagination')
            if pagination:
                next_button = pagination.find('a', string='›') or pagination.find('a', string='Next')
        
        if next_button and next_button.get('href'):
            href = next_button['href']
            return self.BASE_URL + href if href.startswith('/') else href
        
        return None
