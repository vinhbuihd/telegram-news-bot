"""
News Collector Module - Collects news from RSS feeds
"""
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from html import unescape
import logging

from config import config
from database import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsCollector:
    def __init__(self):
        self.feeds = config.RSS_FEEDS
        self.keywords = config.get_keywords()
    
    def _clean_text(self, text: str) -> str:
        """Clean HTML and special characters from text"""
        if not text:
            return ""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Unescape HTML entities
        text = unescape(text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()
    
    def _is_relevant(self, title: str, summary: str = "") -> bool:
        """Check if article is relevant based on keywords"""
        combined = f"{title} {summary}".lower()
        return any(keyword.lower() in combined for keyword in self.keywords)
    
    def _parse_date(self, entry) -> Optional[str]:
        """Parse publication date from feed entry"""
        date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
        for field in date_fields:
            if hasattr(entry, field) and getattr(entry, field):
                try:
                    parsed = getattr(entry, field)
                    return datetime(*parsed[:6]).isoformat()
                except:
                    pass
        return datetime.now().isoformat()
    
    def collect_from_feed(self, feed_info: Dict) -> List[Dict]:
        """Collect news from a single RSS feed"""
        articles = []
        try:
            logger.info(f"Fetching: {feed_info['name']}")
            feed = feedparser.parse(feed_info['url'])
            
            if feed.bozo and feed.bozo_exception:
                logger.warning(f"Feed error for {feed_info['name']}: {feed.bozo_exception}")
            
            for entry in feed.entries[:15]:  # Limit to 15 most recent
                title = self._clean_text(entry.get('title', ''))
                summary = self._clean_text(entry.get('summary', entry.get('description', '')))
                link = entry.get('link', '')
                
                if not title or not link:
                    continue
                
                # Filter by relevance
                if not self._is_relevant(title, summary):
                    continue
                
                article = {
                    'title': title,
                    'link': link,
                    'source': feed_info['name'],
                    'region': feed_info['region'],
                    'published_date': self._parse_date(entry),
                    'summary': summary[:500] if summary else None  # Limit summary length
                }
                articles.append(article)
                
        except Exception as e:
            logger.error(f"Error collecting from {feed_info['name']}: {e}")
        
        return articles
    
    def collect_all(self) -> List[Dict]:
        """Collect news from all configured RSS feeds"""
        all_articles = []
        
        for feed_info in self.feeds:
            articles = self.collect_from_feed(feed_info)
            all_articles.extend(articles)
            logger.info(f"Collected {len(articles)} relevant articles from {feed_info['name']}")
        
        # Remove duplicates based on link
        seen_links = set()
        unique_articles = []
        for article in all_articles:
            if article['link'] not in seen_links:
                seen_links.add(article['link'])
                unique_articles.append(article)
        
        logger.info(f"Total unique relevant articles: {len(unique_articles)}")
        return unique_articles
    
    def collect_and_save(self) -> Dict:
        """Collect news and save to database"""
        articles = self.collect_all()
        
        new_count = 0
        duplicate_count = 0
        
        for article in articles:
            is_new = db.save_article(
                title=article['title'],
                link=article['link'],
                source=article['source'],
                region=article['region'],
                published_date=article['published_date'],
                summary=article['summary']
            )
            if is_new:
                new_count += 1
            else:
                duplicate_count += 1
        
        result = {
            'total_collected': len(articles),
            'new_articles': new_count,
            'duplicates': duplicate_count
        }
        
        logger.info(f"Collection result: {result}")
        return result
    
    def get_articles_for_analysis(self, hours: int = 24) -> List[Dict]:
        """Get recent articles for AI analysis"""
        return db.get_recent_articles(hours=hours)


# Create singleton instance
collector = NewsCollector()


if __name__ == "__main__":
    # Test collection
    result = collector.collect_and_save()
    print(f"Collection result: {result}")
    
    articles = collector.get_articles_for_analysis(hours=24)
    print(f"\nRecent articles for analysis: {len(articles)}")
    for article in articles[:5]:
        print(f"- {article['title'][:60]}...")
