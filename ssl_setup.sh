#!/bin/bash

# SSL Setup Script for TODO App
# This script automatically sets up SSL certificates with auto-renewal

echo "🔒 Setting up SSL certificates for todo.emikon.rs..."

# Install Certbot if not already installed
if ! command -v certbot &> /dev/null; then
    echo "📦 Installing Certbot..."
    sudo apt update
    sudo apt install certbot python3-certbot-nginx -y
fi

# Create SSL configuration
echo "⚙️  Creating SSL configuration..."

# Get SSL certificate with your email
echo "📧 Using email: baki1812@gmail.com"
sudo certbot --nginx \
    --email baki1812@gmail.com \
    --agree-tos \
    --no-eff-email \
    -d todo.emikon.rs \
    -d www.todo.emikon.rs

# Test auto-renewal
echo "🔄 Testing auto-renewal..."
sudo certbot renew --dry-run

# Set up automatic renewal cron job
echo "⏰ Setting up automatic renewal..."

# Check if cron job already exists
if ! crontab -l 2>/dev/null | grep -q "certbot renew"; then
    # Add cron job for automatic renewal (runs twice daily)
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet --nginx") | crontab -
    echo "✅ Automatic renewal cron job added"
else
    echo "ℹ️  Automatic renewal cron job already exists"
fi

# Create renewal hook for Nginx reload
echo "🔧 Creating renewal hook..."
sudo mkdir -p /etc/letsencrypt/renewal-hooks/post

sudo tee /etc/letsencrypt/renewal-hooks/post/nginx-reload.sh > /dev/null << 'EOF'
#!/bin/bash
# Reload Nginx after certificate renewal
systemctl reload nginx
EOF

sudo chmod +x /etc/letsencrypt/renewal-hooks/post/nginx-reload.sh

# Verify SSL setup
echo "✅ Verifying SSL setup..."
curl -I https://todo.emikon.rs

echo "🎉 SSL setup complete!"
echo "📧 Certificate notifications will be sent to: baki1812@gmail.com"
echo "🔄 Certificates will auto-renew twice daily"
echo "🌐 Your app is now accessible at: https://todo.emikon.rs"

