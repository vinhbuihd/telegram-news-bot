"""
Configuration file for the Telegram News Bot
For GitHub Actions: Use environment variables (Secrets)
"""
import os
from dataclasses import dataclass
from typing import List

@dataclass
class Config:
    # Telegram Bot Token - Set in GitHub Secrets
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # Your Telegram User ID - Set in GitHub Secrets
    TELEGRAM_USER_ID: int = int(os.getenv("TELEGRAM_USER_ID", "0"))
    
    # Google Gemini API Key - Set in GitHub Secrets
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Schedule time (for reference, actual schedule is in GitHub Actions workflow)
    SCHEDULE_HOUR: int = 7
    SCHEDULE_MINUTE: int = 0
    
    # RSS Feed sources - All free and reputable
    RSS_FEEDS: List[dict] = None
    
    def __post_init__(self):
        self.RSS_FEEDS = [
            # World News
            {"name": "Reuters World", "url": "https://feeds.reuters.com/Reuters/worldNews", "region": "World"},
            {"name": "Reuters Politics", "url": "https://feeds.reuters.com/Reuters/PoliticsNews", "region": "US"},
            
            # Asia News
            {"name": "BBC Asia", "url": "https://feeds.bbci.co.uk/news/world/asia/rss.xml", "region": "Asia"},
            {"name": "BBC World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "region": "World"},
            
            # Financial News
            {"name": "Reuters Business", "url": "https://feeds.reuters.com/reuters/businessNews", "region": "Finance"},
            
            # Alternative sources (backup)
            {"name": "NPR World", "url": "https://feeds.npr.org/1004/rss.xml", "region": "World"},
            {"name": "The Guardian World", "url": "https://www.theguardian.com/world/rss", "region": "World"},
        ]
        
    # Keywords to filter relevant news
    def get_keywords(self):
        return [
            # Countries
            "united states", "usa", "america", "biden", "trump", "white house", "congress",
            "china", "chinese", "beijing", "xi jinping",
            "russia", "russian", "moscow", "putin", "kremlin",
            "japan", "japanese", "tokyo", "kishida",
            
            # Financial
            "oil price", "crude oil", "opec", "gold price", "gold market",
            "real estate", "property market", "housing",
            "stock market", "federal reserve", "interest rate",
            "economy", "inflation", "recession",
            
            # Geopolitics
            "sanctions", "trade war", "tariff", "diplomacy",
            "military", "defense", "nato", "war", "conflict"
        ]

config = Config()
