# 🚀 VPS Setup Instructions for TODO App

## 📋 Terminal Commands to Run on VPS

### 1. Connect to your VPS
```bash
ssh root@your-vps-ip
```

### 2. Download and run setup script
```bash
# Download the setup script
curl -o setup.sh https://raw.githubusercontent.com/BranislavCuturilo/todo/main/setup.sh

# Make it executable
chmod +x setup.sh

# Run the setup
./setup.sh
```

### 3. Manual setup (if script fails)
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install packages
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib git curl

# Create directory
sudo mkdir -p /var/www/todo
sudo chown $USER:$USER /var/www/todo

# Clone repository
cd /var/www/todo
git clone https://github.com/BranislavCuturilo/todo.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp env.example .env
nano .env  # Edit with your settings

# Setup database
sudo -u postgres psql << EOF
CREATE DATABASE todo;
CREATE USER todo WITH PASSWORD 'todo_password_123';
GRANT ALL PRIVILEGES ON DATABASE todo TO todo;
ALTER USER todo CREATEDB;
\q
EOF

# Run migrations
python manage.py migrate --settings=solo_todo.settings_production

# Create superuser
python manage.py createsuperuser --settings=solo_todo.settings_production

# Collect static files
python manage.py collectstatic --noinput --settings=solo_todo.settings_production

# Setup Gunicorn service
sudo cp solo-todo.service /etc/systemd/system/todo.service
sudo systemctl daemon-reload
sudo systemctl enable todo
sudo systemctl start todo

# Setup Nginx
sudo cp nginx.conf /etc/nginx/sites-available/todo
sudo ln -sf /etc/nginx/sites-available/todo /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Setup SSL
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d todo.emikon.rs -d www.todo.emikon.rs --non-interactive --agree-tos --email your-email@example.com

# Set permissions
sudo chown -R www-data:www-data /var/www/todo
sudo chmod -R 755 /var/www/todo
```

## 🔧 GitHub Actions Setup

### 1. Add GitHub Secrets
Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:
- `VPS_HOST`: Your VPS IP address
- `VPS_USERNAME`: Your VPS username (usually root)
- `VPS_SSH_KEY`: Your private SSH key
- `VPS_PORT`: SSH port (usually 22)

### 2. Test deployment
Push to main branch:
```bash
git add .
git commit -m "Initial deployment"
git push origin main
```

## 🌐 DNS Setup

Add these DNS records to your domain provider:
```
Type: A
Name: todo
Value: your-vps-ip

Type: A  
Name: www.todo
Value: your-vps-ip
```

## 🔍 Verification

### Check if everything is working:
```bash
# Check app status
sudo systemctl status todo

# Check nginx status  
sudo systemctl status nginx

# Check logs
sudo journalctl -u todo -f

# Test website
curl -I https://todo.emikon.rs
```

### Useful commands:
```bash
# Restart app
sudo systemctl restart todo

# Restart nginx
sudo systemctl restart nginx

# View app logs
sudo journalctl -u todo -f

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Manual backup
/var/www/todo/backup.sh
```

## 🎯 Success!

Your TODO app should now be available at:
- https://todo.emikon.rs
- https://www.todo.emikon.rs

Every push to main branch will automatically deploy to your VPS! 🚀



