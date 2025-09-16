# TechHub - AI-Powered Tech News Aggregator

A modern, intelligent news aggregator that fetches, summarizes, and tracks trending tech news using AI. Built with FastAPI, SQLAlchemy, and powered by local LLM integration.

## 🚀 Features

- **📰 News Aggregation**: Fetches news from multiple RSS feeds
- **🤖 AI Summarization**: Uses Ollama (Mistral) for intelligent article summarization
- **📊 Trending Detection**: Identifies trending topics using keyword analysis
- **🔄 Auto-Update**: Scheduled news fetching every hour
- **📱 Modern UI**: Responsive, professional news interface
- **🐳 Docker Ready**: Complete containerization setup
- **📈 Analytics**: Real-time statistics and trending metrics

## 🛠️ Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Python 3.13
- **Database**: SQLite with SQLAlchemy ORM
- **AI/ML**: Ollama (Mistral), NLTK, Newspaper3k
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **News Sources**: RSS feeds (The Verge, TechCrunch, etc.)
- **Deployment**: Docker, Docker Compose

## 📋 Prerequisites

- Python 3.13+
- Docker & Docker Compose (for containerized deployment)
- Ollama (for AI summarization)

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/techhub.git
cd techhub

# Run with Docker
./docker-run.sh

# Access the application
open http://localhost:8080
```

### Option 2: Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/techhub.git
cd techhub

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from src.models import init_db; init_db()"

# Start the application
python run.py

# Access the application
open http://localhost:8000
```

## 📁 Project Structure

```
techhub/
├── src/                    # Source code
│   ├── main.py            # FastAPI application
│   ├── models.py          # Database models
│   ├── collector.py       # News collection & AI processing
│   └── simple_trending.py # Trending detection
├── static/                # Frontend assets
│   └── index.html         # Main web interface
├── docker-compose.yml     # Docker orchestration
├── Dockerfile            # Container configuration
├── requirements.txt      # Python dependencies
├── tech_scheduler.py     # Automated scheduler
└── README.md            # This file
```

## 🔧 Configuration

### RSS Feeds
Edit `src/collector.py` to add/modify news sources:

```python
RSS_FEEDS = [
    "https://www.theverge.com/rss/index.xml",
    "https://techcrunch.com/feed/",
    # Add more feeds here
]
```

### AI Model
The app uses Ollama with Mistral model. Install Ollama and pull the model:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Mistral model
ollama pull mistral
```

## 📊 API Endpoints

- `GET /` - Main web interface
- `GET /articles` - List all articles (paginated)
- `GET /articles/{id}` - Get specific article
- `GET /trending` - Get trending articles
- `GET /trending-topics` - Get trending topics
- `GET /stats` - Get statistics
- `POST /refresh` - Manually refresh news

## 🐳 Docker Commands

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart
docker-compose restart

# Access container
docker-compose exec techhub bash
```

## 🔄 Automated Features

- **Hourly News Fetching**: Automatically collects new articles
- **AI Summarization**: Generates intelligent summaries
- **Trending Detection**: Identifies popular topics
- **Database Updates**: Maintains article metadata

## 🎨 UI Features

- **Modern Design**: Clean, professional interface
- **Responsive Layout**: Works on desktop and mobile
- **Dark Theme**: Professional dark navigation
- **Infinite Scroll**: Seamless article browsing
- **Real-time Stats**: Live statistics display
- **Image Support**: Article images with fallbacks

## 📈 Monitoring

- **Health Checks**: Built-in service monitoring
- **Logging**: Comprehensive application logs
- **Statistics**: Real-time metrics and counts
- **Error Handling**: Graceful error management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Ollama](https://ollama.ai/) - Local LLM integration
- [Newspaper3k](https://newspaper.readthedocs.io/) - Article extraction
- [Font Awesome](https://fontawesome.com/) - Icons
- [Google Fonts](https://fonts.google.com/) - Typography

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/techhub/issues) page
2. Create a new issue with detailed information
3. Include logs and error messages

---

**TechHub** - Stay informed with AI-powered tech news aggregation 🚀