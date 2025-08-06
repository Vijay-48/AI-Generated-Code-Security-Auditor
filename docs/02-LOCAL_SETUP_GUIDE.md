# 🛠️ AI Code Security Auditor - Setup Guide v2.0.0

> **Complete implementation instructions for the AI Code Security Auditor PIP package**

---

## 📋 **Prerequisites**

### **System Requirements**
- **Python 3.11+** - Required for modern language features and compatibility
- **pip 21.0+** - For package installation and dependency management
- **4GB RAM minimum** - For AI model processing (8GB+ recommended)
- **2GB disk space** - For models and data storage

### **Optional Dependencies**
- **Git** - For repository scanning features
- **Redis** - For caching and async processing (performance enhancement)
- **curl** - For API testing and health checks

### **Operating System Support**
- ✅ **Linux** (Ubuntu 20.04+, CentOS 8+, Debian 11+)
- ✅ **macOS** (10.15+, ARM64 and x86_64)
- ✅ **Windows** (10+, WSL2 recommended)

---

## 🚀 **Installation Methods**

### **Method 1: PyPI Installation (Recommended)**

```bash
# Install from PyPI (when published)
pip install ai-code-security-auditor

# Verify installation
auditor --help
auditor models
```

### **Method 2: Wheel Installation**

```bash
# Install from wheel file
pip install ai_code_security_auditor-2.0.0-py3-none-any.whl

# Verify installation
auditor --help
```

### **Method 3: Source Installation (Developers)**

```bash
# Clone repository (if developing)
git clone <repository-url>
cd ai-code-security-auditor

# Install in development mode
pip install -e .

# Verify installation
auditor --help
```

### **Method 4: Virtual Environment (Recommended for Testing)**

```bash
# Create virtual environment
python -m venv ai-auditor-env

# Activate virtual environment
# Linux/macOS:
source ai-auditor-env/bin/activate
# Windows:
ai-auditor-env\Scripts\activate

# Install package
pip install ai-code-security-auditor

# Verify installation
auditor --help
```

---

## 🔧 **Configuration**

### **1. API Key Setup (Required)**

The AI Code Security Auditor requires an OpenRouter API key for LLM functionality.

#### **Get Your API Key**
1. Visit [OpenRouter.ai](https://openrouter.ai/)
2. Create an account (free tier available)
3. Navigate to API Keys section
4. Generate a new API key

#### **Configure API Key**

**Method 1: Environment Variable (Recommended)**
```bash
# Linux/macOS
export OPENROUTER_API_KEY="your-api-key-here"
echo 'export OPENROUTER_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc

# Windows
set OPENROUTER_API_KEY=your-api-key-here
# Or add to system environment variables
```

**Method 2: .env File**
Create a `.env` file in your working directory:
```env
OPENROUTER_API_KEY=your-api-key-here
OPENROUTER_REFERER=https://your-domain.com  # Optional
OPENROUTER_TITLE=AI Code Security Auditor   # Optional
```

### **2. CLI Configuration (Optional)**

Create a configuration file for customized defaults:

```bash
# Create config directory
mkdir -p ~/.config/auditor

# Create configuration file
cat > ~/.config/auditor/config.yaml << 'EOF'
# AI Code Security Auditor Configuration v2.0.0

# API Settings
api:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  timeout: 300

# Scanning Settings
scanning:
  default_model: "agentica-org/deepcoder-14b-preview:free"
  timeout: 300
  max_file_size: "10MB"
  batch_size: 10
  
# Analytics Settings
analytics:
  retention_days: 365
  cache_ttl: 3600
  enable_forecasting: true
  
# Output Settings
output:
  default_format: "table"
  colors: true
  progress_bars: true
  show_details: true
  
# Filter Settings
filters:
  default_excludes:
    - "*/node_modules/*"
    - "*/.git/*" 
    - "*/venv/*"
    - "*/env/*"
    - "*/__pycache__/*"
    - "*/test*/*"
    - "*/build/*"
    - "*/dist/*"
    - "*.log"
    - "*.tmp"
    
  default_includes:
    - "*.py"
    - "*.js"
    - "*.jsx"
    - "*.ts" 
    - "*.tsx"
    - "*.java"
    - "*.go"
    - "*.php"
    - "*.rb"
    - "*.cpp"
    - "*.c"

# Model Preferences
models:
  preferred:
    code_patches: "agentica-org/deepcoder-14b-preview:free"
    quality_assessment: "meta-llama/llama-3.3-70b-instruct:free" 
    fast_classification: "qwen/qwen-2.5-coder-32b-instruct:free"
    security_explanations: "moonshotai/kimi-dev-72b:free"
    
  # Model-specific settings
  settings:
    temperature: 0.1
    max_tokens: 4000
    timeout: 120

# GitHub Integration (Optional)
github:
  token: ""  # Set your GitHub token here
  default_branch: "main"
  max_files_per_repo: 1000
  
# Logging Settings
logging:
  level: "INFO"
  format: "detailed"
  log_to_file: false
  log_file: "auditor.log"
EOF
```

### **3. Redis Setup (Optional - for Enhanced Performance)**

Redis provides caching and async processing capabilities for improved performance.

#### **Install Redis**

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**macOS:**
```bash
# Using Homebrew
brew install redis
brew services start redis
```

**Docker (Cross-platform):**
```bash
docker run -d --name redis -p 6379:6379 redis:alpine
```

#### **Configure Redis Environment Variables**
```bash
export REDIS_URL="redis://localhost:6379/0"
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
export REDIS_DB="0"

# For async processing
export CELERY_BROKER_URL="redis://localhost:6379/1"
export CELERY_RESULT_BACKEND="redis://localhost:6379/2"
```

---

## ✅ **Verification & Testing**

### **1. Basic Functionality Test**

```bash
# Test CLI help
auditor --help

# Test model listing
auditor models

# Test basic analysis
auditor analyze --code "print('hello world')" --language python
```

### **2. Advanced Features Test**

```bash
# Test file scanning
echo 'import os; os.system(user_input)' > vulnerable.py
auditor scan vulnerable.py

# Test with advanced analysis
auditor analyze --code "exec(user_data)" --language python --advanced

# Clean up
rm vulnerable.py
```

### **3. API Server Test**

#### **Start the API Server**
```bash
# Method 1: Direct uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Method 2: Python script
python -c "
import uvicorn
from app.main import app
uvicorn.run(app, host='0.0.0.0', port=8000)
"
```

#### **Test API Endpoints**
```bash
# Health check
curl http://localhost:8000/health

# Models endpoint
curl http://localhost:8000/models

# Basic audit
curl -X POST "http://localhost:8000/audit" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello, World!\")",
    "language": "python"
  }'
```

### **4. Performance Test**

```bash
# Test with larger file
auditor scan /path/to/large/project --max-files 100

# Test with different models
auditor analyze --code "SELECT * FROM users" --language python --model "meta-llama/llama-3.3-70b-instruct:free"
```

---

## 🔧 **Advanced Configuration**

### **1. Custom Security Rules**

Create custom vulnerability detection rules:

```yaml
# ~/.config/auditor/custom_rules.yaml
custom_rules:
  - name: "Custom SQL Injection"
    pattern: "SELECT.*\\+.*user_input"
    language: "python"
    severity: "HIGH"
    description: "Potential SQL injection via string concatenation"
    
  - name: "Hardcoded Password"
    pattern: "password\\s*=\\s*['\"][^'\"]{8,}['\"]"
    language: "*"
    severity: "CRITICAL"  
    description: "Hardcoded password detected"
```

### **2. Integration Scripts**

#### **Pre-commit Hook**
Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
echo "Running security audit..."
auditor scan --staged-only --output-format github
if [ $? -ne 0 ]; then
    echo "Security issues found. Commit rejected."
    exit 1
fi
```

#### **CI/CD Integration**
```yaml
# GitHub Actions example
name: Security Audit
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install auditor
      run: pip install ai-code-security-auditor
    - name: Run security audit
      run: |
        auditor scan . --output-format sarif --save results.sarif
      env:
        OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
    - name: Upload results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: results.sarif
```

### **3. Enterprise Configuration**

For enterprise deployments, create `/etc/auditor/enterprise.yaml`:

```yaml
# Enterprise Configuration
enterprise:
  # License settings
  license:
    key: "enterprise-license-key"
    features: ["bulk_scanning", "advanced_analytics", "sso"]
    
  # SSO Configuration  
  sso:
    enabled: true
    provider: "okta"
    domain: "company.okta.com"
    
  # Compliance Settings
  compliance:
    standards: ["SOC2", "PCI-DSS", "GDPR"]
    reporting:
      frequency: "weekly"
      recipients: ["security-team@company.com"]
      
  # Performance Settings
  performance:
    max_concurrent_scans: 50
    cache_size: "2GB"
    worker_processes: 8
    
  # Database Settings (for analytics)
  database:
    type: "postgresql"
    host: "analytics-db.company.com"
    port: 5432
    database: "security_analytics"
    ssl_mode: "require"
```

---

## 🐛 **Troubleshooting**

### **Common Issues**

#### **1. Import Errors**
```bash
# Error: ModuleNotFoundError
# Solution: Ensure package is properly installed
pip install --upgrade ai-code-security-auditor

# Verify installation
python -c "import app.main; print('✅ Import successful')"
```

#### **2. API Key Issues**
```bash
# Error: API key not configured
# Solution: Set environment variable
export OPENROUTER_API_KEY="your-key"

# Verify key is set
auditor models
```

#### **3. Permission Errors**
```bash
# Error: Permission denied
# Solution: Check file permissions
chmod +x $(which auditor)

# Or install in user space
pip install --user ai-code-security-auditor
```

#### **4. Redis Connection Issues**
```bash
# Error: Redis connection failed
# Solution: Check Redis status
redis-cli ping

# If not installed, install Redis or disable caching
export REDIS_URL=""
```

### **Debug Mode**

Enable debug logging for troubleshooting:

```bash
# Set debug environment
export AUDITOR_DEBUG=true
export AUDITOR_LOG_LEVEL=DEBUG

# Run with verbose output
auditor scan . --verbose --debug
```

### **Performance Issues**

If experiencing slow performance:

```bash
# Use faster models for classification
auditor scan . --model "qwen/qwen-2.5-coder-32b-instruct:free"

# Reduce batch size
auditor scan . --batch-size 5

# Enable caching (requires Redis)
export REDIS_URL="redis://localhost:6379/0"
```

---

## 📊 **Health Monitoring**

### **System Health Check**

Create a health monitoring script:

```bash
#!/bin/bash
# health_check.sh

echo "🔍 AI Code Security Auditor Health Check"
echo "========================================"

# Check Python version
echo "Python version: $(python --version)"

# Check package installation
if command -v auditor >/dev/null 2>&1; then
    echo "✅ CLI tool installed"
else
    echo "❌ CLI tool not found"
    exit 1
fi

# Check API key
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "⚠️  API key not configured"
else
    echo "✅ API key configured"
fi

# Check Redis (optional)
if redis-cli ping >/dev/null 2>&1; then
    echo "✅ Redis available"
else
    echo "ℹ️  Redis not available (optional)"
fi

# Test basic functionality
echo "Testing basic functionality..."
if auditor --help >/dev/null 2>&1; then
    echo "✅ Basic functionality working"
else
    echo "❌ Basic functionality failed"
    exit 1
fi

# Test model access (requires API key)
if [ ! -z "$OPENROUTER_API_KEY" ]; then
    if auditor models >/dev/null 2>&1; then
        echo "✅ Model access working"
    else
        echo "⚠️  Model access failed (check API key)"
    fi
fi

echo "🎉 Health check completed successfully!"
```

Run with:
```bash
chmod +x health_check.sh
./health_check.sh
```

---

## 🚀 **Next Steps**

After successful installation:

1. **📖 Read the CLI Reference**: [CLI Commands Guide](05-CLI_Commands.md)
2. **🧪 Run Sample Tests**: [Testing Guide](03-LOCAL_TESTING_GUIDE.md)  
3. **📊 Explore Analytics**: Try `auditor trends --help`
4. **🔧 Customize Configuration**: Modify `~/.config/auditor/config.yaml`
5. **🤝 Join Community**: GitHub Discussions for questions and tips

---

## 📞 **Support**

If you encounter any issues during setup:

- **📚 Documentation**: Check the [Documentation Index](00-DOCUMENTATION_INDEX.md)
- **🐛 Bug Reports**: GitHub Issues with detailed error messages
- **💬 Community**: GitHub Discussions for setup questions
- **📧 Enterprise**: Contact enterprise support for business licenses

---

<div align="center">

**[⬅️ Back to Main README](../README.md) • [➡️ Testing Guide](03-LOCAL_TESTING_GUIDE.md)**

</div>