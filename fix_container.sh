#!/bin/bash

echo "🔧 Rešavanje konflikta kontejnera..."

# Zaustavi sve kontejnere
docker-compose down

# Obriši sve kontejnere koji možda ostaju
docker rm -f $(docker ps -aq) 2>/dev/null || true

# Obriši sve volume-ove
docker volume prune -f

# Pokreni kontejnere ponovo
docker-compose up -d

echo "✅ Kontejneri pokrenuti!"
echo ""
echo "🔍 Provera statusa:"
docker-compose ps

echo ""
echo "📋 Provera CSRF settings-a:"
docker-compose exec web python -c "from django.conf import settings; print('CSRF_TRUSTED_ORIGINS:', getattr(settings, 'CSRF_TRUSTED_ORIGINS', 'NOT SET'))"

echo ""
echo "📄 Sadržaj CSRF_TRUSTED_ORIGINS iz fajla:"
docker-compose exec web grep -A 10 "CSRF_TRUSTED_ORIGINS" /app/solo_todo/settings_production.py
