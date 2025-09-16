#!/bin/bash

# TechHub Docker Setup Script

echo "🚀 Setting up TechHub with Docker..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Build and start the services
echo "📦 Building Docker images..."
docker-compose build

echo "🗄️ Initializing database..."
# Initialize the database by running the collector once
docker-compose run --rm techhub python -c "
from src.models import init_db
init_db()
print('✅ Database initialized')
"

echo "🌐 Starting TechHub services..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ TechHub is now running!"
    echo "🌐 Web interface: http://localhost:8080"
    echo "📊 API stats: http://localhost:8080/stats"
    echo ""
    echo "📋 Useful commands:"
    echo "  View logs: docker-compose logs -f"
    echo "  Stop services: docker-compose down"
    echo "  Restart: docker-compose restart"
    echo "  Update: docker-compose pull && docker-compose up -d"
else
    echo "❌ Failed to start services. Check logs with: docker-compose logs"
    exit 1
fi
