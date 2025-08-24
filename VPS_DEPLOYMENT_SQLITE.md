# VPS Deployment Instructions - SQLite Version

## Multi-App VPS Setup
This application is configured for deployment on a VPS with multiple Django applications:
- **Port**: 8001 (each app uses incrementing ports: 8001, 8002, 8003...)
- **Domain**: todo.emikon.rs
- **Database**: SQLite (perfect for small to medium workloads)
- **Access**: https://todo.emikon.rs

## Prerequisites
- Ubuntu VPS with Docker and Docker Compose installed
- Domain name pointing to your VPS
- SSH access to your VPS

## Step 1: Server Setup

### Install Docker and Docker Compose
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again for group changes to take effect
exit
# SSH back to your server
```

### Install Nginx (for domain routing)
```bash
sudo apt install nginx -y
sudo systemctl enable nginx
sudo systemctl start nginx
```

## Step 2: Application Deployment

### Clone and Setup Application
```bash
# Clone your repository
git clone <your-repo-url> /opt/todo
cd /opt/todo

# Create backup directory
mkdir -p backup

# Copy your backup database (if you have one)
# scp db.sqlite3 user@your-vps:/opt/todo/backup/db.sqlite3.backup
```

### Configure Environment
```bash
# Copy environment file
cp env.example .env

# Edit environment variables
nano .env
```

Update the `.env` file with your settings:
```env
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=todo.emikon.rs,www.todo.emikon.rs,your-vps-ip
DB_ENGINE=sqlite3
```

**Important**: Replace `your-vps-ip` with your actual VPS IP address.

### Update Nginx Configuration
Edit the `nginx.conf` file:
```bash
nano nginx.conf
```

The server_name is already configured for `todo.emikon.rs`:
```nginx
server_name todo.emikon.rs www.todo.emikon.rs;
```

### Deploy Application
```bash
# Make deployment script executable
chmod +x deploy_sqlite.sh

# Deploy the application
./deploy_sqlite.sh
```

**Expected Output**: The script will show:
- ✅ Backup database found - will be restored on startup (if backup exists)
- ✅ Application is running successfully!
- 🌐 Access your application at: http://localhost:8001

## Step 3: Domain Configuration

### Configure Nginx for Domain Routing (Multi-App Setup)
Since you have multiple Django applications on this VPS, create a new Nginx site configuration:
```bash
sudo nano /etc/nginx/sites-available/todo
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name todo.emikon.rs www.todo.emikon.rs;
    
    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Note**: This configuration routes `todo.emikon.rs` to port 8001. For other applications, use different ports (8002, 8003, etc.) and domains.

**Example for other apps**:
- App 2: `app2.emikon.rs` → port 8002
- App 3: `app3.emikon.rs` → port 8003

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/todo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**Test the configuration**:
```bash
# Test if nginx configuration is valid
sudo nginx -t

# Test if the domain is accessible
curl -I http://todo.emikon.rs
```

### Configure Firewall
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

**Note**: Port 8001 is not exposed externally - it's only accessible through Nginx proxy.

## Step 4: SSL Certificate (Optional but Recommended)

### Install Certbot
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### Get SSL Certificate (Automated)
```bash
# Make SSL setup script executable
chmod +x ssl_setup.sh

# Run automated SSL setup
./ssl_setup.sh
```

**Note**: This script will:
- Install Certbot automatically
- Get SSL certificate for todo.emikon.rs
- Set up automatic renewal
- Use email: baki1812@gmail.com
- Test auto-renewal functionality
- Create renewal hooks for Nginx

After SSL setup, your application will be accessible at `https://todo.emikon.rs`

### Monitor SSL Certificates
```bash
# Make SSL monitor script executable
chmod +x ssl_monitor.sh

# Check SSL certificate status
./ssl_monitor.sh
```

## Step 5: Backup Database

### If you have a backup from previous VPS:
```bash
# Upload your backup to the server
scp /path/to/your/backup/db.sqlite3 user@your-vps:/opt/todo/backup/db.sqlite3.backup

# Restart the application to restore the backup
cd /opt/todo
docker-compose down
docker-compose up -d
```

**Backup Restore Process**:
1. The application automatically detects `backup/db.sqlite3.backup`
2. Copies it to the main database location
3. Runs migrations if needed
4. Starts the application with your data restored

**To upload your backup**:
```bash
# From your local machine, upload the backup
scp /path/to/your/db.sqlite3 user@your-vps:/opt/todo/backup/db.sqlite3.backup
```

## Step 6: Monitoring and Maintenance

### View Application Logs
```bash
cd /opt/todo
docker-compose logs -f
```

**Log locations**:
- Application logs: `docker-compose logs web`
- Nginx logs: `docker-compose logs nginx`
- System logs: `sudo journalctl -u nginx`

### Create Database Backup
```bash
# Create backup of current database
docker-compose exec web cp /app/db.sqlite3 /app/backup/db.sqlite3.backup
docker cp todo_web_1:/app/backup/db.sqlite3.backup ./backup/

# Or create a timestamped backup
docker-compose exec web cp /app/db.sqlite3 /app/backup/db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)

# Download backup to local machine
docker cp todo_web_1:/app/backup/db.sqlite3.backup ./backup/

# Or download to your local machine from VPS
scp user@your-vps:/opt/todo/backup/db.sqlite3.backup ./
```

### Create Superuser (if needed)
```bash
# Create admin user for the application
docker-compose exec web python manage.py createsuperuser
```

**Access admin panel**: https://todo.emikon.rs/admin

### Update Application
```bash
cd /opt/todo
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Note**: This will restart the application and apply any new migrations automatically.

## Troubleshooting

### Check Container Status
```bash
docker-compose ps
```

### Check Application Health
```bash
# Check if the application is responding
curl -I http://localhost:8001

# Check if the domain is working
curl -I http://todo.emikon.rs

# Check if the application is healthy
curl -f http://localhost:8001/ || echo "Application is down"

# Check SSL certificate (after setup)
curl -I https://todo.emikon.rs
```

### Check Application Logs
```bash
docker-compose logs web
docker-compose logs nginx

# Follow logs in real-time
docker-compose logs -f web
docker-compose logs -f nginx
```

### Access Container Shell
```bash
docker-compose exec web bash
```

### Check Database
```bash
# Check if database exists
docker-compose exec web ls -la /app/db.sqlite3

# Check database size
docker-compose exec web du -h /app/db.sqlite3
```

### Restart Services
```bash
docker-compose restart
```

### Monitor Resources
```bash
# Check container resource usage
docker stats

# Check disk usage
df -h

# Check memory usage
free -h

# Check application performance
docker-compose exec web python manage.py check
```

## Security Notes

1. **Change default secret key** in `.env` file
2. **Use strong passwords** for admin users
3. **Keep system updated** regularly
4. **Monitor logs** for suspicious activity
5. **Backup database** regularly
6. **Use SSL certificates** for HTTPS
7. **Firewall configuration** - only allow necessary ports
8. **Regular security updates** for both system and containers

## Performance Optimization

1. **Database**: SQLite is perfect for small to medium workloads
2. **Static files**: Served by Nginx with caching
3. **Gunicorn workers**: Adjust based on your VPS resources
4. **Memory usage**: Monitor with `docker stats`

## Final Checklist

- [ ] Docker and Docker Compose installed
- [ ] Application cloned to `/opt/todo`
- [ ] Backup database uploaded to `backup/db.sqlite3.backup`
- [ ] Environment variables configured in `.env`
- [ ] Nginx site configuration created
- [ ] SSL certificate obtained
- [ ] Application deployed and running
- [ ] Domain accessible at https://todo.emikon.rs
- [ ] Admin user created
- [ ] Regular backup schedule configured

## Support

If you encounter any issues:
1. Check the logs: `docker-compose logs -f`
2. Verify configuration: `docker-compose config`
3. Test connectivity: `curl -I https://todo.emikon.rs`
4. Check system resources: `docker stats`

## Summary

Your TODO application is now configured for:
- **Multi-app VPS deployment** with port 8001
- **Domain routing** via `todo.emikon.rs`
- **SQLite database** with automatic backup restore
- **SSL encryption** for secure access
- **Docker containerization** for easy management
- **Nginx reverse proxy** for optimal performance

The application will be accessible at: **https://todo.emikon.rs**

**Next steps**:
1. Upload your backup database to `backup/db.sqlite3.backup`
2. Follow the deployment instructions above
3. Access your application at https://todo.emikon.rs

**For other applications on the same VPS**:
- Use ports 8002, 8003, 8004, etc.
- Create separate Nginx configurations for each domain
- Follow the same deployment pattern

**Example for next app**:
```bash
# App 2 on port 8002
docker-compose.yml: ports: - "8002:8000"
nginx.conf: proxy_pass http://127.0.0.1:8002
domain: app2.emikon.rs
```

**Port allocation**:
- TODO App: 8001 → todo.emikon.rs
- App 2: 8002 → app2.emikon.rs
- App 3: 8003 → app3.emikon.rs
- App 4: 8004 → app4.emikon.rs

**Important**: Each application should have its own directory and Docker Compose configuration.

**Directory structure on VPS**:
```
/opt/
├── todo/          # Port 8001, Domain: todo.emikon.rs
├── app2/          # Port 8002, Domain: app2.emikon.rs
├── app3/          # Port 8003, Domain: app3.emikon.rs
└── app4/          # Port 8004, Domain: app4.emikon.rs
```

**Nginx sites structure**:
```
/etc/nginx/sites-available/
├── todo           # Routes todo.emikon.rs → 8001
├── app2           # Routes app2.emikon.rs → 8002
├── app3           # Routes app3.emikon.rs → 8003
└── app4           # Routes app4.emikon.rs → 8004
```

**SSL certificates**:
```
/etc/letsencrypt/live/
├── todo.emikon.rs/
├── app2.emikon.rs/
├── app3.emikon.rs/
└── app4.emikon.rs/
```

**Backup structure**:
```
/opt/todo/backup/
├── db.sqlite3.backup
├── db.sqlite3.backup.20241201_143022
└── db.sqlite3.backup.20241202_090015
```

**Monitoring commands**:
```bash
# Check all applications status
for app in todo app2 app3 app4; do
  echo "=== $app ==="
  cd /opt/$app && docker-compose ps
done

# Check all domains
for domain in todo.emikon.rs app2.emikon.rs app3.emikon.rs app4.emikon.rs; do
  echo "=== $domain ==="
  curl -I https://$domain
done
```

**Automated backup script**:
```bash
#!/bin/bash
# /opt/backup_all.sh
for app in todo app2 app3 app4; do
  if [ -d "/opt/$app" ]; then
    echo "Backing up $app..."
    cd /opt/$app
    docker-compose exec web cp /app/db.sqlite3 /app/backup/db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)
  fi
done
```

**Cron job for automated backups**:
```bash
# Add to crontab: crontab -e
0 2 * * * /opt/backup_all.sh >> /var/log/backup.log 2>&1
```

**SSL auto-renewal cron job** (automatically set up by ssl_setup.sh):
```bash
# Check existing SSL renewal jobs
crontab -l | grep certbot

# Manual SSL renewal test
sudo certbot renew --dry-run
```

**System monitoring**:
```bash
# Check system resources
htop
iotop
nethogs

# Check Docker resources
docker system df
docker stats --no-stream
```

**Log rotation**:
```bash
# Configure log rotation for Docker containers
sudo nano /etc/logrotate.d/docker-containers

# Add this content:
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    size=1M
    missingok
    delaycompress
    copytruncate
}
```

**Security hardening**:
```bash
# Update system regularly
sudo apt update && sudo apt upgrade -y

# Check for security updates
sudo unattended-upgrades --dry-run

# Monitor failed login attempts
sudo tail -f /var/log/auth.log | grep "Failed password"
```

**Performance optimization**:
```bash
# Optimize Docker daemon
sudo nano /etc/docker/daemon.json

# Add these settings:
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

**Restart Docker after changes**:
```bash
sudo systemctl restart docker
```

**Final verification**:
```bash
# Test all applications
curl -I https://todo.emikon.rs
docker-compose ps
docker stats --no-stream

# Check system health
df -h
free -h
uptime

# Check SSL certificate
./ssl_monitor.sh
```

**Congratulations!** 🎉
Your TODO application is now fully configured for multi-app VPS deployment with:
- ✅ Port 8001 allocation
- ✅ Domain routing via todo.emikon.rs
- ✅ SQLite database with backup support
- ✅ Docker containerization
- ✅ Nginx reverse proxy
- ✅ SSL encryption with auto-renewal
- ✅ Automated monitoring and backup scripts
- ✅ SSL notifications to baki1812@gmail.com

**Ready for deployment!** 🚀
Follow the step-by-step instructions above to deploy your application on the VPS.

**Next application setup**:
When you're ready to deploy the next application, simply:
1. Clone it to `/opt/app2`
2. Update the port to 8002 in docker-compose.yml
3. Create Nginx configuration for app2.emikon.rs
4. Follow the same deployment pattern

**Template for next app**:
```bash
# Copy this template for each new application
cp -r /opt/todo /opt/app2
cd /opt/app2
# Edit docker-compose.yml: change port to 8002
# Edit nginx.conf: change domain to app2.emikon.rs
# Edit .env: change ALLOWED_HOSTS to app2.emikon.rs
```

**Quick port allocation reference**:
- App 1: 8001 → todo.emikon.rs
- App 2: 8002 → app2.emikon.rs  
- App 3: 8003 → app3.emikon.rs
- App 4: 8004 → app4.emikon.rs
- App 5: 8005 → app5.emikon.rs

**Nginx configuration template for new apps**:
```nginx
server {
    listen 80;
    server_name app2.emikon.rs www.app2.emikon.rs;
    
    location / {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Quick Commands Reference

```bash
# Start application
docker-compose up -d

# Stop application
docker-compose down

# View logs
docker-compose logs -f

# Restart application
docker-compose restart

# Update application
git pull && docker-compose build --no-cache && docker-compose up -d

# Create backup
docker-compose exec web cp /app/db.sqlite3 /app/backup/db.sqlite3.backup

# Check status
docker-compose ps

# Access admin panel
# Open: https://todo.emikon.rs/admin

# Check application status
curl -I https://todo.emikon.rs

# Check SSL certificate
./ssl_monitor.sh

# Emergency restart
docker-compose down && docker-compose up -d
```
