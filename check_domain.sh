#!/bin/bash

echo "🔍 Provera domena i Nginx konfiguracije..."

echo "📋 DNS provera:"
nslookup todo.emikon.rs

echo ""
echo "🌐 Nginx status:"
docker-compose ps

echo ""
echo "📄 Nginx konfiguracija:"
docker-compose exec nginx cat /etc/nginx/conf.d/default.conf

echo ""
echo "📋 Nginx logovi:"
docker-compose logs nginx

echo ""
echo "🔧 Provera portova:"
sudo netstat -tlnp | grep -E "(80|443)"

echo ""
echo "🌐 Testiranje domena:"
curl -I http://todo.emikon.rs
curl -I https://todo.emikon.rs
