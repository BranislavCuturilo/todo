#!/bin/bash

echo "🔍 Provera portova..."

echo "📋 Koji procesi koriste port 80:"
sudo netstat -tlnp | grep :80

echo ""
echo "📋 Koji procesi koriste port 443:"
sudo netstat -tlnp | grep :443

echo ""
echo "🐳 Docker kontejneri koji rade:"
docker ps

echo ""
echo "📄 Sadržaj CSRF_TRUSTED_ORIGINS iz settings_production.py:"
docker-compose exec web cat /app/solo_todo/settings_production.py | grep -A 15 "CSRF_TRUSTED_ORIGINS"

echo ""
echo "🔧 Provera da li se settings učitava iz pravog fajla:"
docker-compose exec web python -c "
import os
import sys
print('Python path:', sys.path)
print('Current working directory:', os.getcwd())
print('Files in solo_todo directory:')
for f in os.listdir('/app/solo_todo'):
    if f.startswith('settings'):
        print(f'  {f}')
"
