# 🛡️ AI Code Security Auditor v2.0.0 - Complete Local Setup Guide

> **Production-Ready AI-powered security scanner with multi-model LLM integration, advanced analytics, and comprehensive vulnerability detection.**

## 🏗️ Project Architecture

This is a **FastAPI-based Python application** (not a full-stack web app) with:
- **Core API Server**: FastAPI application with OpenRouter AI integration
- **CLI Tools**: Professional command-line interface with rich visuals
- **Background Workers**: Celery workers for async processing
- **Caching Layer**: Redis for performance optimization
- **Analytics Engine**: Comprehensive security analytics and reporting
- **Multi-Model AI**: 4 specialized LLM models for different security tasks

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (5 minutes)](#quick-start-5-minutes)
3. [Method 1: Docker Setup (Recommended)](#method-1-docker-setup-recommended)
4. [Method 2: Local Python Environment](#method-2-local-python-environment)
5. [Method 3: Production Deployment](#method-3-production-deployment)
6. [Environment Configuration](#environment-configuration)
7. [Running the Application](#running-the-application)
8. [CLI Usage](#cli-usage)
9. [API Testing](#api-testing)
10. [Troubleshooting](#troubleshooting)
11. [Development Setup](#development-setup)

---

## 📋 Prerequisites

### System Requirements
- **Python 3.11+** (required)
- **Git** (for cloning the repository)
- **Docker & Docker Compose** (for Docker setup)
- **Redis** (for caching - optional but recommended)
- **8GB RAM** recommended (4GB minimum)
- **5GB free disk space**

### API Keys Required
- **OpenRouter API Key** (for AI models) - **Already configured in this project**
- **GitHub Token** (optional - for repository scanning)

---

## 🚀 Quick Start (3 methods)

### Option A: Docker (Recommended - 2 minutes)
```bash
# 1. Start all services with Docker
docker-compose up -d

# 2. Wait 30 seconds, then test
curl http://localhost:8000/health

# 3. Access services
echo "🌐 API Documentation: http://localhost:8000/docs"
echo "📊 Worker Monitoring: http://localhost:5555"
echo "✅ Docker setup complete!"
```

### Option B: Local Python (Advanced users)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start Redis (required)
redis-server --daemonize yes

# 3. Run the API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 4. Test CLI tools
python -m auditor.cli models
```

### Option C: CLI Only (Fastest for scanning)
```bash
# 1. Install as package
pip install -e .

# 2. Test installation
auditor models

# 3. Scan your code
auditor scan . --output-format github --save report.md
```

---

## 🐳 Method 1: Docker Setup (Recommended)

### Step 1: Prerequisites
```bash
# Install Docker (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 2: Environment Setup
```bash
# The .env file is already configured with working API keys
# Verify the configuration:
cat .env

# Should show:
# OPENROUTER_API_KEY=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
# REDIS_URL=redis://localhost:6379/0
# (other configuration...)
```

### Step 3: Run the Application Stack
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# Expected output:
# NAME                   SERVICE    STATUS    PORTS
# app-app-1             app        Up        0.0.0.0:8000->8000/tcp
# app-redis-1           redis      Up        0.0.0.0:6379->6379/tcp
# app-worker-1          worker     Up        
# app-flower-1          flower     Up        0.0.0.0:5555->5555/tcp
```

### Services Architecture
The Docker setup runs these services:

| Service | Purpose | Port | Description |
|---------|---------|------|-------------|
| **app** | FastAPI Server | 8000 | Main API with security scanning |
| **redis** | Cache & Message Broker | 6379 | Caching and job queue |
| **worker** | Background Jobs | - | Celery worker for async tasks |
| **flower** | Monitoring | 5555 | Real-time task monitoring |

### Step 4: Verify Installation
```bash
# Test API health
curl http://localhost:8000/health

# Expected response:
# {"status":"ok","version":"2.0.0","features":["async_processing","caching","websockets"],"cache_status":"connected"}

# Test AI models
curl http://localhost:8000/models

# Test security scanning
curl -X POST "http://localhost:8000/audit" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import os\nos.system(user_input)",
    "language": "python"
  }'
```

---

## 🐍 Method 2: Local Python Environment

### Step 1: Python Environment Setup
```bash
# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt

# Install security tools
pip install bandit semgrep
```

### Step 2: Install Redis (Required for Caching)
```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# macOS
brew install redis
brew services start redis

# Windows (using WSL recommended)
# Or use Docker: docker run -d -p 6379:6379 redis:7-alpine
```

### Step 3: Database Setup
```bash
# Create data directories
mkdir -p chroma_db
mkdir -p data

# Set permissions
chmod 755 chroma_db data
```

### Step 4: Run the Application
```bash
# Method A: Using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Method B: Using Python module
python -m app.main

# Method C: Using the CLI entry point
python -m auditor.cli models  # Test CLI functionality
```

### Step 5: Run Background Services (Optional but recommended)
```bash
# Terminal 1: Run Celery worker
celery -A app.celery_app worker --loglevel=info --concurrency=2

# Terminal 2: Run Flower monitoring (optional)
celery -A app.celery_app flower --port=5555

# Terminal 3: Keep the main app running
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🏭 Method 3: Production Deployment

### Step 1: Production Docker Compose
```bash
# Use the production configuration
docker-compose -f docker-compose.prod.yml up -d

# Or build with specific optimizations
docker build -f Dockerfile.prod -t ai-security-auditor:prod .
```

### Step 2: Environment Variables for Production
```bash
# Create production .env file
cp .env .env.prod

# Edit for production settings
nano .env.prod

# Add production-specific variables:
# OPENROUTER_API_KEY=your-production-key
# REDIS_URL=redis://production-redis:6379/0
# DATABASE_URL=postgresql://user:pass@db:5432/security_auditor
```

### Step 3: Run with Production Settings
```bash
# Load production environment
export $(cat .env.prod | xargs)

# Run with production settings
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## ⚙️ Environment Configuration

### Required Environment Variables
```bash
# Core Configuration (.env file)
OPENROUTER_API_KEY=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
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1/chat/completions
OPENROUTER_REFERER=http://localhost:8000
OPENROUTER_TITLE="AI Code Security Auditor"

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

### Optional Environment Variables
```bash
# GitHub Integration (for repository scanning)
GITHUB_TOKEN=ghp_your_github_token_here
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Database Configuration
DATABASE_URL=sqlite:///./security_auditor.db

# Monitoring
PROMETHEUS_METRICS=true
LOG_LEVEL=INFO
```

### Verify Environment Setup
```bash
# Check if all environment variables are loaded
python -c "
from app.config import settings
print('✅ OpenRouter API Key:', '***' + settings.OPENROUTER_API_KEY[-10:] if settings.OPENROUTER_API_KEY else '❌ Missing')
print('✅ Redis URL:', settings.REDIS_URL)
print('✅ Database URL:', settings.DATABASE_URL)
"
```

---

## 🚀 Running the Application

### Service Endpoints
Once running, the following endpoints will be available:

| Service | URL | Description |
|---------|-----|-------------|
| **Main API** | http://localhost:8000 | Core security scanning API |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health Check** | http://localhost:8000/health | Service status |
| **Metrics** | http://localhost:8000/metrics | Prometheus metrics |
| **Flower Dashboard** | http://localhost:5555 | Celery task monitoring |
| **Redis** | localhost:6379 | Cache and message broker |

### Checking Service Status
```bash
# Check if all services are running
docker-compose ps

# Check application logs
docker-compose logs app

# Check worker logs
docker-compose logs worker

# Check Redis status
docker-compose logs redis

# Check if ports are listening
netstat -tulnp | grep -E ':(8000|6379|5555)'
```

---

## 💻 CLI Usage

### Installation as Package
```bash
# Install the CLI tool
pip install -e .

# Verify installation
auditor --help
ai-security-auditor --help  # Alternative command name
```

### CLI Commands

#### 1. List Available Models
```bash
auditor models
```

#### 2. Scan Files/Directories
```bash
# Basic directory scan
auditor scan .

# Scan with specific model
auditor scan . --model "agentica-org/deepcoder-14b-preview:free"

# Scan with advanced analysis
auditor scan . --advanced

# Exclude certain directories
auditor scan . \
  --exclude "*/tests/*" \
  --exclude "*/node_modules/*" \
  --exclude "*/.git/*"

# Generate GitHub Actions report
auditor scan . \
  --output-format github \
  --save security-report.md
```

#### 3. Analyze Code Directly
```bash
# Analyze specific code
auditor analyze \
  --code "import os; os.system(user_input)" \
  --language python \
  --model "agentica-org/deepcoder-14b-preview:free"
```

#### 4. Advanced Analytics (Phase 9 Features)
```bash
# Trend analysis
auditor trends-detailed --period 30 --include-forecast

# Top vulnerability rules
auditor top-rules --limit 10 --severity high

# Performance analysis
auditor performance --include-models --breakdown-language

# Generate reports
auditor generate-report \
  --report-type security_summary \
  --time-range 7d \
  --format markdown \
  --save weekly-report.md
```

---

## 🧪 API Testing

### Basic API Tests
```bash
# Test 1: Health Check
curl -X GET "http://localhost:8000/health"

# Expected: {"status":"ok","version":"2.0.0",...}

# Test 2: Available Models
curl -X GET "http://localhost:8000/models"

# Expected: {"available_models":[...],"recommendations":{...}}

# Test 3: Basic Security Scan
curl -X POST "http://localhost:8000/audit" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import os\nos.system(user_input)",
    "language": "python"
  }'

# Expected: {"scan_results":{...},"vulnerabilities":[...],...}
```

### Advanced API Tests
```bash
# Test 4: Model-Specific Analysis
curl -X POST "http://localhost:8000/audit" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "SELECT * FROM users WHERE id = " + user_id,
    "language": "python",
    "model": "agentica-org/deepcoder-14b-preview:free",
    "use_advanced_analysis": true
  }'

# Test 5: JavaScript Scanning
curl -X POST "http://localhost:8000/audit" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "eval(userInput); document.write(data);",
    "language": "javascript"
  }'

# Test 6: Async Job Processing
curl -X POST "http://localhost:8000/async/audit" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import os\nos.system(user_input)",
    "language": "python",
    "priority": "high"
  }'
```

### Analytics API Tests (Phase 9)
```bash
# Test 7: Trend Analysis
curl "http://localhost:8000/api/analytics/trends/detailed?period=30&granularity=daily"

# Test 8: Top Rules Analysis
curl "http://localhost:8000/api/analytics/top-rules?limit=10&severity_filter=high"

# Test 9: Performance Metrics
curl "http://localhost:8000/api/analytics/performance/detailed?include_model_stats=true"
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue 1: "Connection refused" on port 8000
```bash
# Check if service is running
docker-compose ps
curl http://localhost:8000/health

# If not running, restart
docker-compose down && docker-compose up -d

# Check logs for errors
docker-compose logs app
```

#### Issue 2: "Module not found" errors
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
export PYTHONPATH="${PYTHONPATH}:/app"

# Verify installation
python -c "import app.main; print('✅ App imports correctly')"
```

#### Issue 3: Redis connection errors
```bash
# Check Redis status
redis-cli ping  # Should return PONG

# If using Docker
docker-compose logs redis

# Restart Redis
docker-compose restart redis
```

#### Issue 4: OpenRouter API errors
```bash
# Verify API key is loaded
python -c "
import os
from app.config import settings
key = settings.OPENROUTER_API_KEY
print('API Key loaded:', 'Yes' if key else 'No')
print('Key length:', len(key) if key else 0)
"

# Test API key manually
curl -H "Authorization: Bearer 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" \
  -H "HTTP-Referer: http://localhost:8000" \
  -H "X-Title: AI Code Security Auditor" \
  https://openrouter.ai/api/v1/models
```

#### Issue 5: Permission errors
```bash
# Fix file permissions
sudo chown -R $USER:$USER /app/chroma_db
sudo chown -R $USER:$USER /app/data
chmod 755 /app/chroma_db /app/data
```

### Performance Issues

#### Slow scanning performance
```bash
# Enable Redis caching
export REDIS_URL="redis://localhost:6379/0"

# Use async endpoints
curl -X POST "http://localhost:8000/async/audit" \
  -H "Content-Type: application/json" \
  -d '{"code":"...","language":"python"}'

# Check cache status
curl "http://localhost:8000/async/cache/stats"
```

#### High memory usage
```bash
# Monitor memory usage
docker stats

# Limit memory in docker-compose.yml
# Add under services:
#   mem_limit: 2g
#   memswap_limit: 2g
```

### Debug Mode

#### Enable Debug Logging
```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Or in .env file
echo "LOG_LEVEL=DEBUG" >> .env

# Restart services
docker-compose restart
```

#### Check System Resources
```bash
# Check disk space
df -h

# Check memory
free -h

# Check CPU usage
top

# Check open files
lsof -i :8000
lsof -i :6379
```

---

## 🛠️ Development Setup

### Development Environment
```bash
# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest -v

# Run with coverage
pytest --cov=app --cov=auditor --cov-report=html
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m api          # API tests only

# Run tests with output
pytest -v -s

# Generate coverage report
pytest --cov=app tests/ --cov-report=html
open htmlcov/index.html
```

### Development Tools
```bash
# Code formatting
black app/ auditor/
isort app/ auditor/

# Type checking
mypy app/

# Linting
flake8 app/ auditor/

# Security scanning (dogfooding!)
auditor scan . --advanced
```

---

## 📊 Monitoring and Maintenance

### Health Checks
```bash
# Comprehensive health check
curl http://localhost:8000/health | jq

# Check all services
curl http://localhost:8000/ | jq '.features'

# Monitor metrics
curl http://localhost:8000/metrics
```

### Log Management
```bash
# View application logs
docker-compose logs -f app

# View worker logs
docker-compose logs -f worker

# View all logs
docker-compose logs -f
```

### Backup and Recovery
```bash
# Backup database and cache
mkdir -p backups
cp -r chroma_db backups/chroma_db_$(date +%Y%m%d)
redis-cli SAVE
cp dump.rdb backups/redis_$(date +%Y%m%d).rdb

# Restore from backup
cp backups/chroma_db_20241219 chroma_db/
cp backups/redis_20241219.rdb dump.rdb
docker-compose restart
```

---

## 🚀 Next Steps

### After Successful Setup
1. **🔍 Run Your First Scan**: Use the CLI to scan your codebase
2. **📊 Explore Analytics**: Check out the Phase 9 analytics features
3. **🔗 CI/CD Integration**: Set up GitHub Actions workflows
4. **📈 Monitor Performance**: Use the Flower dashboard and metrics
5. **🛡️ Security Review**: Regular scans and trend analysis

### Integration Ideas
- **VS Code Extension**: Use the CLI in your development workflow
- **GitHub Actions**: Automated security scanning on PRs
- **Slack/Teams**: Webhook notifications for critical findings
- **JIRA Integration**: Automatic ticket creation for vulnerabilities

### Resources
- **📚 Full Documentation**: Available in `/docs` directory
- **🛠️ API Reference**: http://localhost:8000/docs
- **📈 Monitoring**: http://localhost:5555 (Flower dashboard)
- **💬 GitHub Issues**: For bug reports and feature requests

---

## 🏁 Conclusion

You now have a **production-ready AI Code Security Auditor** running locally! This setup includes:

✅ **Multi-Model AI Integration**: 4 specialized LLM models  
✅ **Comprehensive Security Scanning**: Bandit, Semgrep, secret detection  
✅ **Professional CLI Tools**: Rich terminal interface  
✅ **Advanced Analytics**: Trend analysis and reporting  
✅ **Production Features**: Caching, async processing, monitoring  
✅ **Full Docker Environment**: Ready for deployment

The system is now ready to secure your codebases with the power of AI! 🛡️✨

---

**Made with ❤️ by the AI Security Team**  
*Transforming code security through artificial intelligence*