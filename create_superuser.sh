#!/bin/bash

echo "👤 Kreiranje superuser-a..."

# Kreiraj superuser
docker-compose exec web python manage.py createsuperuser --noinput --username admin --email admin@todo.emikon.rs

# Postavi password za admin korisnika
echo "🔐 Postavljanje password-a za admin korisnika..."
docker-compose exec web python manage.py shell -c "
from django.contrib.auth.models import User
user = User.objects.get(username='admin')
user.set_password('admin123')
user.save()
print('Admin korisnik kreiran sa password-om: admin123')
"

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
echo "✅ Superuser kreiran!"
echo "🌐 Pristupite aplikaciji:"
echo "   http://todo.emikon.rs"
echo "   Username: admin"
echo "   Password: admin123"
