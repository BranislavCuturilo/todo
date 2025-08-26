#!/bin/bash

echo "🔍 Provera Django settings u Docker kontejneru..."

# Proveri environment varijable
echo "📋 Environment varijable:"
docker-compose exec web env | grep DJANGO

echo ""
echo "🔧 Django settings modul:"
docker-compose exec web python -c "import os; print('DJANGO_SETTINGS_MODULE:', os.environ.get('DJANGO_SETTINGS_MODULE', 'NOT SET'))"

echo ""
echo "📁 Trenutni settings fajl:"
docker-compose exec web python -c "from django.conf import settings; print('Settings file:', settings.__file__)"

echo ""
echo "🔒 CSRF postavke:"
docker-compose exec web python -c "from django.conf import settings; print('CSRF_TRUSTED_ORIGINS:', getattr(settings, 'CSRF_TRUSTED_ORIGINS', 'NOT SET'))"

echo ""
echo "🐛 DEBUG mode:"
docker-compose exec web python -c "from django.conf import settings; print('DEBUG:', settings.DEBUG)"

echo ""
echo "🌐 ALLOWED_HOSTS:"
docker-compose exec web python -c "from django.conf import settings; print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS)"
