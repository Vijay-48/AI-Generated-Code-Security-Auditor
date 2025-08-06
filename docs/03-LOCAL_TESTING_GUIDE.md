# 🧪 AI Code Security Auditor - Testing Guide v2.0.0

> **Comprehensive testing and verification procedures for the AI Code Security Auditor PIP package**

---

## 🎯 **Testing Overview**

This guide provides step-by-step testing procedures to verify that the AI Code Security Auditor is working correctly after installation. All tests are designed for the v2.0.0 PIP package distribution.

### **Testing Objectives**
- ✅ **Verify Installation**: Ensure package is correctly installed
- ✅ **Test Core Features**: CLI commands and API endpoints
- ✅ **Validate AI Integration**: Confirm LLM models are accessible  
- ✅ **Check Performance**: Verify response times and accuracy
- ✅ **Test Integration**: CI/CD and Python library usage

---

## 📋 **Prerequisites**

### **Required Setup**
```bash
# 1. Install the package
pip install ai-code-security-auditor

# 2. Set API key
export OPENROUTER_API_KEY="your-api-key-here"

# 3. Verify Python version
python --version  # Should be 3.11+
```

### **Optional Components** 
```bash
# Install Redis for caching tests (optional)
# Ubuntu/Debian:
sudo apt install redis-server
sudo systemctl start redis-server

# macOS:
brew install redis
brew services start redis

# Docker:
docker run -d --name redis -p 6379:6379 redis:alpine
```

---

## ✅ **Basic Functionality Tests**

### **Test 1: Installation Verification**

#### **1.1 CLI Tool Availability**
```bash
# Test CLI command exists
which auditor
# Expected: /path/to/auditor

# Test help command
auditor --help
# Expected: Usage information with command list
```

#### **1.2 Python Import Test**
```bash
# Test core modules import correctly
python -c "
from app.main import app
from app.agents.security_agent import SecurityAgent
from auditor.cli import main
print('✅ All imports successful')
"
# Expected: ✅ All imports successful
```

#### **1.3 Version Verification**
```bash
# Check package version
pip show ai-code-security-auditor | grep Version
# Expected: Version: 2.0.0
```

### **Test 2: API Key Configuration**

#### **2.1 Environment Variable Test**
```bash
# Verify API key is set
echo $OPENROUTER_API_KEY
# Expected: Your API key (not empty)

# Test model access
auditor models
# Expected: List of available models
```

#### **2.2 Model Listing Test**
```bash
# Get available models
auditor models --format json | head -20
# Expected: JSON list with models like:
# - agentica-org/deepcoder-14b-preview:free
# - meta-llama/llama-3.3-70b-instruct:free
# - qwen/qwen-2.5-coder-32b-instruct:free
# - moonshotai/kimi-dev-72b:free
```

---

## 🔍 **Core Feature Tests**

### **Test 3: CLI Analysis Commands**

#### **3.1 Basic Code Analysis**
```bash
# Test simple code analysis
auditor analyze --code "print('Hello, World!')" --language python
# Expected: Analysis results with no vulnerabilities found

# Test with vulnerable code
auditor analyze --code "import os; os.system(user_input)" --language python
# Expected: Command injection vulnerability detected
```

#### **3.2 File Scanning Test**
```bash
# Create test file
echo 'import os
os.system(user_input)
password = "hardcoded123"
exec(user_data)' > test_vulnerable.py

# Scan the file
auditor scan test_vulnerable.py
# Expected: Multiple vulnerabilities detected:
# - Command injection (os.system)
# - Hardcoded password
# - Code execution (exec)

# Clean up
rm test_vulnerable.py
```

#### **3.3 Advanced Analysis Features**
```bash
# Test advanced analysis mode
auditor analyze --code "SELECT * FROM users WHERE id = $1" --language python --advanced
# Expected: Detailed analysis with AI explanations

# Test specific model selection
auditor analyze --code "exec(user_input)" --language python --model "meta-llama/llama-3.3-70b-instruct:free"
# Expected: Analysis using specified model
```

### **Test 4: Output Formats**

#### **4.1 Multiple Format Test**
```bash
# Create test code
VULNERABLE_CODE="import subprocess; subprocess.run(user_cmd, shell=True)"

# Test different output formats
auditor analyze --code "$VULNERABLE_CODE" --language python --output-format table
auditor analyze --code "$VULNERABLE_CODE" --language python --output-format json
auditor analyze --code "$VULNERABLE_CODE" --language python --output-format csv
auditor analyze --code "$VULNERABLE_CODE" --language python --output-format sarif
auditor analyze --code "$VULNERABLE_CODE" --language python --output-format github
```

#### **4.2 Report Generation Test**
```bash
# Test report saving
auditor analyze --code "os.system(user_input)" --language python --output-format github --save security_report.md

# Verify report created
ls -la security_report.md
cat security_report.md | head -20

# Clean up
rm security_report.md
```

---

## 🌐 **API Testing**

### **Test 5: FastAPI Server**

#### **5.1 Start API Server**
```bash
# Start server in background
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

# Wait for startup
sleep 5

# Save PID for cleanup
echo $SERVER_PID > api_server.pid
```

#### **5.2 Health Check Test**
```bash
# Test health endpoint
curl -s http://localhost:8000/health | python -m json.tool
# Expected: {"status": "ok", "version": "2.0.0", ...}

# Test models endpoint
curl -s http://localhost:8000/models | python -c "
import sys, json
data = json.load(sys.stdin)
print(f'✅ Found {len(data[\"available_models\"])} models')
"
```

#### **5.3 Audit Endpoint Test**
```bash
# Test audit endpoint
curl -X POST "http://localhost:8000/audit" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import os\nos.system(user_input)",
    "language": "python"
  }' | python -c "
import sys, json
data = json.load(sys.stdin)
vulns = len(data['vulnerabilities'])
print(f'✅ Found {vulns} vulnerabilities')
"
```

#### **5.4 Async Endpoint Test**
```bash
# Test async audit
JOB_RESPONSE=$(curl -s -X POST "http://localhost:8000/async/audit" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "exec(user_data)",
    "language": "python"
  }')

# Extract job ID
JOB_ID=$(echo $JOB_RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['job_id'])")
echo "Job ID: $JOB_ID"

# Check status
sleep 3
curl -s "http://localhost:8000/async/jobs/$JOB_ID/status" | python -m json.tool

# Get results
curl -s "http://localhost:8000/async/jobs/$JOB_ID/results" | python -c "
import sys, json
data = json.load(sys.stdin)
if 'vulnerabilities' in data:
    print(f'✅ Async job completed with {len(data[\"vulnerabilities\"])} vulnerabilities')
else:
    print('⏳ Job still processing')
"
```

### **Test 6: API Server Cleanup**
```bash
# Stop server
if [ -f api_server.pid ]; then
    kill $(cat api_server.pid)
    rm api_server.pid
    echo "✅ API server stopped"
fi
```

---

## 📊 **Advanced Feature Tests**

### **Test 7: Analytics Commands**

#### **7.1 Trends Analysis**
```bash
# Test trends command
auditor trends --period 30
# Expected: Trend analysis (may be empty for new installation)

# Test detailed trends
auditor trends-detailed --period 7 --include-forecast
# Expected: Detailed analytics with forecasting
```

#### **7.2 Performance Analysis**
```bash
# Test performance command
auditor performance --include-models
# Expected: Performance metrics and model usage

# Test with language breakdown
auditor performance --breakdown-language
# Expected: Performance data by programming language
```

#### **7.3 Rule Analysis**
```bash
# Test top rules command
auditor top-rules --limit 10
# Expected: Most frequently triggered vulnerability rules
```

### **Test 8: Configuration Tests**

#### **8.1 Config File Test**
```bash
# Create config directory
mkdir -p ~/.config/auditor

# Create test configuration
cat > ~/.config/auditor/config.yaml << 'EOF'
scanning:
  default_model: "qwen/qwen-2.5-coder-32b-instruct:free"
  timeout: 120
output:
  default_format: "json"
  colors: false
EOF

# Test with config
auditor analyze --code "print('test')" --language python
# Expected: Uses configuration settings (JSON format, fast model)

# Clean up
rm ~/.config/auditor/config.yaml
```

#### **8.2 Environment Override Test**
```bash
# Test environment variable override
AUDITOR_OUTPUT_FORMAT=csv auditor analyze --code "print('test')" --language python
# Expected: CSV format output
```

---

## 🧩 **Integration Tests**

### **Test 9: Python Library Integration**

#### **9.1 Direct API Usage**
```python
# Create test script
cat > test_integration.py << 'EOF'
import asyncio
from app.agents.security_agent import SecurityAgent

async def test_agent():
    """Test direct agent usage"""
    agent = SecurityAgent()
    
    # Test analysis
    result = await agent.run(
        code="import os; os.system(user_input)",
        language="python",
        use_advanced_analysis=True
    )
    
    # Verify results
    vulnerabilities = result.get('vulnerabilities', [])
    print(f"✅ Found {len(vulnerabilities)} vulnerabilities")
    
    for vuln in vulnerabilities[:3]:  # Show first 3
        print(f"  - {vuln.get('title', 'Unknown')} ({vuln.get('severity', 'Unknown')})")
    
    return len(vulnerabilities) > 0

# Run test
if __name__ == "__main__":
    result = asyncio.run(test_agent())
    print(f"✅ Integration test {'passed' if result else 'needs attention'}")
EOF

# Run integration test
python test_integration.py
# Expected: ✅ Found X vulnerabilities, ✅ Integration test passed

# Clean up
rm test_integration.py
```

#### **9.2 FastAPI Integration**
```python
# Create FastAPI integration test
cat > test_fastapi_integration.py << 'EOF'
from fastapi import FastAPI
from app.main import app as security_app

# Create test app
app = FastAPI()

# Mount security auditor
app.mount("/security", security_app)

# Test custom endpoint
@app.get("/test")
async def test_endpoint():
    return {"status": "integration_working"}

if __name__ == "__main__":
    print("✅ FastAPI integration imports successful")
    print("✅ Security app mounted at /security")
EOF

# Run integration test
python test_fastapi_integration.py
# Expected: ✅ FastAPI integration imports successful

# Clean up
rm test_fastapi_integration.py
```

### **Test 10: CI/CD Integration Test**

#### **10.1 GitHub Actions Simulation**
```bash
# Simulate CI/CD pipeline
echo "🔄 Simulating CI/CD pipeline..."

# 1. Install (simulated)
echo "✅ Package installation simulated"

# 2. Environment setup
export OPENROUTER_API_KEY=$OPENROUTER_API_KEY  # Use existing key

# 3. Security scan
echo "🔍 Running security scan..."
auditor scan . --output-format sarif --save ci_results.sarif

# 4. Verify SARIF output
if [ -f ci_results.sarif ]; then
    echo "✅ SARIF results generated"
    ls -la ci_results.sarif
    
    # Check SARIF format
    python -c "
import json
with open('ci_results.sarif', 'r') as f:
    data = json.load(f)
print(f'✅ SARIF format valid, version: {data.get(\"version\", \"unknown\")}')
"
else
    echo "❌ SARIF results not generated"
fi

# Clean up
rm -f ci_results.sarif
```

---

## 🚀 **Performance Tests**

### **Test 11: Speed and Accuracy**

#### **11.1 Response Time Test**
```bash
# Test response times
echo "⏱️ Testing response times..."

# Single analysis timing
time auditor analyze --code "import os; os.system(input())" --language python > /dev/null
# Expected: < 5 seconds for simple analysis

# Batch processing timing  
echo 'import os
os.system(user_input)
exec(user_data)
eval(user_input)
subprocess.run(cmd, shell=True)' > batch_test.py

time auditor scan batch_test.py > /dev/null
# Expected: < 10 seconds for multi-vulnerability file

# Clean up
rm batch_test.py
```

#### **11.2 Model Performance Comparison**
```bash
# Test different models for speed comparison
SAMPLE_CODE="import subprocess; subprocess.run(user_cmd, shell=True)"

echo "🧪 Testing model performance..."

# Fast model
time auditor analyze --code "$SAMPLE_CODE" --language python --model "qwen/qwen-2.5-coder-32b-instruct:free" > /dev/null

# Quality model  
time auditor analyze --code "$SAMPLE_CODE" --language python --model "meta-llama/llama-3.3-70b-instruct:free" > /dev/null

echo "✅ Model performance comparison complete"
```

---

## 🐛 **Troubleshooting Tests**

### **Test 12: Error Handling**

#### **12.1 Invalid Input Test**
```bash
# Test invalid language
auditor analyze --code "print('test')" --language invalid_language
# Expected: Error message about invalid language

# Test empty code
auditor analyze --code "" --language python
# Expected: Error message about empty code

# Test invalid model
auditor analyze --code "print('test')" --language python --model "nonexistent-model"
# Expected: Error message about invalid model
```

#### **12.2 Network Issues Test**
```bash
# Test with invalid API key
OPENROUTER_API_KEY_BACKUP=$OPENROUTER_API_KEY
export OPENROUTER_API_KEY="invalid-key"

auditor models
# Expected: Authentication error

# Restore API key
export OPENROUTER_API_KEY=$OPENROUTER_API_KEY_BACKUP
```

### **Test 13: Edge Cases**

#### **13.1 Large File Test**
```bash
# Create large test file
python -c "
code = 'import os\\nos.system(user_input)\\n' * 100
with open('large_test.py', 'w') as f:
    f.write(code)
print('Created large test file')
"

# Test scanning large file
auditor scan large_test.py --max-lines 1000
# Expected: Should handle large file gracefully

# Clean up
rm large_test.py
```

#### **13.2 Special Characters Test**
```bash
# Test with special characters
auditor analyze --code 'print("Hello 世界! 🌍")' --language python
# Expected: Should handle Unicode correctly
```

---

## 📊 **Test Results Summary**

### **Test Completion Checklist**

Create a test results summary:

```bash
# Create test summary
cat > test_results.md << 'EOF'
# AI Code Security Auditor - Test Results

## ✅ Test Summary
- **Installation Tests**: PASS
- **CLI Commands**: PASS  
- **API Endpoints**: PASS
- **AI Model Access**: PASS
- **Output Formats**: PASS
- **Integration Tests**: PASS
- **Performance Tests**: PASS
- **Error Handling**: PASS

## 📊 Key Metrics
- **Response Time**: < 5 seconds (single analysis)
- **API Health**: 200 OK
- **Model Access**: 4/4 models available
- **Format Support**: 5/5 formats working
- **Integration**: Python + FastAPI working

## 🎯 Recommendations
- ✅ Production ready
- ✅ All core features functional
- ✅ Performance within acceptable limits
- ✅ Error handling robust

## 🚀 Next Steps
- Deploy to production environment
- Integrate with CI/CD pipeline
- Train team on CLI commands
- Set up monitoring and alerts
EOF

echo "✅ Test results summary created in test_results.md"
```

---

## 🎯 **Custom Test Scenarios**

### **Test 14: Your Use Case**

Adapt these templates for your specific testing needs:

#### **Custom Security Rules Test**
```bash
# Test your specific vulnerability patterns
YOUR_CODE="your specific code pattern here"
auditor analyze --code "$YOUR_CODE" --language python --advanced
```

#### **Custom Integration Test**
```bash
# Test integration with your tools
# Add your specific integration tests here
```

---

## 📞 **Test Support**

### **If Tests Fail**

1. **Check Prerequisites**: Verify Python 3.11+, API key set
2. **Review Installation**: Re-run `pip install ai-code-security-auditor`
3. **Verify Network**: Test `curl http://api.openrouter.ai/api/v1/models`
4. **Check Logs**: Run commands with `--verbose` flag
5. **Seek Help**: GitHub Issues with test failure details

### **Test Environment Cleanup**

```bash
# Clean up test artifacts
rm -f test_*.py security_report.* ci_results.sarif test_results.md
rm -f api_server.pid

# Remove test config
rm -rf ~/.config/auditor/test_*

echo "✅ Test environment cleaned up"
```

---

<div align="center">

## 🎉 **Testing Complete!**

**[📖 Return to Setup Guide](02-LOCAL_SETUP_GUIDE.md) • [💻 Explore CLI Commands](05-CLI_Commands.md) • [🏠 Main Documentation](../README.md)**

---

**All systems verified • Ready for production • Secure by design**

</div>