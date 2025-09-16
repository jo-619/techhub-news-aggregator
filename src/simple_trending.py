import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import List, Dict
from .models import SessionLocal, Article

class SimpleTrendingDetector:
    def __init__(self):
        # Basic stop words without NLTK dependency
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs'
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text for analysis"""
        if not text:
            return ""
        
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
        
        # Split into words and filter
        words = text.split()
        words = [word for word in words if word not in self.stop_words and len(word) > 2]
        
        return ' '.join(words)
    
    def extract_keywords(self, articles: List[Article]) -> List[str]:
        """Extract keywords from articles"""
        all_text = ""
        for article in articles:
            if article.content:
                all_text += " " + self.clean_text(article.title + " " + article.content)
        
        # Count word frequencies
        words = all_text.split()
        word_counts = Counter(words)
        
        # Return top keywords (excluding very common words)
        common_words = {
            'said', 'new', 'one', 'would', 'could', 'also', 'may', 'first', 'last', 'time', 'year', 'day', 'week', 'month',
            'from', 'after', 'which', 'there', 'about', 'more', 'than', 'when', 'where', 'what', 'how', 'why', 'who',
            'some', 'many', 'most', 'other', 'each', 'every', 'all', 'any', 'both', 'either', 'neither', 'such',
            'very', 'much', 'little', 'few', 'several', 'enough', 'too', 'so', 'as', 'if', 'then', 'than',
            'because', 'since', 'while', 'during', 'before', 'until', 'unless', 'although', 'though', 'however',
            'therefore', 'moreover', 'furthermore', 'nevertheless', 'meanwhile', 'consequently', 'accordingly'
        }
        filtered_words = {word: count for word, count in word_counts.items() 
                         if word not in common_words and len(word) > 4}
        
        return [word for word, count in Counter(filtered_words).most_common(50)]
    
    def get_trending_news(self, hours: int = 24, limit: int = 10) -> List[Dict]:
        """Get top trending news articles based on keyword frequency"""
        db = SessionLocal()
        
        # Get articles from the last N hours
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        recent_articles = db.query(Article).filter(
            Article.published >= cutoff_time
        ).all()
        
        db.close()
        
        if not recent_articles:
            return []
        
        # Extract keywords to understand what's trending
        keywords = self.extract_keywords(recent_articles)
        top_keywords = set(keywords[:30])  # Top 30 keywords
        
        # Score each article based on trending keyword mentions
        article_scores = []
        for article in recent_articles:
            if not article.content:
                continue
                
            # Clean the article text
            clean_text = self.clean_text(article.title + " " + article.content)
            article_words = set(clean_text.split())
            
            # Calculate trending score
            trending_score = 0
            for keyword in top_keywords:
                if keyword in article_words:
                    # Weight by keyword frequency in the corpus
                    keyword_freq = keywords.count(keyword)
                    trending_score += keyword_freq
            
            # Additional scoring factors
            title_boost = 0
            if article.title:
                title_words = set(self.clean_text(article.title).split())
                for keyword in top_keywords:
                    if keyword in title_words:
                        title_boost += 2  # Title mentions are more important
            
            total_score = trending_score + title_boost
            
            if total_score > 0:
                article_scores.append({
                    'id': article.id,
                    'title': article.title,
                    'link': article.link,
                    'content': article.content[:200] + "..." if len(article.content) > 200 else article.content,
                    'summary': article.summary or "No summary available",
                    'image_url': article.image_url,
                    'published': article.published.isoformat() if article.published else None,
                    'trending_score': total_score,
                    'keyword_matches': len(article_words.intersection(top_keywords))
                })
        
        # Sort by trending score (highest first)
        article_scores.sort(key=lambda x: x['trending_score'], reverse=True)
        
        # Return top trending articles
        return article_scores[:limit]
    
    def get_trending_topics(self, hours: int = 24) -> List[Dict]:
        """Legacy method - now returns trending news instead of topics"""
        return self.get_trending_news(hours, 10)

# Global instance
trending_detector = SimpleTrendingDetector()

def get_trending_topics(hours: int = 24) -> List[Dict]:
    """Get trending topics from recent articles"""
    return trending_detector.get_trending_topics(hours)
