#!/bin/bash

# TODO App Deployment Script
# Run this script on your VPS server to set up the application

set -e  # Exit on any error

echo "🚀 Starting TODO App deployment..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "🔧 Installing required packages..."
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib git curl

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /var/www/todo
sudo chown $USER:$USER /var/www/todo

# Clone repository
echo "📥 Cloning repository..."
cd /var/www/todo
git clone https://github.com/BranislavCuturilo/todo.git .

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Set up environment variables
echo "⚙️ Setting up environment variables..."
cp env.example .env
echo "Please edit .env file with your settings:"
echo "nano .env"

# Set up PostgreSQL
echo "🗄️ Setting up PostgreSQL database..."
sudo -u postgres psql << EOF
CREATE DATABASE todo;
CREATE USER todo WITH PASSWORD 'todo_password_123';
GRANT ALL PRIVILEGES ON DATABASE todo TO todo;
ALTER USER todo CREATEDB;
\q
EOF

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate --settings=solo_todo.settings_production

# Create superuser
echo "👤 Creating superuser..."
python manage.py createsuperuser --settings=solo_todo.settings_production

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --settings=solo_todo.settings_production

# Set up Gunicorn service
echo "🔧 Setting up Gunicorn service..."
sudo cp solo-todo.service /etc/systemd/system/todo.service
sudo systemctl daemon-reload
sudo systemctl enable todo
sudo systemctl start todo

# Set up Nginx
echo "🌐 Setting up Nginx..."
sudo cp nginx.conf /etc/nginx/sites-available/todo
sudo ln -sf /etc/nginx/sites-available/todo /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Set up SSL with Let's Encrypt
echo "🔒 Setting up SSL certificate..."
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d todo.emikon.rs -d www.todo.emikon.rs --non-interactive --agree-tos --email your-email@example.com

# Set proper permissions
echo "🔐 Setting proper permissions..."
sudo chown -R www-data:www-data /var/www/todo
sudo chmod -R 755 /var/www/todo

# Create backup script
echo "💾 Setting up backup script..."
sudo tee /var/www/todo/backup.sh > /dev/null << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/www/todo/backups"
mkdir -p $BACKUP_DIR

# Database backup
sudo -u postgres pg_dump todo > $BACKUP_DIR/todo_$DATE.sql

# Media files backup
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/todo/media/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

sudo chmod +x /var/www/todo/backup.sh

# Add backup to crontab
echo "⏰ Setting up automatic backups..."
(crontab -l 2>/dev/null; echo "0 2 * * * /var/www/todo/backup.sh") | crontab -

echo "✅ Deployment completed successfully!"
echo ""
echo "🌐 Your application is now available at:"
echo "   http://todo.emikon.rs"
echo "   https://todo.emikon.rs"
echo ""
echo "🔧 Useful commands:"
echo "   sudo systemctl status todo    # Check app status"
echo "   sudo systemctl restart todo   # Restart app"
echo "   sudo systemctl status nginx   # Check nginx status"
echo "   sudo journalctl -u todo -f    # View app logs"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env file with your settings"
echo "2. Update DNS records to point todo.emikon.rs to this server"
echo "3. Test the application"
echo ""
echo "🎉 Deployment complete!"






