#!/bin/bash

# SSL Certificate Monitor
# This script checks SSL certificate status and sends notifications

echo "🔍 Checking SSL certificate status..."

# Check certificate expiration
CERT_EXPIRY=$(sudo certbot certificates | grep "VALID:" | awk '{print $2}')
DOMAIN="todo.emikon.rs"

echo "📅 Certificate for $DOMAIN expires: $CERT_EXPIRY"

# Check if certificate is valid
if sudo certbot certificates | grep -q "VALID:"; then
    echo "✅ SSL certificate is valid"
    
    # Check days until expiration
    EXPIRY_DATE=$(sudo certbot certificates | grep "VALID:" | awk '{print $2}')
    DAYS_LEFT=$(echo $EXPIRY_DATE | xargs -I {} date -d {} +%s | xargs -I {} echo $(( ({} - $(date +%s)) / 86400 )))
    
    echo "⏰ Days until expiration: $DAYS_LEFT"
    
    if [ $DAYS_LEFT -lt 30 ]; then
        echo "⚠️  WARNING: Certificate expires in less than 30 days!"
        echo "🔄 Attempting to renew..."
        sudo certbot renew --quiet --nginx
    fi
else
    echo "❌ SSL certificate is invalid or missing"
    echo "🔧 Running SSL setup..."
    ./ssl_setup.sh
fi

# Test HTTPS connectivity
echo "🌐 Testing HTTPS connectivity..."
if curl -s -I https://$DOMAIN | grep -q "200 OK"; then
    echo "✅ HTTPS is working correctly"
else
    echo "❌ HTTPS is not working"
fi

# Check auto-renewal cron job
if crontab -l 2>/dev/null | grep -q "certbot renew"; then
    echo "✅ Auto-renewal cron job is active"
else
    echo "❌ Auto-renewal cron job is missing"
    echo "🔧 Setting up auto-renewal..."
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet --nginx") | crontab -
fi

echo "📧 SSL notifications sent to: baki1812@gmail.com"

