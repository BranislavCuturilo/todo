#!/bin/bash

set -e  # Exit on any error

echo "🚀 Početak kompletnog deployment-a TODO aplikacije..."

# 1. Čišćenje sistema
echo "🧹 Čišćenje postojećih instalacija..."
docker-compose down -v 2>/dev/null || true
docker system prune -f
sudo systemctl stop nginx 2>/dev/null || true
sudo systemctl disable nginx 2>/dev/null || true

# 2. Kloniranje repozitorijuma
echo "📥 Kloniranje repozitorijuma..."
if [ ! -d "/opt/todo" ]; then
    sudo mkdir -p /opt/todo
    sudo chown $USER:$USER /opt/todo
fi

cd /opt/todo

if [ ! -d ".git" ]; then
    git clone https://github.com/BranislavCuturilo/todo.git .
else
    git pull origin main
fi

# 3. Podešavanje Nginx
echo "🌐 Podešavanje Nginx..."
sudo cp nginx-todo.conf /etc/nginx/sites-available/todo
sudo ln -sf /etc/nginx/sites-available/todo /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx konfiguracije
sudo nginx -t

# Pokretanje Nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# 4. Podešavanje SSL sertifikata
echo "🔒 Podešavanje SSL sertifikata..."
sudo certbot --nginx -d todo.emikon.rs -d www.todo.emikon.rs --non-interactive --agree-tos --email baki1812@gmail.com

# 5. Pokretanje Docker aplikacije
echo "🐳 Pokretanje Docker aplikacije..."
docker-compose up -d

# 6. Čekanje da se aplikacija pokrene
echo "⏳ Čekanje da se aplikacija pokrene..."
sleep 10

# 7. Provera statusa
echo "🔍 Provera statusa..."
docker-compose ps
sudo systemctl status nginx

# 8. Podešavanje automatskog obnavljanja SSL
echo "🔄 Podešavanje automatskog obnavljanja SSL..."
sudo crontab -l 2>/dev/null | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | sudo crontab -

# 9. Podešavanje backup-a
echo "💾 Podešavanje backup sistema..."
mkdir -p /opt/todo/backups

cat > /opt/todo/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/todo/backups"
mkdir -p $BACKUP_DIR

# Database backup
docker-compose exec -T web cp /app/db.sqlite3 /tmp/db_backup.sqlite3
docker cp $(docker-compose ps -q web):/tmp/db_backup.sqlite3 $BACKUP_DIR/db_$DATE.sqlite3

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sqlite3" -mtime +7 -delete
EOF

chmod +x /opt/todo/backup.sh

# Dodaj backup u crontab
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/todo/backup.sh") | crontab -

echo "✅ Deployment završen uspešno!"
echo ""
echo "🌐 Vaša aplikacija je dostupna na:"
echo "   http://todo.emikon.rs"
echo "   https://todo.emikon.rs"
echo ""
echo "🔧 Korisne komande:"
echo "   docker-compose logs -f    # Pregled logova"
echo "   docker-compose restart    # Restart aplikacije"
echo "   sudo systemctl restart nginx  # Restart Nginx-a"
echo "   /opt/todo/backup.sh      # Ručni backup"
echo ""
echo "📝 Napomene:"
echo "1. Aplikacija je pokrenuta na portu 8001"
echo "2. Nginx rutira saobracaj sa todo.emikon.rs na port 8001"
echo "3. SSL sertifikat je automatski podesen"
echo "4. Backup se radi automatski svaki dan u 2:00"
echo "5. SSL se obnavlja automatski"
echo ""
echo "🎉 Deployment završen!"
