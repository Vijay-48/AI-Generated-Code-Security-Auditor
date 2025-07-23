#!/bin/bash

echo "🛑 Stopping AI Code Security Auditor services..."

# Create logs directory if it doesn't exist
mkdir -p logs

# Kill processes if PIDs exist
if [ -f .api.pid ]; then
    kill $(cat .api.pid) 2>/dev/null
    rm .api.pid
    echo "✅ API server stopped"
fi

if [ -f .celery.pid ]; then
    kill $(cat .celery.pid) 2>/dev/null
    rm .celery.pid
    echo "✅ Celery worker stopped"
fi

if [ -f .flower.pid ]; then
    kill $(cat .flower.pid) 2>/dev/null
    rm .flower.pid
    echo "✅ Flower monitoring stopped"
fi

# Stop Redis (optional)
# redis-cli shutdown

echo "🔄 All services stopped!"