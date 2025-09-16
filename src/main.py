from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from .models import SessionLocal, Article, init_db
from .summarizer import summarize_with_ollama, get_simple_summary
from .simple_trending import get_trending_topics, trending_detector
from datetime import datetime, timezone
from typing import List, Optional
import os

app = FastAPI(title="Global News Tracker", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Serve static files (for frontend)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    """Serve the main frontend page"""
    if os.path.exists("static/index.html"):
        with open("static/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    return {"message": "Global News Tracker API", "docs": "/docs"}

@app.get("/articles")
def get_articles(limit: int = 50, offset: int = 0):
    """Get articles with pagination"""
    db = SessionLocal()
    articles = db.query(Article).order_by(Article.published.desc()).offset(offset).limit(limit).all()
    db.close()
    
    return [{
        "id": a.id,
        "title": a.title, 
        "link": a.link, 
        "content": a.content[:500] + "..." if len(a.content) > 500 else a.content,
        "summary": a.summary or "No summary available",
        "image_url": a.image_url,
        "published": a.published.isoformat() if a.published else None
    } for a in articles]

@app.get("/articles/{article_id}")
def get_article(article_id: int):
    """Get a specific article by ID"""
    db = SessionLocal()
    article = db.query(Article).filter(Article.id == article_id).first()
    db.close()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return {
        "id": article.id,
        "title": article.title,
        "link": article.link,
        "content": article.content,
        "summary": article.summary or "No summary available",
        "published": article.published.isoformat() if article.published else None
    }

@app.get("/summarize/{article_id}")
def summarize_article(article_id: int):
    """Summarize a specific article"""
    db = SessionLocal()
    article = db.query(Article).filter(Article.id == article_id).first()
    db.close()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    summary = summarize_with_ollama(article.content)
    return {
        "id": article.id,
        "title": article.title,
        "summary": summary
    }

@app.get("/trending")
def get_trending(hours: int = 168):  # Default to 7 days (168 hours)
    """Get trending news articles from recent articles"""
    try:
        trending = trending_detector.get_trending_news(hours, 10)
        return {"trending_news": trending, "hours": hours}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting trending news: {str(e)}")

@app.get("/trending-topics")
def get_trending_topics_endpoint(hours: int = 24):
    """Get trending topics (legacy endpoint)"""
    try:
        trending = get_trending_topics(hours)
        return {"trending_topics": trending, "hours": hours}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting trending topics: {str(e)}")

# Removed timeline endpoint for now - can be added later

@app.get("/stats")
def get_stats():
    """Get basic statistics about the news database"""
    from .models import Metadata
    
    db = SessionLocal()
    total_articles = db.query(Article).count()
    recent_articles = db.query(Article).filter(
        Article.published >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    ).count()
    
    # Get the actual last fetch time
    last_fetch_record = db.query(Metadata).filter(Metadata.key == "last_fetch").first()
    last_updated = last_fetch_record.value if last_fetch_record else datetime.now(timezone.utc).isoformat()
    
    db.close()
    
    return {
        "total_articles": total_articles,
        "articles_today": recent_articles,
        "last_updated": last_updated
    }

@app.post("/refresh")
def refresh_news():
    """Manually trigger news collection"""
    try:
        from .collector import fetch_articles, save_articles
        articles = fetch_articles()
        save_articles(articles)
        return {"message": f"Successfully processed {len(articles)} articles"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing news: {str(e)}")
