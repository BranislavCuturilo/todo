#!/bin/bash

# Deploy TODO application to production
echo "🚀 Deploying TODO application..."

# Navigate to project directory
cd /var/www/todo

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate --settings=solo_todo.settings_production

# Create superuser if needed (uncomment if needed)
# echo "👤 Creating superuser..."
# python manage.py createsuperuser --settings=solo_todo.settings_production

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --settings=solo_todo.settings_production

# Clear old service worker caches by updating cache version
echo "🧹 Clearing old caches..."
# The service worker cache will be automatically updated with the new version

# Restart the application
echo "🔄 Restarting application..."
sudo systemctl restart todo

# Wait a moment for the service to start
sleep 3

# Check if the application is running
echo "🔍 Checking application status..."
if sudo systemctl is-active --quiet todo; then
    echo "✅ Application is running successfully!"
    echo "🌐 Application URL: http://your-domain.com"
else
    echo "❌ Application failed to start!"
    sudo systemctl status todo
    exit 1
fi

# Test if the application is responding
echo "🧪 Testing application response..."
sleep 5
if curl -f http://localhost:8001/ > /dev/null 2>&1; then
    echo "✅ Application is responding correctly!"
else
    echo "❌ Application is not responding!"
    exit 1
fi

echo "🎉 Deployment completed successfully!"
echo "💡 If you still see 'solo todo' in the browser, try:"
echo "   1. Hard refresh (Ctrl+F5 or Cmd+Shift+R)"
echo "   2. Clear browser cache"
echo "   3. Open in incognito/private mode"


