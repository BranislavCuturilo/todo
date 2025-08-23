# 🚀 TODO App Deployment - Step by Step

## 📋 VPS Details
- **IP**: 185.119.90.175
- **User**: root
- **Ports**: 22 (SSH), 3389 (RDP)
- **App Port**: 8001
- **Domain**: todo.emikon.rs

## 🔧 Step 1: Connect to VPS

```bash
ssh root@185.119.90.175
```

## 🔧 Step 2: Download and Run Deployment Script

```bash
# Download the deployment script
curl -o deploy_todo.sh https://raw.githubusercontent.com/BranislavCuturilo/todo/main/deploy_todo.sh

# Make it executable
chmod +x deploy_todo.sh

# Run the deployment
./deploy_todo.sh
```

## 🔧 Step 3: Manual Setup (if script fails)

```bash
# System update
sudo apt update && sudo apt upgrade -y

# Install packages
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib git curl certbot python3-certbot-nginx

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
sudo certbot --nginx -d todo.emikon.rs -d www.todo.emikon.rs --non-interactive --agree-tos --email your-email@example.com

# Permissions
sudo chown -R www-data:www-data /var/www/todo
sudo chmod -R 755 /var/www/todo
```

## 🔧 Step 4: Environment Configuration

Edit the `.env` file:
```bash
nano /var/www/todo/.env
```

Set these values:
```env
SECRET_KEY=your-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=todo.emikon.rs,www.todo.emikon.rs,185.119.90.175,localhost,127.0.0.1
DB_NAME=todo
DB_USER=todo
DB_PASSWORD=todo_password_123
DB_HOST=localhost
DB_PORT=5432
```

Generate SECRET_KEY:
```bash
cd /var/www/todo
source venv/bin/activate
python manage.py generate_secret_key
```

## 🔧 Step 5: DNS Setup

Add these DNS records to your domain provider:
```
Type: A
Name: todo
Value: 185.119.90.175

Type: A
Name: www.todo
Value: 185.119.90.175
```

## 🔧 Step 6: GitHub Actions Setup

1. Go to: https://github.com/BranislavCuturilo/todo/settings/secrets/actions
2. Add these secrets:
   - `VPS_HOST`: 185.119.90.175
   - `VPS_USERNAME`: root
   - `VPS_SSH_KEY`: Your private SSH key
   - `VPS_PORT`: 22

## 🔧 Step 7: Verification

```bash
# Check services
sudo systemctl status todo
sudo systemctl status nginx

# Check if port 8001 is listening
sudo netstat -tlnp | grep :8001

# Check logs
sudo journalctl -u todo -f
sudo tail -f /var/log/nginx/access.log

# Test website
curl -I https://todo.emikon.rs
```

## 🔧 Step 8: SSL Certificate Renewal

Add to crontab for automatic SSL renewal:
```bash
sudo crontab -e
```

Add this line:
```
0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔧 Step 9: Backup Setup

The backup script is already created at `/var/www/todo/backup.sh` and added to crontab.

Manual backup:
```bash
/var/www/todo/backup.sh
```

## 🔧 Step 10: Maintenance Commands

```bash
# Restart services
sudo systemctl restart todo
sudo systemctl restart nginx

# View logs
sudo journalctl -u todo -f
sudo tail -f /var/log/nginx/error.log

# Update app manually
cd /var/www/todo
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --settings=solo_todo.settings_production
python manage.py collectstatic --noinput --settings=solo_todo.settings_production
sudo systemctl restart todo
```

## 🔧 Step 11: Troubleshooting

```bash
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

After completing these steps, your TODO app will be available at:
- **https://todo.emikon.rs**
- **https://www.todo.emikon.rs**

Every push to main branch will automatically deploy to your VPS! 🚀

## 📊 Monitoring

- **App Status**: `sudo systemctl status todo`
- **Nginx Status**: `sudo systemctl status nginx`
- **App Logs**: `sudo journalctl -u todo -f`
- **Nginx Logs**: `sudo tail -f /var/log/nginx/access.log`
- **Backup Logs**: Check `/var/www/todo/backups/` directory

