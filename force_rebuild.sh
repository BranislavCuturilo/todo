#!/bin/bash

echo "🔨 Force rebuild Docker image-a..."

# Zaustavi kontejnere
docker-compose down

# Obriši sve Docker image-ove
docker system prune -f
docker rmi $(docker images -q) 2>/dev/null || true

# Rebuild image bez cache-a
docker-compose build --no-cache

# Pokreni kontejnere
docker-compose up -d

echo "✅ Rebuild završen!"
echo ""
echo "🔍 Provera settings-a:"
docker-compose exec web python -c "from django.conf import settings; print('CSRF_TRUSTED_ORIGINS:', getattr(settings, 'CSRF_TRUSTED_ORIGINS', 'NOT SET'))"
