# T-Beauty Deployment Guide

## Quick Start for New Environments

### 1. Clone and Setup
```bash
git clone https://github.com/yeboahd24/t_beauty.git
cd t_beauty
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configure Database
Choose one of these methods:

#### Method A: Environment Variables (Production)
```bash
export DATABASE_URL="postgresql://username:password@host:port/tbeauty?sslmode=require"
export SECRET_KEY="your-production-secret-key"
export ENVIRONMENT="production"
export DEBUG="false"
python main.py
```

#### Method B: .env File (Development/Staging)
```bash
cp config/.env.example .env
# Edit .env with your credentials
nano .env
python main.py
```

#### Method C: Startup Script
```bash
cp run_tbeauty.sh.example run_tbeauty.sh
# Edit run_tbeauty.sh with your credentials
nano run_tbeauty.sh
chmod +x run_tbeauty.sh
./run_tbeauty.sh
```

## Production Deployment

### Docker Deployment (Recommended)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  tbeauty:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/tbeauty
      - SECRET_KEY=your-secret-key
      - ENVIRONMENT=production
      - DEBUG=false
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: tbeauty
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Run with:
```bash
docker-compose up -d
```

### Cloud Platform Deployment

#### Heroku
```bash
# Install Heroku CLI
heroku create your-app-name
heroku addons:create heroku-postgresql:mini
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set ENVIRONMENT="production"
heroku config:set DEBUG="false"
git push heroku main
```

#### Railway
```bash
# Connect your GitHub repo to Railway
# Set environment variables in Railway dashboard:
# DATABASE_URL, SECRET_KEY, ENVIRONMENT=production, DEBUG=false
```

#### DigitalOcean App Platform
```yaml
# app.yaml
name: tbeauty
services:
- name: web
  source_dir: /
  github:
    repo: yeboahd24/t_beauty
    branch: main
  run_command: python main.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DATABASE_URL
    value: postgresql://user:pass@host:port/tbeauty
  - key: SECRET_KEY
    value: your-secret-key
  - key: ENVIRONMENT
    value: production
  - key: DEBUG
    value: false
```

### Traditional Server Deployment

#### Using systemd (Linux)

Create `/etc/systemd/system/tbeauty.service`:
```ini
[Unit]
Description=T-Beauty Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/tbeauty
Environment=DATABASE_URL=postgresql://user:pass@host:port/tbeauty
Environment=SECRET_KEY=your-secret-key
Environment=ENVIRONMENT=production
Environment=DEBUG=false
ExecStart=/var/www/tbeauty/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable tbeauty
sudo systemctl start tbeauty
sudo systemctl status tbeauty
```

#### Using PM2 (Node.js Process Manager)
```bash
npm install -g pm2
pm2 start ecosystem.config.js
```

Create `ecosystem.config.js`:
```javascript
module.exports = {
  apps: [{
    name: 'tbeauty',
    script: 'python',
    args: 'main.py',
    cwd: '/path/to/tbeauty',
    env: {
      DATABASE_URL: 'postgresql://user:pass@host:port/tbeauty',
      SECRET_KEY: 'your-secret-key',
      ENVIRONMENT: 'production',
      DEBUG: 'false'
    }
  }]
}
```

### Nginx Reverse Proxy

Create `/etc/nginx/sites-available/tbeauty`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/tbeauty /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Environment Variables Reference

### Required
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key (generate with `openssl rand -hex 32`)

### Optional
- `ENVIRONMENT`: `development` | `staging` | `production` (default: `development`)
- `DEBUG`: `true` | `false` (default: `true`)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiry (default: `30`)
- `BACKEND_CORS_ORIGINS`: Comma-separated allowed origins

### Example Production Values
```bash
DATABASE_URL="postgresql://user:pass@host:5432/tbeauty?sslmode=require"
SECRET_KEY="your-32-character-secret-key-here"
ENVIRONMENT="production"
DEBUG="false"
ACCESS_TOKEN_EXPIRE_MINUTES="60"
BACKEND_CORS_ORIGINS="https://yourdomain.com,https://app.yourdomain.com"
```

## Security Checklist for Production

- [ ] Use strong, unique SECRET_KEY
- [ ] Set DEBUG=false
- [ ] Use HTTPS/SSL certificates
- [ ] Restrict CORS origins
- [ ] Use environment variables, not .env files
- [ ] Enable database SSL (sslmode=require)
- [ ] Set up proper firewall rules
- [ ] Use reverse proxy (Nginx/Apache)
- [ ] Set up monitoring and logging
- [ ] Regular security updates

## Troubleshooting

### "No such file or directory: ./run_tbeauty.sh"
- The script is gitignored for security
- Use environment variables or create from example
- See deployment methods above

### Database connection issues
- Verify DATABASE_URL format: `postgresql://user:pass@host:port/db`
- Check network connectivity
- Ensure PostgreSQL is running
- Verify credentials

### Permission denied
- Check file permissions: `chmod +x run_tbeauty.sh`
- Verify user has access to files
- Check systemd service user

Your T-Beauty application is now ready for production deployment! 🚀