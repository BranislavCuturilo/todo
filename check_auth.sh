#!/bin/bash

echo "🔐 Provera autentifikacije i baze podataka..."

echo "📋 Provera da li postoji baza podataka:"
docker-compose exec web ls -la /app/db.sqlite3

echo ""
echo "👥 Provera korisnika u bazi:"
docker-compose exec web python manage.py shell -c "
from django.contrib.auth.models import User
users = User.objects.all()
print(f'Broj korisnika u bazi: {users.count()}')
for user in users:
    print(f'  - {user.username} (email: {user.email})')
"

echo ""
echo "🔧 Provera da li se baza može povezati:"
docker-compose exec web python manage.py check

echo ""
echo "📋 Provera logova aplikacije:"
docker-compose logs web | tail -20

echo ""
echo "🌐 Testiranje login forme:"
curl -s http://185.119.90.175:8001/login/ | grep -i "form\|input\|button"
