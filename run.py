#!/usr/bin/env python3
"""
News Tracker - Main Entry Point
Run the news collection and API server
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.collector import create_table, fetch_articles, save_articles
from src.simple_trending import trending_detector

def main():
    """Main function to run news collection"""
    print("🚀 Starting News Collection...")
    
    # Initialize database
    create_table()
    
    # Fetch and save articles
    articles = fetch_articles()
    save_articles(articles)
    
    print("✅ News collection completed!")

if __name__ == "__main__":
    main()
