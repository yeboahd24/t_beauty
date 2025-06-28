# Environment Setup for T-Beauty

## Database Configuration

### 1. Create your .env file
```bash
cp config/.env.example .env
```

### 2. Update .env with your PostgreSQL credentials
```env
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# PostgreSQL Database URL
DATABASE_URL=postgresql://username:password@host:port/tbeauty?sslmode=require

ENVIRONMENT=development
DEBUG=true
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 3. Database URL Format
```
postgresql://username:password@host:port/database_name?sslmode=require
```

**Important**: 
- Use `postgresql://` not `postgres://` (SQLAlchemy 2.0+ requirement)
- Include `?sslmode=require` for secure connections
- Use a dedicated database name (e.g., `tbeauty`) to avoid conflicts

## Running the Application

### Option 1: Direct Python
```bash
source venv/bin/activate
python main.py
```

### Option 2: Using startup script
```bash
./run_tbeauty.sh
```

### Option 3: With explicit environment variable
```bash
source venv/bin/activate
export DATABASE_URL="postgresql://user:pass@host:port/tbeauty?sslmode=require"
python main.py
```

## Security Best Practices

1. **Never commit credentials** - `.env` files are gitignored
2. **Use environment variables** in production
3. **Rotate credentials** regularly
4. **Use SSL/TLS** for database connections
5. **Limit database permissions** to what the app needs

## Troubleshooting

### "Can't load plugin: sqlalchemy.dialects:postgres"
- Install PostgreSQL adapter: `pip install psycopg2-binary`
- Check URL format uses `postgresql://` not `postgres://`

### "Connection refused"
- Verify database server is running
- Check host, port, and credentials
- Ensure network connectivity

### Environment variable conflicts
- Clear shell variables: `unset DATABASE_URL`
- Check `.env` file is in project root
- Verify environment variable priority

## Environment Variable Priority

1. Shell environment variables (highest)
2. System environment variables  
3. `.env` file (lowest)

To use `.env` file, ensure no conflicting shell variables are set.