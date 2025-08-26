#!/bin/bash

echo "🔧 Rešavanje Nginx konflikta..."

# Zaustavi sistemski Nginx
echo "🛑 Zaustavljanje sistemskog Nginx-a..."
sudo systemctl stop nginx
sudo systemctl disable nginx

# Proveri da li je port 80 slobodan
echo "🔍 Provera portova..."
sudo netstat -tlnp | grep :80

# Pokreni Docker kontejnere
echo "🐳 Pokretanje Docker kontejnera..."
docker-compose up -d

echo "✅ Nginx konflikt rešen!"
echo ""
echo "🔍 Provera statusa:"
docker-compose ps

echo ""
echo "📋 Provera CSRF settings-a:"
docker-compose exec web python -c "from django.conf import settings; print('CSRF_TRUSTED_ORIGINS:', getattr(settings, 'CSRF_TRUSTED_ORIGINS', 'NOT SET'))"

echo ""
echo "📄 Sadržaj CSRF_TRUSTED_ORIGINS iz fajla:"
docker-compose exec web cat /app/solo_todo/settings_production.py | grep -A 15 "CSRF_TRUSTED_ORIGINS"
