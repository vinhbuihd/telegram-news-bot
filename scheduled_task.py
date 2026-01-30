"""
GitHub Actions Scheduled Task Script
Runs daily to collect news and send report via Telegram
"""
import asyncio
import logging
from datetime import datetime
import sys
import os

from telegram import Bot
from config import config
from news_collector import collector
from ai_analyzer import analyzer

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def send_telegram_message(text: str, chat_id: int):
    """Send message via Telegram Bot API"""
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
    
    # Split long messages (Telegram limit is 4096 chars)
    if len(text) > 4000:
        parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for i, part in enumerate(parts):
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=part,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.warning(f"Markdown failed, sending plain text: {e}")
                await bot.send_message(
                    chat_id=chat_id,
                    text=part
                )
    else:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.warning(f"Markdown failed, sending plain text: {e}")
            await bot.send_message(
                chat_id=chat_id,
                text=text
            )


async def run_scheduled_task():
    """Main scheduled task function"""
    logger.info("="*50)
    logger.info(f"Starting scheduled task at {datetime.now()}")
    
    # Validate config
    if not config.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not configured!")
        sys.exit(1)
    
    if config.TELEGRAM_USER_ID == 0:
        logger.error("TELEGRAM_USER_ID not configured!")
        sys.exit(1)
    
    if not config.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not configured!")
        sys.exit(1)
    
    try:
        # Step 1: Collect news
        logger.info("Step 1: Collecting news...")
        collection_result = collector.collect_and_save()
        logger.info(f"Collected: {collection_result}")
        
        # Step 2: Get articles for analysis
        logger.info("Step 2: Getting articles for analysis...")
        articles = collector.get_articles_for_analysis(hours=24)
        logger.info(f"Found {len(articles)} articles")
        
        if not articles:
            logger.warning("No articles found!")
            await send_telegram_message(
                "⚠️ Không có tin tức mới trong 24 giờ qua.",
                config.TELEGRAM_USER_ID
            )
            return
        
        # Step 3: Analyze with Gemini
        logger.info("Step 3: Analyzing with Gemini...")
        result = analyzer.analyze_news(articles)
        
        if result["success"]:
            logger.info(f"Analysis successful!")
            
            # Step 4: Send report
            logger.info("Step 4: Sending report via Telegram...")
            
            header = f"🌅 **Báo cáo sáng {datetime.now().strftime('%d/%m/%Y')}**\n\n"
            full_message = header + result["report"]
            
            await send_telegram_message(full_message, config.TELEGRAM_USER_ID)
            
            logger.info("Report sent successfully!")
            
        else:
            logger.error(f"Analysis failed: {result.get('error')}")
            await send_telegram_message(
                f"❌ Lỗi phân tích tin tức: {result.get('error')}",
                config.TELEGRAM_USER_ID
            )
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Task error: {e}", exc_info=True)
        try:
            await send_telegram_message(
                f"❌ Lỗi hệ thống: {str(e)}",
                config.TELEGRAM_USER_ID
            )
        except:
            pass
        sys.exit(1)
    
    logger.info(f"Task completed at {datetime.now()}")
    logger.info("="*50)


def main():
    """Entry point for scheduled task"""
    asyncio.run(run_scheduled_task())


if __name__ == "__main__":
    main()
