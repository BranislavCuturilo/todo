#!/bin/bash

echo "💾 Debug baze podataka..."

echo "📋 Provera da li postoji vaša stara baza:"
ls -la /opt/todo/db.sqlite3

echo ""
echo "📋 Veličina baze:"
du -h /opt/todo/db.sqlite3

echo ""
echo "📋 Provera da li se baza može otvoriti:"
docker-compose exec web python -c "
import sqlite3
try:
    conn = sqlite3.connect('/app/db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
    tables = cursor.fetchall()
    print('Tabele u bazi:')
    for table in tables:
        print(f'  - {table[0]}')
    conn.close()
except Exception as e:
    print(f'Greška: {e}')
"

echo ""
echo "👥 Provera korisnika u trenutnoj bazi:"
docker-compose exec web python manage.py shell -c "
from django.contrib.auth.models import User
users = User.objects.all()
print(f'Broj korisnika: {users.count()}')
for user in users:
    print(f'  - {user.username} (email: {user.email})')
"

echo ""
echo "📋 Provera da li se koristi Docker volume:"
docker volume ls | grep todo

echo ""
echo "🔧 Provera sadržaja Docker volume-a:"
docker run --rm -v todo_sqlite_data:/app alpine ls -la /app/db.sqlite3 2>/dev/null || echo "Baza nije u Docker volume-u"
