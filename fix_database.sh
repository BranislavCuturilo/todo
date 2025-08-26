#!/bin/bash

echo "💾 Zamena baze podataka u Docker volume-u..."

# Zaustavi kontejnere
echo "🛑 Zaustavljanje kontejnera..."
docker-compose down

# Obriši postojeći volume
echo "🗑️ Brisanje postojećeg volume-a..."
docker volume rm todo_sqlite_data

# Kreiraj novi volume
echo "📦 Kreiranje novog volume-a..."
docker volume create todo_sqlite_data

# Kopiraj vašu bazu u novi volume
echo "📋 Kopiranje vaše baze u volume..."
docker run --rm -v todo_sqlite_data:/app -v $(pwd)/db.sqlite3:/app/db.sqlite3 alpine cp /app/db.sqlite3 /app/

# Pokreni kontejnere
echo "🚀 Pokretanje kontejnera..."
docker-compose up -d

echo "✅ Baza zamenjena!"
echo ""
echo "👥 Provera korisnika u bazi:"
docker-compose exec web python manage.py shell -c "
from django.contrib.auth.models import User
users = User.objects.all()
print(f'Broj korisnika: {users.count()}')
for user in users:
    print(f'  - {user.username} (email: {user.email})')
"

echo ""
echo "📋 Provera veličine baze u volume-u:"
docker run --rm -v todo_sqlite_data:/app alpine ls -la /app/db.sqlite3

echo ""
echo "🌐 Testirajte aplikaciju:"
echo "   http://185.119.90.175:8001"
echo "   http://todo.emikon.rs"
