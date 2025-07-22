# 🛡️ AI Code Security Auditor v2.0.0 - Local Testing Guide

This document provides step-by-step instructions to set up, run, and test the AI Code Security Auditor on your local machine.

---

## 🚀 **Quick Start (5 Minutes)**

### **Step 1: Prerequisites Check**
```bash
# Check Python version (requires 3.11+)
python3 --version

# Check if pip is available
pip --version

# Check if git is available (optional)
git --version
```

### **Step 2: Clone/Navigate to Project**
```bash
# If you have the code locally, navigate to it:
cd /path/to/ai-code-security-auditor

# Or if you need to clone:
# git clone <repository-url>
# cd ai-code-security-auditor
```

### **Step 3: Install Dependencies**
```bash
# Install all requirements
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### **Step 4: Set Up Environment (Optional but Recommended)**
```bash
# Get your free OpenRouter API key from: https://openrouter.ai/
export OPENROUTER_API_KEY="sk-or-v1-your-key-here"

# Or add to your shell profile for persistence:
echo 'export OPENROUTER_API_KEY="sk-or-v1-your-key-here"' >> ~/.bashrc
```

### **Step 5: Start the API Server**
```bash
# Start the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Server will be available at: http://localhost:8001
# API docs at: http://localhost:8001/docs
```

---

## 🧪 **Testing Phase 1: Basic Functionality**

### **Test 1: Health Check**
```bash
# Test API health (in a new terminal)
curl http://localhost:8001/health

# Expected output:
# {"status":"ok","version":"2.0.0","features":["async_processing","caching","websockets"],"cache_status":"disconnected"}
```

### **Test 2: API Information**
```bash
# Get API information
curl http://localhost:8001/ | jq '.'

# Expected: API version, available endpoints, and features
```

### **Test 3: Available Models**
```bash
# Test models endpoint
curl http://localhost:8001/models | jq '.'

# Expected: List of 4 OpenRouter models with descriptions
```

### **Test 4: Basic CLI Commands**
```bash
# Test CLI help
python auditor/cli.py --help

# Test models command
python auditor/cli.py models

# Expected: List of available AI models with recommendations
```

---

## 🔍 **Testing Phase 2: Security Scanning**

### **Test 5: Direct Code Analysis (API)**
```bash
# Test basic vulnerability detection
curl -X POST "http://localhost:8001/audit" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import os\ndef unsafe_function(user_input):\n    os.system(f\"echo {user_input}\")",
    "language": "python"
  }' | jq '.'

# Expected: Detection of command injection vulnerability (B605)
```

### **Test 6: Advanced Analysis with AI**
```bash
# Test with specific model
curl -X POST "http://localhost:8001/audit" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import os\npassword = \"secret123\"\nos.system(f\"rm {user_input}\")",
    "language": "python",
    "model": "agentica-org/deepcoder-14b-preview:free",
    "use_advanced_analysis": true
  }' | jq '.'

# Expected: Multiple vulnerabilities + AI-generated patches and insights
```

### **Test 7: CLI Code Analysis**
```bash
# Test CLI analyze command
python auditor/cli.py analyze \
  --code "import os; os.system('rm -rf /')" \
  --language python

# Expected: Formatted vulnerability report with recommendations
```

### **Test 8: Directory Scanning**
```bash
# Scan current directory
python auditor/cli.py scan --path .

# Scan with specific output format
python auditor/cli.py scan \
  --path . \
  --output-format github \
  --save test-security-report.md

# Expected: Comprehensive security report saved to file
```

---

## 📊 **Testing Phase 3: Phase 9 Analytics Features**

### **Test 9: Trend Analysis (API)**
```bash
# Test detailed trends endpoint
curl "http://localhost:8001/api/analytics/trends/detailed?period=7&granularity=daily&include_forecasting=true" | jq '.'

# Expected: Trend data with growth rates and forecasting
```

### **Test 10: Top Rules Analysis (API)**
```bash
# Test top rules endpoint
curl "http://localhost:8001/api/analytics/top-rules?limit=5" | jq '.'

# Expected: Most frequently triggered security rules
```

### **Test 11: Performance Analytics (API)**
```bash
# Test performance endpoint
curl "http://localhost:8001/api/analytics/performance/detailed?include_model_stats=true" | jq '.'

# Expected: Performance metrics with optimization insights
```

### **Test 12: Data Export (API)**
```bash
# Test export functionality
curl -X POST "http://localhost:8001/api/analytics/export" \
  -H "Content-Type: application/json" \
  -d '{
    "time_range": "7d",
    "format": "json",
    "include_trends": true,
    "include_repositories": true
  }' | jq '.'

# Expected: Export confirmation with download information
```

---

## 🖥️ **Testing Phase 4: Advanced CLI Features**

### **Test 13: Trend Analysis (CLI)**
```bash
# Basic trends
python auditor/cli.py trends-detailed --period 7

# Advanced trends with forecasting
python auditor/cli.py trends-detailed \
  --period 30 \
  --granularity daily \
  --include-forecast \
  --visual

# Export trends to CSV
python auditor/cli.py trends-detailed \
  --period 14 \
  --output csv \
  --save trends-analysis.csv
```

### **Test 14: Top Rules Analysis (CLI)**
```bash
# Basic top rules
python auditor/cli.py top-rules --limit 10

# Filtered analysis
python auditor/cli.py top-rules \
  --severity high \
  --tool bandit \
  --output table

# Export to CSV
python auditor/cli.py top-rules \
  --limit 20 \
  --output csv \
  --save top-rules-report.csv
```

### **Test 15: Performance Analysis (CLI)**
```bash
# Comprehensive performance analysis
python auditor/cli.py performance \
  --include-models \
  --breakdown-language

# Export performance data
python auditor/cli.py performance \
  --output json \
  --save performance-metrics.json
```

### **Test 16: Report Generation (CLI)**
```bash
# Security summary report
python auditor/cli.py generate-report \
  --report-type security_summary \
  --time-range 7d \
  --format markdown \
  --save weekly-security-report.md

# Trends analysis report
python auditor/cli.py generate-report \
  --report-type vulnerability_trends \
  --time-range 30d \
  --format json \
  --save trends-report.json

# Performance report
python auditor/cli.py generate-report \
  --report-type performance_analysis \
  --time-range 30d \
  --format markdown \
  --save performance-report.md
```

---

## 🎯 **Testing Phase 5: Advanced Features**

### **Test 17: Multiple Output Formats**
```bash
# Test different output formats
python auditor/cli.py scan . --output-format table
python auditor/cli.py scan . --output-format json --save results.json
python auditor/cli.py scan . --output-format github --save github-report.md
python auditor/cli.py scan . --output-format sarif --save security.sarif
```

### **Test 18: Advanced Filtering**
```bash
# Severity filtering
python auditor/cli.py scan . --severity-filter high

# Pattern exclusions
python auditor/cli.py scan . \
  --exclude "*/tests/*" \
  --exclude "*/node_modules/*" \
  --exclude "*/.git/*"

# Include specific files
python auditor/cli.py scan . \
  --include "*.py" \
  --include "*.js"
```

### **Test 19: Model Selection**
```bash
# Test different AI models
python auditor/cli.py analyze \
  --code "import subprocess; subprocess.call(cmd, shell=True)" \
  --language python \
  --model "meta-llama/llama-3.3-70b-instruct:free"

python auditor/cli.py analyze \
  --code "SELECT * FROM users WHERE id = " + userId \
  --language javascript \
  --model "qwen/qwen-2.5-coder-32b-instruct:free"
```

---

## 🏃‍♂️ **Quick Demo Script**

### **Test 20: Run Complete Demo**
```bash
# Run the comprehensive demo script
chmod +x example_session.sh
./example_session.sh

# This will test all major features automatically
```

### **Test 21: Run Final Validation**
```bash
# Run complete validation suite
python final_validation.py

# Expected: 7/7 (100%) validation success
```

---

## 🔧 **Troubleshooting Guide**

### **Common Issues & Solutions**

#### **1. "Command not found: auditor"**
```bash
# Solution 1: Install in development mode
pip install -e .

# Solution 2: Run CLI directly
python auditor/cli.py --help

# Solution 3: Check Python PATH
echo $PYTHONPATH
```

#### **2. "No such file or directory: bandit"**
```bash
# Solution: Install security tools
pip install bandit semgrep

# Or install all requirements
pip install -r requirements.txt
```

#### **3. "Rate limit exceeded" from OpenRouter**
```bash
# This is expected with free tier - core features still work
# Solution: Upgrade OpenRouter plan or use caching
echo "Rate limits are handled gracefully - this is normal"
```

#### **4. "Connection refused" on API calls**
```bash
# Solution: Make sure API server is running
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Check if port is in use
lsof -i :8001
```

#### **5. "CLI argument parsing errors"**
```bash
# ❌ Incorrect syntax:
python auditor/cli.py scan --exclude "*/tests/*" "*/node_modules/*"

# ✅ Correct syntax:
python auditor/cli.py scan --exclude "*/tests/*" --exclude "*/node_modules/*"
```

#### **6. "Import errors" or missing dependencies**
```bash
# Solution: Reinstall all dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version
python3 --version  # Should be 3.11+
```

---

## 📊 **Expected Test Results**

### **Successful Test Indicators:**

#### **API Tests:**
- Health endpoint returns `{"status":"ok","version":"2.0.0"}`
- Models endpoint returns 4 AI models
- Audit endpoint detects vulnerabilities (B605, B608, etc.)
- Analytics endpoints return trend and performance data

#### **CLI Tests:**
- Help commands display comprehensive usage information
- Scan commands detect and report vulnerabilities
- Analytics commands show trends, rules, and performance data
- Report generation creates properly formatted files

#### **Phase 9 Analytics:**
- Trend analysis shows vulnerability patterns over time
- Top rules analysis identifies most frequent security issues
- Performance analysis provides optimization recommendations
- Report generation creates professional documentation

#### **File Outputs:**
After testing, you should see files like:
- `test-security-report.md` - GitHub Actions format report
- `trends-analysis.csv` - Vulnerability trends data
- `performance-metrics.json` - Performance analysis
- `weekly-security-report.md` - Executive summary report

---

## 🎯 **Success Criteria**

Your local installation is working correctly if:

✅ **API Server**: All endpoints respond correctly  
✅ **CLI Commands**: All commands execute without errors  
✅ **Security Scanning**: Vulnerabilities are detected and reported  
✅ **Phase 9 Analytics**: Trends, rules, and performance data are generated  
✅ **AI Integration**: Models are accessible and provide intelligent analysis  
✅ **Report Generation**: Professional reports are created in multiple formats  
✅ **Output Formats**: All formats (table, JSON, CSV, Markdown) work correctly  

---

## 🚀 **Next Steps After Local Testing**

1. **Customize Configuration**: Edit `~/.config/auditor/config.yaml`
2. **Integrate with CI/CD**: Use GitHub Actions workflow
3. **Deploy to Production**: Use `./deploy.sh` script
4. **Share with Team**: Distribute the comprehensive documentation

---

## 📞 **Support & Resources**

- **Full Documentation**: See `README.md` for complete usage guide
- **CLI Reference**: See `docs/CLI_Commands.md` for all commands
- **API Documentation**: Visit `http://localhost:8001/docs` when server is running
- **Change History**: See `CHANGELOG.md` for version details

---

**🎉 Happy Testing! Your AI Code Security Auditor v2.0.0 is ready to transform code security! 🛡️**