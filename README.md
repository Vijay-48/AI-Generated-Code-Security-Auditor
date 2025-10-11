# 🛡️ AI Code Security Auditor v2.0.0

> **Multi-AI powered security scanning tool with GroqCloud & OpenRouter integration for lightning-fast vulnerability detection**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GroqCloud](https://img.shields.io/badge/GroqCloud-Ultra--Fast-00D4AA.svg)](https://console.groq.com/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-Multi--Model-purple.svg)](https://openrouter.ai)

## 🚀 **Super Quick Start (5 Minutes!)**

### **1. Run Setup Script**
```bash
# One command installation
bash setup.sh
```

### **2. API Keys Already Configured! ✅**
Your `.env` file is ready with:
- ✅ **GroqCloud API** - Ultra-fast inference
- ✅ **OpenRouter API** - Access to 20+ models
- ✅ **Automatic fallback** - Secondary models configured

### **3. Test Installation**
```bash
# View available models
python -m auditor.cli models

# Scan sample vulnerable code
python -m auditor.cli scan --path test_vulnerable.py

# Quick code analysis
python -m auditor.cli analyze --code "os.system(user_input)" --language python
```

### **4. You're Ready! 🎉**
```bash
# Scan your project
python -m auditor.cli scan --path ./your_project

# Advanced AI analysis
python -m auditor.cli scan --path ./your_project --advanced

# Generate report for hackathon
python -m auditor.cli scan --path ./your_project --output-format github --output-file security-report.md
```

---

## 🎯 **Core Features**

### **🤖 Multi-Model AI Analysis**
- **GPT-4**: Premium analysis with OpenAI's latest model
- **GPT-3.5**: Fast and efficient analysis  
- **DeepCoder 14B**: Specialized for code patches
- **LLaMA 3.3**: Balanced quality assessment
- **Qwen Coder**: Ultra-fast vulnerability classification

### **🔍 Security Scanning**
- **Static Analysis**: Bandit (Python) + Semgrep (multi-language)
- **Secret Detection**: AWS keys, API tokens, passwords, certificates
- **Multi-Language**: Python, JavaScript, TypeScript, Java, Go
- **Real-time Analysis**: Instant feedback on security issues

### **📊 Smart Reporting** 
- **Multiple Formats**: Table, JSON, CSV, SARIF, GitHub Actions
- **AI-Generated Fixes**: Automatic patch suggestions
- **Severity Scoring**: Critical, High, Medium, Low classification
- **Detailed Explanations**: Educational security insights

---

## 🖥️ **CLI Commands**

### **Basic Scanning**
```bash
# Scan a single file
python -m auditor.cli scan --path myfile.py

# Scan entire directory
python -m auditor.cli scan --path ./src

# Scan with specific model
python -m auditor.cli scan --path myfile.py --model openai/gpt-4

# Advanced analysis with AI insights
python -m auditor.cli scan --path myfile.py --advanced
```

### **Direct Code Analysis**
```bash
# Analyze code snippet directly
python -m auditor.cli analyze \
  --code "exec(user_input)" \
  --language python

# With specific model
python -m auditor.cli analyze \
  --code "SELECT * FROM users WHERE id = $1" \
  --language python \
  --model openai/gpt-4
```

### **Output Formats**
```bash
# JSON output
python -m auditor.cli scan --path app.py --output-format json

# Save to file
python -m auditor.cli scan --path app.py --output-format github --output-file security-report.md

# SARIF for CI/CD integration
python -m auditor.cli scan --path . --output-format sarif --output-file results.sarif
```

### **Available Models**
```bash
# List all available AI models
python -m auditor.cli models
```

---

## 🌐 **API Usage**

### **Start API Server**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### **API Examples**
```bash
# Analyze code via API
curl -X POST "http://localhost:8000/audit" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import os; os.system(user_input)",
    "language": "python",
    "model": "openai/gpt-4",
    "use_advanced_analysis": true
  }'

# Check available models
curl "http://localhost:8000/models"

# Health check
curl "http://localhost:8000/health"
```

---

## 📖 **Example Usage**

### **1. Scan Vulnerable Python Code**
```python
# vulnerable_code.py
import os
import subprocess

def run_command(user_input):
    # ❌ VULNERABLE: Command injection
    os.system(user_input)
    
def db_query(user_id):
    # ❌ VULNERABLE: SQL injection
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute_query(query)

# ❌ VULNERABLE: Hardcoded credentials
AWS_SECRET_KEY = "AKIAIOSFODNN7EXAMPLE"
```

**Scan it:**
```bash
python -m auditor.cli scan --path vulnerable_code.py --advanced
```

**Results:**
```
Security Audit Results
================================================================================

File: vulnerable_code.py
--------------------------------------------------
  [!] Use of os.system (B605)
     Severity: HIGH
     Line: 5
     Description: Starting a process with a shell, possible injection attack vector
     AI Fix Available: HIGH confidence

  [!] Hardcoded password (B106)  
     Severity: HIGH
     Line: 11
     Description: Possible hardcoded password
     AI Fix Available: MEDIUM confidence

  [!] SQL Injection Risk
     Severity: CRITICAL
     Line: 9
     Description: Potential SQL injection via string formatting
     AI Fix Available: HIGH confidence
```

### **2. Get AI-Powered Fix Suggestions**
```bash
python -m auditor.cli analyze \
  --code "os.system(user_input)" \
  --language python \
  --model openai/gpt-4
```

**AI Response:**
```
🔍 Security Analysis:
==================

VULNERABILITY: Command Injection (CWE-78)
SEVERITY: CRITICAL

🚨 SECURITY RISK:
The code uses os.system() with user input, allowing attackers to execute arbitrary system commands.

🛠️ RECOMMENDED FIX:
```python
import subprocess

def run_command(user_input):
    # ✅ SECURE: Use subprocess with shell=False
    try:
        result = subprocess.run([user_input], shell=False, capture_output=True, text=True)
        return result.stdout
    except FileNotFoundError:
        return "Command not found"
```

📚 EXPLANATION:
- subprocess.run() with shell=False prevents command injection
- Input validation should be added for additional security
- Consider using a whitelist of allowed commands
```

---

## ⚙️ **Configuration**

### **Environment Variables**
```bash
# Required (choose one)
OPENROUTER_API_KEY=your_key_here     # Multi-model access
OPENAI_API_KEY=sk-your_key_here      # Direct OpenAI access

# Optional
DEFAULT_MODEL=openai/gpt-4           # Default AI model
API_PORT=8000                        # API server port  
MAX_FILE_SIZE_MB=10                  # Max file size to scan
SCAN_TIMEOUT_SECONDS=300             # Scan timeout
```

### **Supported File Types**
- **Python**: `.py`
- **JavaScript**: `.js`, `.jsx`  
- **TypeScript**: `.ts`, `.tsx`
- **Java**: `.java`
- **Go**: `.go`

---

## 🔧 **Troubleshooting**

### **Common Issues**

**1. "No API key found" Error**
```bash
# Solution: Set up your API key
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY or OPENAI_API_KEY
```

**2. "Command not found: auditor"**  
```bash
# Solution: Use module format
python -m auditor.cli --help
```

**3. "Model not available" Error**
```bash
# Solution: Check available models
python -m auditor.cli models
```

**4. "File too large" Error**
```bash
# Solution: Increase limit in .env
MAX_FILE_SIZE_MB=50
```

### **Getting Help**
```bash
# CLI help
python -m auditor.cli --help
python -m auditor.cli scan --help

# Check installation
python -c "import app.main; print('✅ Installation OK')"
```

---

## 📚 **Additional Resources**

### **API Documentation**
- Start server: `uvicorn app.main:app --reload`
- Visit: `http://localhost:8000/docs`

### **Getting API Keys**
- **OpenRouter**: https://openrouter.ai/ (Recommended)
  - Gives access to GPT-4, Claude, LLaMA, and more
  - Often cheaper than direct API access
  
- **OpenAI**: https://platform.openai.com/api-keys
  - Direct access to GPT-4 and GPT-3.5
  - Requires OpenAI account with credits

### **Model Comparison**
| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| GPT-4 | Medium | Highest | High | Production use |
| GPT-3.5 | Fast | High | Low | Development/testing |
| DeepCoder | Medium | High | Free | Code patches |
| LLaMA 3.3 | Medium | High | Free | Balanced analysis |
| Qwen Coder | Fast | Good | Free | Quick scans |

---

## 🏆 **Perfect for Hackathons!**

✅ **Quick Setup**: Clone, install, configure API key - ready in 2 minutes
✅ **Multiple AI Models**: GPT-4, GPT-3.5, and free alternatives  
✅ **Real Security Value**: Detects actual vulnerabilities in your code
✅ **Great Demo Material**: AI-powered fixes and explanations
✅ **Professional Output**: Multiple formats including GitHub Actions
✅ **CLI + API**: Both command-line and web API interfaces

---

## 📄 **License**

MIT License - see [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ for secure coding**

[🐛 Report Bug](https://github.com/Vijay-48/AI-Generated-Code-Security-Auditor/issues) • [✨ Request Feature](https://github.com/Vijay-48/AI-Generated-Code-Security-Auditor/issues) • [📖 Documentation](https://github.com/Vijay-48/AI-Generated-Code-Security-Auditor/wiki)

</div>