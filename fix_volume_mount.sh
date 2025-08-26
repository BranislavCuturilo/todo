#!/bin/bash

echo "🔧 Ispravka mountovanja volume-a..."

# Zaustavi kontejnere
echo "🛑 Zaustavljanje kontejnera..."
docker-compose down

# Obriši sve volume-ove
echo "🗑️ Brisanje svih volume-ova..."
docker volume rm todo_sqlite_data todo_static_volume todo_media_volume 2>/dev/null || true

# Kreiraj nove volume-ove
echo "📦 Kreiranje novih volume-ova..."
docker volume create todo_sqlite_data
docker volume create todo_static_volume
docker volume create todo_media_volume

# Kopiraj vašu bazu u volume
echo "📋 Kopiranje baze u volume..."
docker run --rm -v todo_sqlite_data:/app -v $(pwd)/db.sqlite3:/tmp/db.sqlite3 alpine cp /tmp/db.sqlite3 /app/

# Proveri da li je baza kopirana
echo "✅ Provera da li je baza kopirana:"
docker run --rm -v todo_sqlite_data:/app alpine ls -la /app/db.sqlite3

# Pokreni kontejnere
echo "🚀 Pokretanje kontejnera..."
docker-compose up -d

# Sačekaj da se kontejneri pokrenu
echo "⏳ Čekam da se kontejneri pokrenu..."
sleep 10

# Proveri status
echo "📋 Status kontejnera:"
docker-compose ps

echo ""
echo "📋 Logovi web kontejnera:"
docker-compose logs web | tail -5

echo ""
echo "🌐 Testirajte aplikaciju:"
echo "   http://185.119.90.175:8001"
echo "   http://todo.emikon.rs"
