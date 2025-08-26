#!/bin/bash

echo "🧹 Čišćenje postojećih instalacija..."

# Zaustavi i ukloni postojeće Docker kontejnere
docker-compose down -v
docker system prune -f

# Zaustavi Nginx servis
sudo systemctl stop nginx
sudo systemctl disable nginx

# Ukloni postojeće Nginx konfiguracije
sudo rm -f /etc/nginx/sites-enabled/default
sudo rm -f /etc/nginx/sites-enabled/todo
sudo rm -f /etc/nginx/sites-available/todo

# Očisti postojeće SSL sertifikate
sudo rm -rf /etc/letsencrypt/live/todo.emikon.rs
sudo rm -rf /etc/letsencrypt/archive/todo.emikon.rs

echo "✅ Čišćenje završeno!"
