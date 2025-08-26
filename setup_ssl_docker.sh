#!/bin/bash

echo "🔒 Podešavanje SSL sertifikata za Docker Nginx..."

# Zaustavi Docker kontejnere
docker-compose down

# Podesi SSL sertifikat
echo "📜 Generisanje SSL sertifikata..."
sudo certbot certonly --standalone -d todo.emikon.rs -d www.todo.emikon.rs --non-interactive --agree-tos --email baki1812@gmail.com

# Kopiraj SSL sertifikate u Docker volume
echo "📋 Kopiranje SSL sertifikata..."
sudo mkdir -p /opt/todo/ssl
sudo cp /etc/letsencrypt/live/todo.emikon.rs/fullchain.pem /opt/todo/ssl/
sudo cp /etc/letsencrypt/live/todo.emikon.rs/privkey.pem /opt/todo/ssl/
sudo chown -R $USER:$USER /opt/todo/ssl

# Modifikuj docker-compose.yml da koristi SSL
echo "🐳 Modifikovanje docker-compose.yml za SSL..."
cat > docker-compose-ssl.yml << 'EOF'
services:
  web:
    build: .
    command: >
      sh -c "
        python manage.py migrate &&
        python manage.py collectstatic --noinput &&
        gunicorn --bind 0.0.0.0:8000 --workers 3 solo_todo.wsgi:application
      "
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - sqlite_data:/app
    ports:
      - "8001:8000"
    environment:
      - SECRET_KEY=your-super-secret-key-here-change-this
      - DEBUG=False
      - ALLOWED_HOSTS=localhost,127.0.0.1,todo.emikon.rs,www.todo.emikon.rs,185.119.90.175
      - DB_ENGINE=sqlite3
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx-ssl.conf:/etc/nginx/conf.d/default.conf
      - ./ssl:/etc/nginx/ssl
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - web
    restart: unless-stopped

volumes:
  static_volume:
  media_volume:
  sqlite_data:
EOF

# Kreiram Nginx konfiguraciju sa SSL
echo "🌐 Kreiranje Nginx konfiguracije sa SSL..."
cat > nginx-ssl.conf << 'EOF'
server {
    listen 80;
    server_name todo.emikon.rs www.todo.emikon.rs;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name todo.emikon.rs www.todo.emikon.rs;
    
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Client max body size for file uploads
    client_max_body_size 10M;
    
    # Proxy to Docker container on port 8001
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files
    location /static/ {
        proxy_pass http://web:8000/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        proxy_pass http://web:8000/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
}
EOF

# Pokreni kontejnere sa SSL
echo "🚀 Pokretanje kontejnera sa SSL..."
docker-compose -f docker-compose-ssl.yml up -d

echo "✅ SSL podešavanje završeno!"
echo ""
echo "🔍 Provera statusa:"
docker-compose -f docker-compose-ssl.yml ps

echo ""
echo "🌐 Testirajte:"
echo "   https://todo.emikon.rs"
