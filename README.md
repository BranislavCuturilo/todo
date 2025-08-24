# TODO - Enhanced Task Management System

A comprehensive task management application built with Django, featuring recurring events, priority-based task colors, canvas sketching, and user authentication.

## Features

- **Task Management**: Create, edit, delete, and organize tasks with priorities
- **Recurring Events**: Set up events that repeat daily, weekly, monthly, or yearly
- **Calendar View**: Visual calendar with recurring events and task colors
- **Canvas Sketching**: Draw and save sketches, assign them to projects or tasks
- **Project Organization**: Group tasks into projects for better organization
- **User Authentication**: Secure login, register, and logout functionality
- **Priority Colors**: Visual task prioritization with color coding
- **Responsive Design**: Works on desktop, tablet, and mobile devices
#
## Quick Start with Docker (SQLite)

### Prerequisites
- Docker and Docker Compose installed
- Backup database file (optional)

### Deployment Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd todo
   ```

2. **Add your backup database (optional)**
   ```bash
   # Copy your backup database to the backup directory
   cp /path/to/your/db.sqlite3 backup/db.sqlite3.backup
   ```

3. **Configure environment variables**
   ```bash
   cp env.example .env
   # Edit .env file with your settings
   ```

4. **Deploy with Docker**
   ```bash
   # Option 1: Use deployment script
   chmod +x deploy_sqlite.sh
   ./deploy_sqlite.sh
   
   # Option 2: Manual deployment
   docker-compose up -d
   ```

5. **Access the application**
   - Application: http://localhost:8001
   - Admin panel: http://localhost:8001/admin
   - Production: https://todo.emikon.rs

### SSL Certificate Setup (Production)
```bash
# Automated SSL setup with auto-renewal
chmod +x ssl_setup.sh
./ssl_setup.sh

# Monitor SSL certificates
chmod +x ssl_monitor.sh
./ssl_monitor.sh
```

**SSL Features**:
- ✅ Automatic certificate generation
- ✅ Auto-renewal every 90 days
- ✅ Email notifications to baki1812@gmail.com
- ✅ Nginx integration
- ✅ HTTPS redirect

### Backup Database Support

The application automatically detects and restores backup databases:
- Place your `db.sqlite3` backup file in the `backup/` directory
- Rename it to `db.sqlite3.backup`
- The application will automatically restore it on startup

## Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Create superuser: `python manage.py createsuperuser`
5. Run the server: `python manage.py runserver`

## Production Deployment

See `VPS_DEPLOYMENT_SQLITE.md` for detailed production deployment instructions.

## Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild containers
docker-compose build --no-cache

# Access container shell
docker-compose exec web bash
```

## SSL Management

```bash
# Check SSL certificate status
./ssl_monitor.sh

# Manual SSL renewal test
sudo certbot renew --dry-run

# View SSL certificates
sudo certbot certificates
```


