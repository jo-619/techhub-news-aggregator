import feedparser
from newspaper import Article as NewsArticle
from datetime import datetime, timezone
import requests
from .models import SessionLocal, Article, init_db
from .summarizer import get_simple_summary
RSS_FEEDS = [
    # Tech-specific RSS feeds
    # "https://techcrunch.com/feed/",  # TechCrunch
    "https://www.theverge.com/rss/index.xml",  # The Verge
    # "https://www.theverge.com/rss/index.xml",  # The Verge
    # "https://arstechnica.com/feed/",  # Ars Technica
    # "https://www.wired.com/feed/rss",  # Wired
    # "https://feeds.feedburner.com/venturebeat/SZYF",  # VentureBeat
    # "https://www.engadget.com/rss.xml",  # Engadget
    # "https://feeds.feedburner.com/oreilly/radar",  # O'Reilly Radar
    # "https://www.zdnet.com/topic/artificial-intelligence/rss.xml",  # ZDNet AI
    # "https://feeds.feedburner.com/venturebeat/SZYF",  # VentureBeat
    # # General tech news
    # "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",  # NY Times Tech
    # "https://www.theguardian.com/technology/rss",  # Guardian Tech
    # "https://www.bbc.com/news/technology/rss.xml",  # BBC Tech
    # Add more tech feeds here
]

# 1️⃣ Initialize database
def create_table():
    init_db()

# 2️⃣ No filtering - collect all articles from feeds

# 3️⃣ Extract image URL from RSS entry
def extract_image_url(entry):
    """Extract image URL from RSS entry, checking multiple possible fields"""
    import html
    
    # Check various RSS image fields
    image_fields = [
        'media_content',  # Media RSS
        'media_thumbnail',  # Media RSS thumbnail
        'enclosures',  # RSS enclosures
        'image',  # Direct image field
        'media:content',  # Media RSS namespace
        'media:thumbnail'  # Media RSS thumbnail namespace
    ]
    
    for field in image_fields:
        if hasattr(entry, field):
            value = getattr(entry, field)
            if isinstance(value, list) and value:
                # Handle list of media items
                for item in value:
                    if hasattr(item, 'url'):
                        return html.unescape(item.url)
                    elif isinstance(item, dict) and 'url' in item:
                        return html.unescape(item['url'])
            elif hasattr(value, 'url'):
                return html.unescape(value.url)
            elif isinstance(value, dict) and 'url' in value:
                return html.unescape(value['url'])
            elif isinstance(value, str) and value.startswith('http'):
                return html.unescape(value)
    
    # Check for image in content/summary (fallback)
    content_fields = ['content', 'summary', 'description']
    for field in content_fields:
        if hasattr(entry, field):
            content = getattr(entry, field)
            if isinstance(content, list) and content:
                content = content[0].value if hasattr(content[0], 'value') else str(content[0])
            else:
                content = str(content)
            
            # Look for img tags
            import re
            img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content, re.IGNORECASE)
            if img_match:
                return html.unescape(img_match.group(1))
    
    return None

# 4️⃣ Extract full article content
def extract_article_content(url):
    try:
        article = NewsArticle(url)
        article.download()
        article.parse()
        return article.text.strip()
    except:
        return ""

# 3️⃣ Fetch articles from RSS
def fetch_articles():
    articles = []
    
    for feed_url in RSS_FEEDS:
        try:
            # Use requests to fetch the feed content
            response = requests.get(feed_url, 
                                 headers={'User-Agent': 'Mozilla/5.0'}, 
                                 timeout=10,
                                 verify=False)  # Disable SSL verification for development
            response.raise_for_status()
            
            # Parse the feed content
            feed = feedparser.parse(response.content)
            print(f"Feed: {feed_url} — {len(feed.entries)} entries")
            
            if feed.bozo:
                print(f"  Warning: Feed parsing issues - {feed.bozo_exception}")
        except Exception as e:
            print(f"  Error fetching {feed_url}: {e}")
            continue
            
        for entry in feed.entries[:10]:  # Process up to 10 articles per feed
            title = entry.get("title", "")
            link = entry.get("link", "")
            if not title or not link:
                continue
            
            # Extract image URL from various RSS fields
            image_url = extract_image_url(entry)
            
            # Check if article already exists BEFORE expensive operations
            db = SessionLocal()
            existing = db.query(Article).filter(Article.link == link).first()
            db.close()
            
            if existing:
                print(f"  ⏭️  Skipping duplicate: {title[:50]}...")
                continue
                
            content = extract_article_content(link)
            print(f"{title} — content length: {len(content)}")
            
            # Generate summary if content is substantial
            summary = ""
            if content and len(content) > 100:
                try:
                    summary = get_simple_summary(content)
                    print(f"  Generated summary: {summary[:100]}...")
                except Exception as e:
                    print(f"  Failed to generate summary: {e}")
                    summary = ""
            
            articles.append({
                "title": title,
                "link": link,
                "published": datetime.now(timezone.utc),
                "content": content,
                "summary": summary,
                "image_url": image_url
            })
    return articles

# 4️⃣ Save to Database
def save_articles(articles):
    from .models import Metadata
    from datetime import datetime, timezone
    
    db = SessionLocal()
    saved_count = 0
    
    for art in articles:
        try:
            # Articles are already filtered for duplicates, so just save them
            article = Article(
                title=art["title"],
                link=art["link"],
                content=art["content"],
                summary=art["summary"],
                image_url=art["image_url"],
                published=art["published"]
            )
            db.add(article)
            db.commit()  # Commit each article individually
            saved_count += 1
        except Exception as e:
            print(f"❌ Failed to process {art['link']}: {e}")
            db.rollback()  # Rollback on error
    
    # Update last fetch time
    if saved_count > 0:
        try:
            # Check if last_fetch record exists
            last_fetch = db.query(Metadata).filter(Metadata.key == "last_fetch").first()
            if last_fetch:
                last_fetch.value = datetime.now(timezone.utc).isoformat()
                last_fetch.updated_at = datetime.now(timezone.utc)
            else:
                last_fetch = Metadata(
                    key="last_fetch",
                    value=datetime.now(timezone.utc).isoformat()
                )
                db.add(last_fetch)
            db.commit()
        except Exception as e:
            print(f"❌ Failed to update last fetch time: {e}")
            db.rollback()
    
    print(f"✅ Saved {saved_count} new articles")
    db.close()

# 5️⃣ Main execution
if __name__ == "__main__":
    create_table()
    articles = fetch_articles()
    save_articles(articles)
