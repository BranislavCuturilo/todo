#!/bin/bash

echo "🔍 Debug restart problema..."

echo "📋 Status kontejnera:"
docker-compose ps

echo ""
echo "📋 Logovi web kontejnera:"
docker-compose logs web

echo ""
echo "📋 Logovi nginx kontejnera:"
docker-compose logs nginx

echo ""
echo "🔧 Provera da li web kontejner može da se poveže:"
docker-compose exec web curl -I http://localhost:8000 2>/dev/null || echo "Web kontejner ne radi"

echo ""
echo "📋 Provera da li postoje svi potrebni fajlovi:"
docker-compose exec web ls -la /app/ | head -10

echo ""
echo "📋 Provera da li manage.py postoji:"
docker-compose exec web ls -la /app/manage.py

echo ""
echo "🔧 Provera da li Django može da se pokrene:"
docker-compose exec web python manage.py check 2>/dev/null || echo "Django check ne radi"
