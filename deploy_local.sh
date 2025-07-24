#!/bin/bash

set -e  # Exit on any error

echo "🚀 Starting AI Code Security Auditor..."

# Change to project directory
cd /app

# Create logs directory
mkdir -p logs

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Port $port is already in use"
        echo "   Kill existing process: sudo kill -9 \$(sudo lsof -t -i:$port)"
        return 1
    fi
    return 0
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $name to start..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s --max-time 2 "$url" >/dev/null 2>&1; then
            echo "✅ $name is ready!"
            return 0
        fi
        
        echo "   Attempt $attempt/$max_attempts - waiting 2 seconds..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $name failed to start within 60 seconds"
    return 1
}

# Check if ports are available
echo "🔍 Checking ports..."
check_port 8000 || exit 1
check_port 6379 || echo "   Redis might already be running"

# Start Redis
echo "📦 Starting Redis..."
if ! redis-cli ping >/dev/null 2>&1; then
    redis-server --daemonize yes
    sleep 3
    if ! redis-cli ping >/dev/null 2>&1; then
        echo "❌ Failed to start Redis"
        exit 1
    fi
fi
echo "✅ Redis is running"

# Start FastAPI
echo "🌐 Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
API_PID=$!
echo "   FastAPI PID: $API_PID"

# Save PID for later cleanup
echo $API_PID > .api.pid

# Wait for FastAPI to be ready
if wait_for_service "http://localhost:8000/health" "FastAPI"; then
    # Test the API
    echo "🧪 Testing API endpoints..."
    
    # Test health check
    echo "   Health check:"
    curl -s http://localhost:8000/health | python3 -m json.tool
    
    # Test models endpoint
    echo ""
    echo "   Available models:"
    curl -s http://localhost:8000/models | python3 -c "import sys, json; data=json.load(sys.stdin); print('✅ Models:', len(data['available_models']))"
    
    echo ""
    echo "🎉 Deployment successful!"
    echo ""
    echo "📊 Access points:"
    echo "   • API Documentation: http://localhost:8000/docs"
    echo "   • Health Check: http://localhost:8000/health"
    echo "   • Models: http://localhost:8000/models"
    echo ""
    echo "🖥️  CLI Usage:"  
    echo "   • auditor models"
    echo "   • auditor analyze --code 'print(\"hello\")' --language python"
    echo ""
    echo "📋 Logs:"
    echo "   • API logs: tail -f logs/api.log"
    echo ""
    echo "🛑 To stop: kill $API_PID"
    
else
    echo "❌ FastAPI failed to start. Checking logs..."
    echo "=== API Logs ==="
    cat logs/api.log
    
    # Cleanup
    kill $API_PID 2>/dev/null || true
    rm -f .api.pid
    exit 1
fi