# Simple Deployment Guide (Without Docker)

This guide shows how to run T-Beauty using `python main.py` while automatically loading credentials from `.env` file.

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd t-beauty

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy from example
cp config/.env.example .env

# Edit with your settings
nano .env  # or use your preferred editor
```

Example `.env` file:
```env
SECRET_KEY=your-super-secret-key-min-32-characters
DATABASE_URL=postgresql://username:password@host:port/database?sslmode=require
ENVIRONMENT=production
DEBUG=false
BACKEND_CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### 3. Start the Application

Now you can simply run:

```bash
python main.py
```

The `main.py` script will automatically:
- ✅ Load environment variables from `.env` file
- ✅ Validate required variables are set
- ✅ Show configuration (with masked credentials)
- ✅ Start the FastAPI application

## 🎯 Alternative Running Methods

### Method 1: Direct main.py (Recommended)
```bash
python main.py
```

### Method 2: Using run.py wrapper
```bash
python run.py
```

### Method 3: Using start_production.py
```bash
python start_production.py
```

### Method 4: Manual environment variables
```bash
export SECRET_KEY="your-secret-key"
export DATABASE_URL="postgresql://..."
python main.py
```

## 📋 Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key (32+ chars) | `your-super-secure-secret-key-here` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |

## 🔧 Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment name | `development` |
| `DEBUG` | Debug mode | `true` |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins | `["*"]` |

## 🛠️ Database Setup

### If using existing PostgreSQL server:
```bash
# Make sure your DATABASE_URL points to existing PostgreSQL
# The application will create tables automatically
python main.py
```

### If you need to setup PostgreSQL:

#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo -u postgres createuser --interactive
sudo -u postgres createdb tbeauty
```

#### On macOS:
```bash
brew install postgresql
brew services start postgresql
createdb tbeauty
```

#### On Windows:
Download and install PostgreSQL from https://www.postgresql.org/download/windows/

## 🔒 Security Configuration

### Generate Secure Secret Key
```python
# Run this to generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Production Settings
For production, make sure to set:
```env
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-actual-secure-key-32-chars-minimum
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
BACKEND_CORS_ORIGINS=https://yourdomain.com
```

## 🌐 Reverse Proxy Setup (Production)

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Apache Configuration
```apache
<VirtualHost *:80>
    ServerName yourdomain.com
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
    ProxyPreserveHost On
</VirtualHost>
```

## 🔄 Process Management (Production)

### Using systemd (Linux)
Create `/etc/systemd/system/tbeauty.service`:

```ini
[Unit]
Description=T-Beauty Business Management System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/tbeauty
Environment=PATH=/path/to/tbeauty/venv/bin
ExecStart=/path/to/tbeauty/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable tbeauty
sudo systemctl start tbeauty
```

### Using PM2 (Node.js process manager)
```bash
# Install PM2
npm install -g pm2

# Start application
pm2 start main.py --name tbeauty --interpreter python3

# Save PM2 configuration
pm2 save
pm2 startup
```

### Using supervisor
Create `/etc/supervisor/conf.d/tbeauty.conf`:

```ini
[program:tbeauty]
command=/path/to/tbeauty/venv/bin/python main.py
directory=/path/to/tbeauty
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/tbeauty.log
```

## 📊 Monitoring & Logs

### Check Application Status
```bash
curl http://localhost:8000/health
```

### View Logs
The application logs to stdout. To save logs:
```bash
python main.py 2>&1 | tee app.log
```

### Log Rotation
For production, use logrotate:
```bash
# /etc/logrotate.d/tbeauty
/var/log/tbeauty.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Missing .env file**
   ```
   No .env file found. Using system environment variables.
   ERROR: Missing required environment variables:
   ```
   **Solution**: Create `.env` file with required variables

2. **Database connection failed**
   ```
   sqlalchemy.exc.OperationalError: could not connect to server
   ```
   **Solution**: Check DATABASE_URL and ensure PostgreSQL is running

3. **Permission denied**
   ```
   PermissionError: [Errno 13] Permission denied
   ```
   **Solution**: Check file permissions and user privileges

4. **Port already in use**
   ```
   OSError: [Errno 98] Address already in use
   ```
   **Solution**: Kill existing process or change port

### Debug Mode
To run in debug mode:
```bash
# Set in .env file
DEBUG=true

# Or as environment variable
DEBUG=true python main.py
```

## 📝 Files Overview

| File | Purpose | Safe to Commit? |
|------|---------|-----------------|
| `main.py` | Main application entry point | ✅ Yes |
| `run.py` | Alternative runner script | ✅ Yes |
| `start_production.py` | Production startup script | ✅ Yes |
| `.env` | Environment variables | ❌ No (gitignored) |
| `config/.env.example` | Environment template | ✅ Yes |

## 🎯 Best Practices

1. **Always use `.env` file** for configuration
2. **Never commit secrets** to version control
3. **Use strong SECRET_KEY** (minimum 32 characters)
4. **Enable SSL** for database connections in production
5. **Use process manager** for production deployments
6. **Setup reverse proxy** for production
7. **Monitor application** health and logs
8. **Regular backups** of database

---

**Remember**: The updated `main.py` automatically loads your `.env` file, so you can simply run `python main.py` and it will work with your existing configuration!