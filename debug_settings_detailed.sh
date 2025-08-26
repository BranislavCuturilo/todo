#!/bin/bash

echo "🔍 Detaljna provera Django settings..."

echo "📁 Provera da li postoji settings_production.py:"
docker-compose exec web ls -la /app/solo_todo/settings_production.py

echo ""
echo "📄 Sadržaj CSRF_TRUSTED_ORIGINS iz settings_production.py:"
docker-compose exec web grep -A 10 "CSRF_TRUSTED_ORIGINS" /app/solo_todo/settings_production.py

echo ""
echo "🔧 Provera environment varijabli:"
docker-compose exec web env | grep -E "(DJANGO|DEBUG|ALLOWED_HOSTS)"

echo ""
echo "📋 Provera da li se settings učitava iz pravog fajla:"
docker-compose exec web python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solo_todo.settings_production')
django.setup()
from django.conf import settings
print('Settings module:', settings.SETTINGS_MODULE)
print('CSRF_TRUSTED_ORIGINS:', getattr(settings, 'CSRF_TRUSTED_ORIGINS', 'NOT SET'))
print('CSRF_COOKIE_DOMAIN:', getattr(settings, 'CSRF_COOKIE_DOMAIN', 'NOT SET'))
"
