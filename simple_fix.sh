#!/bin/bash

echo "🔧 Jednostavna ispravka baze..."

# Zaustavi kontejnere
echo "🛑 Zaustavljanje kontejnera..."
docker-compose down

# Obriši volume-ove
echo "🗑️ Brisanje volume-ova..."
docker volume rm todo_sqlite_data todo_static_volume todo_media_volume 2>/dev/null || true

# Pokreni kontejnere
echo "🚀 Pokretanje kontejnera..."
docker-compose up -d

# Sačekaj da se pokrenu
echo "⏳ Čekam da se kontejneri pokrenu..."
sleep 15

# Kopiraj bazu direktno u kontejner
echo "📋 Kopiranje baze u kontejner..."
docker cp db.sqlite3 todo-web-1:/app/db.sqlite3

# Restart web kontejnera
echo "🔄 Restart web kontejnera..."
docker-compose restart web

# Sačekaj da se restartuje
sleep 10

echo "✅ Gotovo!"
echo ""
echo "📋 Status kontejnera:"
docker-compose ps

echo ""
echo "📋 Provera baze u kontejneru:"
docker-compose exec web ls -la /app/db.sqlite3

echo ""
echo "👥 Provera korisnika:"
docker-compose exec web python manage.py shell -c "
from django.contrib.auth.models import User
users = User.objects.all()
print(f'Broj korisnika: {users.count()}')
for user in users:
    print(f'  - {user.username} (email: {user.email})')
"

echo ""
echo "🌐 Testirajte aplikaciju:"
echo "   http://185.119.90.175:8001"
echo "   http://todo.emikon.rs"
