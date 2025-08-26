#!/bin/bash

echo "🌐 Rešavanje problema sa domenom..."

echo "📋 Provera DNS-a:"
nslookup todo.emikon.rs

echo ""
echo "🔧 Provera firewall-a:"
sudo ufw status

echo ""
echo "📋 Provera da li Nginx sluša na portu 80:"
sudo netstat -tlnp | grep :80

echo ""
echo "🌐 Testiranje lokalno:"
curl -I http://localhost
curl -I http://127.0.0.1

echo ""
echo "📋 Provera Nginx konfiguracije:"
docker-compose exec nginx nginx -t

echo ""
echo "🔧 Restart Nginx-a:"
docker-compose restart nginx

echo ""
echo "📋 Provera logova:"
docker-compose logs nginx | tail -10
