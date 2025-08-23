# 🚀 Complete TODO App Deployment Commands

## 📋 All Terminal Commands You Need

### 1. VPS Server Setup (One-time)

```bash
# Connect to your VPS
ssh root@your-vps-ip

# Download and run automatic setup
curl -o setup.sh https://raw.githubusercontent.com/BranislavCuturilo/todo/main/setup.sh
chmod +x setup.sh
./setup.sh
```

### 2. Manual Setup (if automatic fails)

```bash
# System update
sudo apt update && sudo apt upgrade -y

# Install packages
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib git curl

# Create app directory
sudo mkdir -p /var/www/todo
sudo chown $USER:$USER /var/www/todo

# Clone repository
cd /var/www/todo
git clone https://github.com/BranislavCuturilo/todo.git .

# Python setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Environment setup
cp env.example .env
nano .env  # Edit with your settings

# Database setup
sudo -u postgres psql << EOF
CREATE DATABASE todo;
CREATE USER todo WITH PASSWORD 'todo_password_123';
GRANT ALL PRIVILEGES ON DATABASE todo TO todo;
ALTER USER todo CREATEDB;
\q
EOF

# Django setup
python manage.py migrate --settings=solo_todo.settings_production
python manage.py createsuperuser --settings=solo_todo.settings_production
python manage.py collectstatic --noinput --settings=solo_todo.settings_production

# Gunicorn service
sudo cp solo-todo.service /etc/systemd/system/todo.service
sudo systemctl daemon-reload
sudo systemctl enable todo
sudo systemctl start todo

# Nginx setup
sudo cp nginx.conf /etc/nginx/sites-available/todo
sudo ln -sf /etc/nginx/sites-available/todo /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# SSL certificate
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d todo.emikon.rs -d www.todo.emikon.rs --non-interactive --agree-tos --email your-email@example.com

# Permissions
sudo chown -R www-data:www-data /var/www/todo
sudo chmod -R 755 /var/www/todo
```

### 3. GitHub Actions Setup

#### Add these secrets to your GitHub repository:
- Go to: https://github.com/BranislavCuturilo/todo/settings/secrets/actions
- Add secrets:
  - `VPS_HOST`: Your VPS IP
  - `VPS_USERNAME`: root (or your username)
  - `VPS_SSH_KEY`: Your private SSH key
  - `VPS_PORT`: 22 (or your SSH port)

### 4. DNS Setup

Add these records to your domain provider:
```
Type: A
Name: todo
Value: your-vps-ip

Type: A
Name: www.todo  
Value: your-vps-ip
```

### 5. Verification Commands

```bash
# Check services
sudo systemctl status todo
sudo systemctl status nginx

# Check logs
sudo journalctl -u todo -f
sudo tail -f /var/log/nginx/access.log

# Test website
curl -I https://todo.emikon.rs
```

### 6. Maintenance Commands

```bash
# Restart services
sudo systemctl restart todo
sudo systemctl restart nginx

# View logs
sudo journalctl -u todo -f
sudo tail -f /var/log/nginx/error.log

# Manual backup
/var/www/todo/backup.sh

# Update app manually
cd /var/www/todo
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --settings=solo_todo.settings_production
python manage.py collectstatic --noinput --settings=solo_todo.settings_production
sudo systemctl restart todo
```

### 7. Troubleshooting

```bash
# Check if port 8000 is listening
sudo netstat -tlnp | grep :8000

# Check nginx configuration
sudo nginx -t

# Check app logs
sudo journalctl -u todo -n 50

# Check permissions
ls -la /var/www/todo/
sudo chown -R www-data:www-data /var/www/todo

# Restart everything
sudo systemctl restart todo
sudo systemctl restart nginx
```

## 🎯 Success!

After running these commands, your app will be available at:
- https://todo.emikon.rs
- https://www.todo.emikon.rs

Every push to main branch will automatically deploy! 🚀

