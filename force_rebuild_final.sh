#!/bin/bash

echo "🔨 Force rebuild Docker image-a sa najnovijim promenama..."

# Zaustavi sve kontejnere
docker-compose down

# Obriši sve Docker image-ove i cache
echo "🧹 Čišćenje Docker cache-a..."
docker system prune -af
docker builder prune -af

# Obriši sve volume-ove
docker volume prune -f

# Rebuild image bez cache-a
echo "🔨 Rebuild image-a..."
docker-compose build --no-cache

# Pokreni kontejnere
echo "🚀 Pokretanje kontejnera..."
docker-compose up -d

echo "✅ Rebuild završen!"
echo ""
echo "🔍 Provera statusa:"
docker-compose ps

echo ""
echo "📋 Provera CSRF settings-a:"
docker-compose exec web python -c "from django.conf import settings; print('CSRF_TRUSTED_ORIGINS:', getattr(settings, 'CSRF_TRUSTED_ORIGINS', 'NOT SET'))"

echo ""
echo "📄 Provera da li se CSRF_TRUSTED_ORIGINS nalazi u fajlu:"
docker-compose exec web grep -A 10 "CSRF_TRUSTED_ORIGINS" /app/solo_todo/settings_production.py

echo ""
echo "🌐 Testirajte aplikaciju:"
echo "   https://todo.emikon.rs"
