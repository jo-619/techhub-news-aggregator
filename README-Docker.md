# TechHub Docker Setup

This guide will help you run TechHub using Docker and Docker Compose.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

## Quick Start

### Option 1: Using the setup script (Recommended)

```bash
./docker-run.sh
```

This script will:
- Build the Docker images
- Initialize the database
- Start all services
- Display helpful information

### Option 2: Manual setup

1. **Build the images:**
   ```bash
   docker-compose build
   ```

2. **Initialize the database:**
   ```bash
   docker-compose run --rm techhub python -c "from src.models import init_db; init_db()"
   ```

3. **Start the services:**
   ```bash
   docker-compose up -d
   ```

## Services

### TechHub Web Application
- **Port:** 8080 (external) → 8000 (internal)
- **URL:** http://localhost:8080
- **Description:** Main web interface and API

### Scheduler Service
- **Description:** Automated news fetching every hour
- **Dependencies:** Requires TechHub service to be running

## Useful Commands

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f techhub
docker-compose logs -f scheduler
```

### Stop services
```bash
docker-compose down
```

### Restart services
```bash
docker-compose restart
```

### Update and restart
```bash
docker-compose pull
docker-compose up -d
```

### Access the container
```bash
docker-compose exec techhub bash
```

### Run one-time commands
```bash
# Fetch news manually
docker-compose run --rm techhub python -c "from src.collector import fetch_articles, save_articles; articles = fetch_articles(); save_articles(articles)"

# Check database
docker-compose run --rm techhub python -c "from src.models import SessionLocal, Article; db = SessionLocal(); print(f'Total articles: {db.query(Article).count()}'); db.close()"
```

## Configuration

### Environment Variables
You can customize the application by creating a `.env` file:

```env
# Database
DATABASE_URL=sqlite:///./news.db

# News sources (comma-separated)
RSS_FEEDS=https://www.theverge.com/rss/index.xml,https://techcrunch.com/feed/

# Update frequency (in hours)
UPDATE_FREQUENCY=1
```

### Volumes
- `./news.db:/app/news.db` - Database persistence
- `./static:/app/static` - Static files (if you want to modify them)

## Troubleshooting

### Port already in use
If port 8080 is already in use, modify the `docker-compose.yml` file:
```yaml
ports:
  - "8081:8000"  # Use port 8081 instead
```

### Database issues
If you encounter database issues, you can reset it:
```bash
docker-compose down
rm news.db
docker-compose up -d
```

### Memory issues
If you're running on a system with limited memory, you can:
1. Reduce the number of RSS feeds
2. Increase Docker's memory limit
3. Use a lighter base image

## Production Deployment

For production deployment, consider:

1. **Use a production WSGI server:**
   ```dockerfile
   CMD ["gunicorn", "src.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
   ```

2. **Add environment-specific configurations**
3. **Use external database (PostgreSQL/MySQL)**
4. **Add reverse proxy (Nginx)**
5. **Implement proper logging and monitoring**

## Development

For development with live reloading:

```bash
# Mount source code as volume
docker-compose -f docker-compose.dev.yml up
```

Create `docker-compose.dev.yml`:
```yaml
version: '3.8'
services:
  techhub:
    build: .
    ports:
      - "8080:8000"
    volumes:
      - .:/app
      - /app/venv  # Exclude virtual environment
    environment:
      - PYTHONPATH=/app
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```
