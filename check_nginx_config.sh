#!/bin/bash

echo "🌐 Provera Nginx konfiguracije..."

echo "📄 Trenutna Nginx konfiguracija:"
docker-compose exec nginx cat /etc/nginx/conf.d/default.conf

echo ""
echo "🔧 Provera da li Nginx može da se poveže sa web kontejnerom:"
docker-compose exec nginx ping -c 3 web

echo ""
echo "📋 Provera da li web kontejner radi:"
docker-compose exec web curl -I http://localhost:8000

echo ""
echo "🌐 Testiranje proxy-ja:"
docker-compose exec nginx curl -I http://web:8000

echo ""
echo "📋 Provera logova web kontejnera:"
docker-compose logs web | tail -10

echo ""
echo "🔧 Provera da li se domen može dostići sa VPS-a:"
curl -I http://todo.emikon.rs
