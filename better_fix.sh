#!/bin/bash

echo "🔧 Bolja ispravka baze..."

# Zaustavi kontejnere
echo "🛑 Zaustavljanje kontejnera..."
docker-compose down

# Obriši volume-ove
echo "🗑️ Brisanje volume-ova..."
docker volume rm todo_static_volume todo_media_volume 2>/dev/null || true

# Pokreni kontejnere
echo "🚀 Pokretanje kontejnera..."
docker-compose up -d

# Sačekaj da se web kontejner potpuno pokrene
echo "⏳ Čekam da se web kontejner potpuno pokrene..."
for i in {1..30}; do
    if docker-compose ps | grep -q "Up.*todo-web-1"; then
        echo "✅ Web kontejner je pokrenut!"
        break
    fi
    echo "⏳ Čekam... ($i/30)"
    sleep 2
done

# Sačekaj još malo da se Django potpuno pokrene
echo "⏳ Čekam da se Django potpuno pokrene..."
sleep 10

# Kopiraj bazu direktno u kontejner
echo "📋 Kopiranje baze u kontejner..."
docker cp db.sqlite3 todo-web-1:/app/db.sqlite3

# Restart web kontejnera
echo "🔄 Restart web kontejnera..."
docker-compose restart web

# Sačekaj da se restartuje
echo "⏳ Čekam da se restartuje..."
sleep 15

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
" 2>/dev/null || echo "Ne mogu da pristupim bazi"

echo ""
echo "🌐 Testirajte aplikaciju:"
echo "   http://185.119.90.175:8001"
echo "   http://todo.emikon.rs"
