# Celery Setup Guide for T-Beauty

## Prerequisites

1. **Activate Virtual Environment**
   ```bash
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Redis**
   ```bash
   # Option A: Using Docker
   docker run -d -p 6379:6379 redis:7-alpine
   
   # Option B: If Redis is installed locally
   redis-server
   ```

## Starting Celery Worker

### Method 1: Using the provided script (Recommended)
```bash
# Make sure virtual environment is activated first!
source venv/bin/activate

# Run the script
./start_celery.sh
```

### Method 2: Manual command
```bash
# Activate virtual environment
source venv/bin/activate

# Set Python path and start Celery
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
celery -A celery_app worker --loglevel=info
```

## Testing the Setup

1. **Start Redis** (in terminal 1)
2. **Start Celery Worker** (in terminal 2)
   ```bash
   source venv/bin/activate
   ./start_celery.sh
   ```
3. **Start FastAPI** (in terminal 3)
   ```bash
   source venv/bin/activate
   python main.py
   ```

## Verifying Celery is Working

You should see output like this when Celery starts:
```
✅ Virtual environment detected: /path/to/your/venv
Starting Celery worker...

 -------------- celery@hostname v5.3.4 (emerald-rush)
--- ***** ----- 
-- ******* ---- Linux-5.x.x-x86_64
- *** --- * --- 
- ** ---------- [config]
- ** ---------- .> app:         t_beauty:0x...
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     redis://localhost:6379/0
- *** --- * --- .> concurrency: 4 (prefork)
-- ******* ---- .> task events: OFF
--- ***** ----- 
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery

[tasks]
  . src.app.tasks.customer_tasks.bulk_import_customers_task

[INFO/MainProcess] Connected to redis://localhost:6379/0
[INFO/MainProcess] mingle: searching for neighbors
[INFO/MainProcess] mingle: all alone
[INFO/MainProcess] celery@hostname ready.
```

## Testing Bulk Import

```bash
# Upload CSV file
curl -X POST "http://localhost:8000/api/v1/customers/bulk-import" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "csv_file=@docs/customers.csv"

# Check status
curl "http://localhost:8000/api/v1/customers/bulk-import/status/TASK_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Troubleshooting

- **"No module named 'app'"**: Make sure virtual environment is activated
- **"Connection refused"**: Make sure Redis is running
- **"Task not registered"**: Check that Celery worker shows the task in the [tasks] section
- **"Permission denied"**: Run `chmod +x start_celery.sh`