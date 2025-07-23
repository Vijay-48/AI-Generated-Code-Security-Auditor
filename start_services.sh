#!/bin/bash

echo "🚀 Starting AI Code Security Auditor..."

# Start Redis
echo "📦 Starting Redis..."
redis-server --daemonize yes

# Wait for Redis
sleep 2

# Start FastAPI in background
echo "🌐 Starting FastAPI server..."
cd /app
uvicorn app.main:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
API_PID=$!

# Start Celery worker in background
echo "👷 Starting Celery worker..."
celery -A app.celery_app worker --loglevel=info --concurrency=2 > logs/celery.log 2>&1 &
CELERY_PID=$!

# Start Flower (optional)
echo "🌸 Starting Flower monitoring..."
celery -A app.celery_app flower --port=5555 > logs/flower.log 2>&1 &
FLOWER_PID=$!

echo "✅ All services started!"
echo "📊 API Documentation: http://localhost:8000/docs" 
echo "🌸 Flower Monitoring: http://localhost:5555"
echo "🛡️ Test CLI: auditor models"

# Save PIDs for shutdown
echo $API_PID > .api.pid
echo $CELERY_PID > .celery.pid  
echo $FLOWER_PID > .flower.pid

echo "💡 To stop services, run: ./stop_services.sh"