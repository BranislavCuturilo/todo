# 🚀 Solo TODO - Quick Start Guide

## ⚡ Brzi Deployment (5 minuta)

### 1. Server Setup
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y python3 python3-pip python3-venv nginx postgresql git

# CentOS/RHEL
sudo yum update && sudo yum install -y python3 python3-pip nginx postgresql git
```

### 2. Clone & Setup
```bash
git clone https://github.com/BranislavCuturilo/todo.git
cd todo
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Environment Setup
```bash
cp env.example .env
# Edit .env with your settings
python manage.py generate_secret_key  # Copy the key to .env
```

### 4. Database Setup
```bash
# PostgreSQL
sudo -u postgres psql
CREATE DATABASE todo;
CREATE USER todo WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE todo TO todo;
\q

# Or use SQLite (for testing)
# Edit .env: DB_ENGINE=sqlite3
```

### 5. Deploy
```bash
python manage.py migrate --settings=solo_todo.settings_production
python manage.py collectstatic --noinput --settings=solo_todo.settings_production
python manage.py createsuperuser --settings=solo_todo.settings_production

# Start with Gunicorn
gunicorn --bind 0.0.0.0:8000 solo_todo.wsgi:application
```

### 6. Nginx (Optional)
```bash
sudo cp nginx.conf /etc/nginx/sites-available/solo-todo
sudo ln -s /etc/nginx/sites-available/solo-todo /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

## 🐳 Docker Deployment (2 minute)

```bash
git clone https://github.com/BranislavCuturilo/todo.git
cd todo
cp env.example .env
# Edit .env
docker-compose up -d
```

## 🔧 Production Checklist

- [ ] SECRET_KEY je generisan i postavljen
- [ ] DEBUG=False u .env
- [ ] ALLOWED_HOSTS sadrži vaš domen
- [ ] Database je konfigurisan
- [ ] Static files su kolektovani
- [ ] Superuser je kreiran
- [ ] SSL sertifikat je instaliran (opciono)
- [ ] Backup sistem je postavljen

## 📞 Support

Za detaljne instrukcije pogledajte [`DEPLOYMENT.md`](DEPLOYMENT.md)

## 🎯 Features

✅ **Kompletna privatnost** - Svaki korisnik vidi samo svoje podatke  
✅ **Sigurnost** - HTTPS, security headers, CSRF protection  
✅ **Skalabilnost** - PostgreSQL, Gunicorn, Nginx  
✅ **Monitoring** - Logovi, backup, error tracking  
✅ **Mobile Ready** - Responsive design  
✅ **Canvas Sketching** - Integrisano crtanje  
✅ **Recurring Events** - Ponavljajući događaji  
✅ **Priority Colors** - Boje prema prioritetu  

## 🚀 Ready to Deploy!

Aplikacija je potpuno spremna za produkciju! 🎉
