"""
Database module for storing news history
"""
import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from contextlib import contextmanager

class NewsDatabase:
    def __init__(self, db_path: str = "news_history.db"):
        self.db_path = db_path
        self._init_db()
    
    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_db(self):
        """Initialize database tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # News articles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS news_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    link TEXT UNIQUE NOT NULL,
                    source TEXT,
                    region TEXT,
                    published_date TEXT,
                    summary TEXT,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Daily reports table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_date DATE UNIQUE NOT NULL,
                    news_summary TEXT,
                    political_analysis TEXT,
                    financial_predictions TEXT,
                    full_report TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Sent messages log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sent_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message_type TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN DEFAULT TRUE
                )
            """)
            
            conn.commit()
    
    def save_article(self, title: str, link: str, source: str, 
                     region: str, published_date: str, summary: str = None) -> bool:
        """Save a news article, returns True if new article"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO news_articles (title, link, source, region, published_date, summary)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (title, link, source, region, published_date, summary))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                # Article already exists
                return False
    
    def get_recent_articles(self, hours: int = 24) -> List[Dict]:
        """Get articles from the last N hours"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cutoff = datetime.now() - timedelta(hours=hours)
            cursor.execute("""
                SELECT * FROM news_articles 
                WHERE collected_at >= ?
                ORDER BY collected_at DESC
            """, (cutoff.isoformat(),))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_unsent_articles(self) -> List[Dict]:
        """Get articles that haven't been included in a report yet"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Get articles collected since the last report
            cursor.execute("""
                SELECT na.* FROM news_articles na
                LEFT JOIN daily_reports dr ON DATE(na.collected_at) = dr.report_date
                WHERE dr.id IS NULL
                ORDER BY na.collected_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def save_daily_report(self, report_date: str, news_summary: str,
                          political_analysis: str, financial_predictions: str,
                          full_report: str) -> bool:
        """Save daily analysis report"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO daily_reports 
                    (report_date, news_summary, political_analysis, financial_predictions, full_report)
                    VALUES (?, ?, ?, ?, ?)
                """, (report_date, news_summary, political_analysis, financial_predictions, full_report))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error saving report: {e}")
                return False
    
    def get_report_by_date(self, date: str) -> Optional[Dict]:
        """Get report for a specific date"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM daily_reports WHERE report_date = ?
            """, (date,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_recent_reports(self, days: int = 7) -> List[Dict]:
        """Get reports from the last N days"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM daily_reports 
                ORDER BY report_date DESC
                LIMIT ?
            """, (days,))
            return [dict(row) for row in cursor.fetchall()]
    
    def log_sent_message(self, user_id: int, message_type: str, success: bool = True):
        """Log a sent message"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sent_messages (user_id, message_type, success)
                VALUES (?, ?, ?)
            """, (user_id, message_type, success))
            conn.commit()
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM news_articles")
            total_articles = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM daily_reports")
            total_reports = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM sent_messages WHERE success = 1")
            total_sent = cursor.fetchone()[0]
            
            return {
                "total_articles": total_articles,
                "total_reports": total_reports,
                "total_messages_sent": total_sent
            }


# Singleton instance
db = NewsDatabase()
