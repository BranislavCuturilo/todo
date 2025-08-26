#!/bin/bash

echo "🔄 Jednostavan restart kontejnera..."

# Restart kontejnere
echo "🔄 Restart kontejnera..."
docker-compose restart

# Sačekaj da se pokrenu
echo "⏳ Čekam da se kontejneri pokrenu..."
sleep 20

echo "✅ Gotovo!"
echo ""
echo "📋 Status kontejnera:"
docker-compose ps

echo ""
echo "📋 Logovi web kontejnera:"
docker-compose logs web | tail -10

echo ""
echo "🌐 Testirajte aplikaciju:"
echo "   http://185.119.90.175:8001"
echo "   http://todo.emikon.rs"
