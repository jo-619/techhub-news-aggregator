#!/usr/bin/env python3
"""
Tech News Scheduler
Automatically fetches tech news every hour
"""

import time
import schedule
import logging
from datetime import datetime, timezone
from src.collector import fetch_articles, save_articles, create_table
from src.simple_trending import trending_detector
from src.models import SessionLocal, Article

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tech_news_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_tech_news_collection():
    """Run tech news collection and analysis"""
    logger.info("🔄 Starting hourly tech news collection...")
    start_time = time.time()
    
    try:
        # Initialize database
        create_table()
        
        # Fetch and save tech articles
        articles = fetch_articles()
        save_articles(articles)
        
        # Analyze trending tech news
        trending = trending_detector.get_trending_news(hours=24, limit=5)
        logger.info(f"📊 Found {len(trending)} trending tech topics")
        
        # Log top trending tech news
        for i, article in enumerate(trending[:3]):
            logger.info(f"🔥 Trending #{i+1}: {article['title'][:60]}... (Score: {article['trending_score']})")
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"✅ Tech news collection completed in {duration:.2f} seconds")
        logger.info(f"📰 Processed {len(articles)} articles")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in tech news collection: {e}")
        return False

def get_tech_stats():
    """Get current tech news statistics"""
    try:
        db = SessionLocal()
        total_articles = db.query(Article).count()
        recent_articles = db.query(Article).filter(
            Article.published >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()
        db.close()
        
        logger.info(f"📈 Stats: {total_articles} total articles, {recent_articles} today")
        return total_articles, recent_articles
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return 0, 0

def main():
    """Main scheduler function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Tech News Scheduler')
    parser.add_argument('--interval', type=int, default=60, help='Collection interval in minutes (default: 60)')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon with scheduling')
    
    args = parser.parse_args()
    
    logger.info("🚀 Starting Tech News Scheduler")
    logger.info(f"⏰ Collection interval: {args.interval} minutes")
    
    if args.once:
        # Run once and exit
        run_tech_news_collection()
        get_tech_stats()
    else:
        # Schedule regular collection
        schedule.every(args.interval).minutes.do(run_tech_news_collection)
        
        # Run initial collection
        logger.info("🔄 Running initial tech news collection...")
        run_tech_news_collection()
        get_tech_stats()
        
        # Keep running
        logger.info(f"⏰ Scheduler running - will collect tech news every {args.interval} minutes")
        logger.info("Press Ctrl+C to stop")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("🛑 Scheduler stopped by user")
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}")

if __name__ == "__main__":
    main()
