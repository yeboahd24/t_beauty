# Production Deployment Guide

This guide explains how to deploy T-Beauty in production environments where you can't rely on gitignored files.

## 🚀 Quick Start

### Option 1: Using start_production.py (Recommended)

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd t-beauty

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file with your production settings
cat > .env << EOF
SECRET_KEY=your-super-secret-production-key-here
DATABASE_URL=postgresql://username:password@host:port/database?sslmode=require
ENVIRONMENT=production
DEBUG=false
EOF

# 5. Start the application
python start_production.py
```

### Option 2: Using Environment Variables

```bash
# Set environment variables
export SECRET_KEY="your-super-secret-production-key"
export DATABASE_URL="postgresql://username:password@host:port/database?sslmode=require"
export ENVIRONMENT="production"
export DEBUG="false"

# Start the application
python start_production.py
```

### Option 3: Using the Deployment Script

```bash
# Run the automated deployment script
chmod +x scripts/deploy.sh
./scripts/deploy.sh

# This will create run_production.sh which you can then use
./run_production.sh
```

## 📋 Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key | `your-super-secret-key-min-32-chars` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `ENVIRONMENT` | Environment name | `production` |
| `DEBUG` | Debug mode | `false` |

## 🔧 Production Configuration

### Generate a Secure Secret Key

```python
# Run this to generate a secure secret key
import secrets
print(secrets.token_urlsafe(32))
```

### Database URL Format

```
postgresql://username:password@hostname:port/database_name?sslmode=require
```

## 🐳 Docker Deployment

If you're using Docker, you can pass environment variables:

```bash
docker run -e SECRET_KEY="your-key" \
           -e DATABASE_URL="postgresql://..." \
           -p 8000:8000 \
           your-tbeauty-image
```

## 🌐 Reverse Proxy Setup

For production, use a reverse proxy like Nginx:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔒 Security Considerations

1. **Never commit secrets** to version control
2. **Use strong SECRET_KEY** (minimum 32 characters)
3. **Enable SSL** for database connections (`sslmode=require`)
4. **Use HTTPS** in production
5. **Set DEBUG=false** in production
6. **Restrict CORS origins** to your actual domains

## 📊 Health Checks

The application provides health check endpoints:

- `GET /health` - Basic health check
- `GET /` - Application info

## 🚨 Troubleshooting

### Common Issues

1. **Missing .env file**: Use environment variables instead
2. **Database connection failed**: Check DATABASE_URL format
3. **Permission denied**: Make sure scripts are executable (`chmod +x`)

### Logs

Check application logs for detailed error information:

```bash
python start_production.py 2>&1 | tee app.log
```

## 📝 Files Safe to Commit

✅ **Safe to commit:**
- `start_production.py` - Production startup script
- `scripts/deploy.sh` - Deployment automation
- `config/.env.example` - Environment template
- `PRODUCTION_DEPLOYMENT.md` - This guide

❌ **Never commit:**
- `.env` - Contains secrets
- `run_tbeauty.sh` - May contain credentials
- Any file with actual passwords/keys

## 🎯 Best Practices

1. **Use CI/CD pipelines** to automate deployment
2. **Store secrets** in your platform's secret management (AWS Secrets Manager, Azure Key Vault, etc.)
3. **Monitor application** health and performance
4. **Backup database** regularly
5. **Update dependencies** regularly for security patches

## 📞 Support

If you encounter issues:

1. Check the logs for error messages
2. Verify all environment variables are set correctly
3. Test database connectivity separately
4. Review this deployment guide

---

**Remember**: The `start_production.py` script is designed to be safe for version control and will work in any production environment where you can set environment variables or create a `.env` file.