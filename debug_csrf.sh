#!/bin/bash

echo "🔍 Detaljna provera CSRF postavki..."

echo "📄 Ceo sadržaj settings_production.py:"
docker-compose exec web cat /app/solo_todo/settings_production.py

echo ""
echo "🔧 Provera da li se fajl učitava iz pravog mesta:"
docker-compose exec web python -c "
import os
import sys
print('Current directory:', os.getcwd())
print('Files in solo_todo:')
for f in os.listdir('/app/solo_todo'):
    print(f'  {f}')
print('\\nSettings file content:')
with open('/app/solo_todo/settings_production.py', 'r') as f:
    content = f.read()
    if 'CSRF_TRUSTED_ORIGINS' in content:
        lines = content.split('\\n')
        for i, line in enumerate(lines):
            if 'CSRF_TRUSTED_ORIGINS' in line:
                print(f'Line {i+1}: {line}')
                for j in range(i+1, min(i+15, len(lines))):
                    print(f'Line {j+1}: {lines[j]}')
                break
    else:
        print('CSRF_TRUSTED_ORIGINS nije pronađen u fajlu!')
"
