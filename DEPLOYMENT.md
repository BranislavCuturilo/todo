# 🚀 TODO App - Production Deployment Guide

Ovaj vodič će vas provesti kroz proces deployment-a TODO aplikacije na VPS server.

## 📋 Preduvjeti

- Ubuntu 20.04+ ili Debian 11+ server
- Root pristup ili sudo privilegije
- Domen koji pokazuje na server
- SSH pristup serveru

## 🛠️ Server Setup

### 1. System Update
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Required Packages
```bash
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib git curl
```

### 3. Create Application User (Optional)
```bash
sudo adduser --disabled-password --gecos '' todo
sudo usermod -aG sudo todo
```

## 🗄️ Database Setup

### 1. PostgreSQL Configuration
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE todo;
CREATE USER todo WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE todo TO todo;
ALTER USER todo CREATEDB;
\q
```

### 2. Test Database Connection
```bash
sudo -u postgres psql -d todo -c "\dt"
```

## 📁 Application Setup

### 1. Clone Repository
```bash
git clone https://github.com/BranislavCuturilo/todo.git /var/www/todo
cd /var/www/todo
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
cp env.example .env
nano .env
```

Popunite `.env` fajl sa vašim podacima:
```env
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=todo.emikon.rs,www.todo.emikon.rs
DB_NAME=todo
DB_USER=todo
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Database Migration
```bash
sudo -u solo_todo python manage.py migrate --settings=solo_todo.settings_production
```

### 6. Create Superuser
```bash
sudo -u solo_todo python manage.py createsuperuser --settings=solo_todo.settings_production
```

### 7. Collect Static Files
```bash
sudo -u solo_todo python manage.py collectstatic --noinput --settings=solo_todo.settings_production
```

## 🔧 Gunicorn Setup

### 1. Update Gunicorn Configuration
```bash
sudo -u solo_todo nano gunicorn.conf.py
```

Ažurirajte putanje u `gunicorn.conf.py`:
```python
bind = "127.0.0.1:8000"
working_directory = "/home/solo_todo/app"
user = "solo_todo"
group = "solo_todo"
```

### 2. Create Systemd Service
```bash
sudo cp solo-todo.service /etc/systemd/system/
sudo nano /etc/systemd/system/solo-todo.service
```

Ažurirajte putanje u service fajlu:
```ini
WorkingDirectory=/home/solo_todo/app
Environment="PATH=/home/solo_todo/app/venv/bin"
ExecStart=/home/solo_todo/app/venv/bin/gunicorn --config gunicorn.conf.py solo_todo.wsgi:application
```

### 3. Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable solo-todo
sudo systemctl start solo-todo
sudo systemctl status solo-todo
```

## 🌐 Nginx Setup

### 1. Configure Nginx
```bash
sudo cp nginx.conf /etc/nginx/sites-available/solo-todo
sudo nano /etc/nginx/sites-available/solo-todo
```

Ažurirajte putanje i domen u nginx konfiguraciji:
```nginx
server_name yourdomain.com www.yourdomain.com;
location /static/ {
    alias /home/solo_todo/app/staticfiles/;
}
location /media/ {
    alias /home/solo_todo/app/media/;
}
```

### 2. Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/solo-todo /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Remove default site
sudo nginx -t
sudo systemctl restart nginx
```

## 🔒 SSL/HTTPS Setup (Let's Encrypt)

### 1. Install Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 2. Obtain SSL Certificate
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 3. Enable HTTPS in Django
Ažurirajte `.env` fajl:
```env
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

I ažurirajte `settings_production.py`:
```python
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)
```

### 4. Restart Services
```bash
sudo systemctl restart solo-todo
sudo systemctl restart nginx
```

## 🐳 Docker Deployment (Alternative)

Ako preferirate Docker deployment:

### 1. Install Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### 2. Install Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. Deploy with Docker
```bash
cd /home/solo_todo/app
sudo docker-compose up -d
```

## 📊 Monitoring & Maintenance

### 1. Log Monitoring
```bash
# Application logs
sudo journalctl -u solo-todo -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Django logs
sudo tail -f /home/solo_todo/app/logs/django.log
```

### 2. Database Backup
```bash
# Create backup script
sudo nano /home/solo_todo/backup.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/solo_todo/backups"
mkdir -p $BACKUP_DIR

# Database backup
sudo -u postgres pg_dump solo_todo > $BACKUP_DIR/solo_todo_$DATE.sql

# Media files backup
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /home/solo_todo/app/media/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

```bash
sudo chmod +x /home/solo_todo/backup.sh
sudo crontab -e
# Add: 0 2 * * * /home/solo_todo/backup.sh
```

### 3. Service Management
```bash
# Restart application
sudo systemctl restart solo-todo

# Restart nginx
sudo systemctl restart nginx

# Check service status
sudo systemctl status solo-todo
sudo systemctl status nginx
```

## 🔧 Troubleshooting

### Common Issues:

1. **Permission Errors**
```bash
sudo chown -R solo_todo:solo_todo /home/solo_todo/app
sudo chmod -R 755 /home/solo_todo/app
```

2. **Database Connection Issues**
```bash
sudo -u postgres psql -c "SELECT version();"
sudo -u solo_todo python manage.py dbshell --settings=solo_todo.settings_production
```

3. **Static Files Not Loading**
```bash
sudo -u solo_todo python manage.py collectstatic --noinput --settings=solo_todo.settings_production
sudo chown -R www-data:www-data /home/solo_todo/app/staticfiles
```

4. **Nginx Configuration Test**
```bash
sudo nginx -t
sudo systemctl status nginx
```

## 📈 Performance Optimization

### 1. Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX idx_task_user_status ON tasks_task(user_id, status);
CREATE INDEX idx_project_user ON tasks_project(user_id);
CREATE INDEX idx_event_user ON tasks_event(user_id);
```

### 2. Caching (Optional)
```bash
sudo apt install -y redis-server
```

Dodajte u `settings_production.py`:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 3. Gunicorn Optimization
Ažurirajte `gunicorn.conf.py`:
```python
workers = multiprocessing.cpu_count() * 2 + 1
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
```

## 🎉 Success!

Nakon ovih koraka, vaša TODO aplikacija će biti dostupna na:
- HTTP: http://yourdomain.com
- HTTPS: https://yourdomain.com (nakon SSL setup-a)

### Final Checklist:
- [ ] Database je kreiran i konfigurisan
- [ ] Environment variables su postavljeni
- [ ] Gunicorn service je pokrenut
- [ ] Nginx je konfigurisan i pokrenut
- [ ] SSL sertifikat je instaliran (opciono)
- [ ] Backup sistem je postavljen
- [ ] Monitoring je konfigurisan

Aplikacija je sada spremna za produkciju! 🚀
