#!/bin/bash

echo "🔍 Detaljna provera settings fajlova..."

echo "📄 Sadržaj settings_production.py CSRF_TRUSTED_ORIGINS:"
docker-compose exec web cat /app/solo_todo/settings_production.py | grep -A 15 "CSRF_TRUSTED_ORIGINS"

echo ""
echo "📄 Sadržaj settings.py CSRF_TRUSTED_ORIGINS:"
docker-compose exec web cat /app/solo_todo/settings.py | grep -A 15 "CSRF_TRUSTED_ORIGINS" 2>/dev/null || echo "Nema CSRF_TRUSTED_ORIGINS u settings.py"

echo ""
echo "🔧 Provera koji settings se koristi:"
docker-compose exec web python -c "
import os
import django
print('DJANGO_SETTINGS_MODULE:', os.environ.get('DJANGO_SETTINGS_MODULE'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solo_todo.settings_production')
django.setup()
from django.conf import settings
print('Settings module:', settings.SETTINGS_MODULE)
print('CSRF_TRUSTED_ORIGINS:', getattr(settings, 'CSRF_TRUSTED_ORIGINS', 'NOT SET'))
print('DEBUG:', settings.DEBUG)
"

echo ""
echo "📋 Provera environment varijabli u kontejneru:"
docker-compose exec web env | grep -E "(DJANGO|DEBUG|ALLOWED_HOSTS)"
