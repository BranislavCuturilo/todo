#!/bin/bash

# SQLite Docker Deployment Script
echo "🚀 Starting SQLite Todo App Deployment..."

# Check if backup exists
if [ -f "backup/db.sqlite3.backup" ]; then
    echo "✅ Backup database found - will be restored on startup"
    # Restore backup
    cp backup/db.sqlite3.backup db.sqlite3
    chmod 644 db.sqlite3
else
    echo "⚠️  No backup database found - will create new database"
fi

# Build and start containers
echo "🔨 Building and starting containers..."
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for containers to be ready
echo "⏳ Waiting for containers to be ready..."
sleep 10

# Check if containers are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Application is running successfully!"
    echo "🌐 Access your application at: http://localhost:8001"
    echo "📊 Container status:"
    docker-compose ps
else
    echo "❌ Application failed to start. Check logs:"
    docker-compose logs
fi
