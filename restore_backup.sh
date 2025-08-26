#!/bin/bash

# Backup Restore Script
echo "🔄 Restoring backup database..."

# Check if backup exists
if [ -f "backup/db.sqlite3.backup" ]; then
    echo "✅ Backup found, restoring..."
    
    # Stop containers
    docker-compose down
    
    # Copy backup to main location
    cp backup/db.sqlite3.backup db.sqlite3
    
    # Set proper permissions
    chmod 644 db.sqlite3
    
    # Start containers
    docker-compose up -d
    
    echo "✅ Backup restored successfully!"
    echo "🌐 Application should be accessible at: https://todo.emikon.rs"
else
    echo "⚠️  No backup found at backup/db.sqlite3.backup"
    echo "📝 Creating new database..."
    
    # Start containers (will create new database)
    docker-compose up -d
    
    echo "✅ New database created!"
fi

# Check status
echo "📊 Checking application status..."
docker-compose ps

echo "🎉 Done!"

