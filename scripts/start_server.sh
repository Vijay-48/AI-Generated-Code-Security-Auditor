#!/bin/bash
echo "🚀 Starting AI Code Security Auditor Server..."

# Set environment variables
export OPENROUTER_API_KEY="***********************"
export OPENROUTER_BASE_URL="https://openrouter.ai/api/v1/chat/completions"
export OPENROUTER_REFERER="http://localhost:8000"
export OPENROUTER_TITLE="AI Code Security Auditor"

# Start the server
cd /app
python -c "
import sys
sys.path.append('/app')
from app.main import app
import uvicorn
print('✅ FastAPI server starting on http://localhost:8000')
print('📚 API Documentation: http://localhost:8000/docs')
print('🔍 Health Check: http://localhost:8000/health')
uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')
"
