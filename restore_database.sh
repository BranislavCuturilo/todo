#!/bin/bash

echo "💾 Ubacivanje postojeće baze podataka..."

echo "📋 Instrukcije:"
echo "1. Kopirajte vašu db.sqlite3 datoteku u /opt/todo/ direktorijum"
echo "2. Zatim pokrenite ovu skriptu"
echo ""

# Proveri da li postoji db.sqlite3 u trenutnom direktorijumu
if [ -f "db.sqlite3" ]; then
    echo "✅ Pronađena db.sqlite3 datoteka!"
    
    # Zaustavi kontejnere
    docker-compose down
    
    # Kopiraj bazu u Docker volume
    docker volume create todo_sqlite_data
    docker run --rm -v todo_sqlite_data:/app -v $(pwd)/db.sqlite3:/app/db.sqlite3 alpine cp /app/db.sqlite3 /app/
    
    # Pokreni kontejnere
    docker-compose up -d
    
    echo "✅ Baza podataka uspešno ubacena!"
    
    echo ""
    echo "👥 Provera korisnika u bazi:"
    docker-compose exec web python manage.py shell -c "
from django.contrib.auth.models import User
users = User.objects.all()
print(f'Broj korisnika u bazi: {users.count()}')
for user in users:
    print(f'  - {user.username} (email: {user.email})')
"
else
    echo "❌ db.sqlite3 datoteka nije pronađena u trenutnom direktorijumu"
    echo "📝 Molim vas da kopirate vašu db.sqlite3 datoteku u /opt/todo/ direktorijum"
fi
