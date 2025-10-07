# 🚀 AI Code Security Auditor - Hackathon Setup

**Get up and running in 2 minutes!**

## ⚡ Quick Setup

### 1. Clone & Install
```bash
git clone https://github.com/Vijay-48/AI-Generated-Code-Security-Auditor.git
cd AI-Generated-Code-Security-Auditor
pip install -r requirements.txt
```

### 2. Setup API Key (Choose One)
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key:
# Option A: OpenRouter (recommended - access to multiple models)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Option B: OpenAI Direct (GPT-4 only)
OPENAI_API_KEY=sk-your_openai_api_key_here
```

**Get API Keys:**
- OpenRouter: https://openrouter.ai/ (gives access to GPT-4, Claude, LLaMA)
- OpenAI: https://platform.openai.com/api-keys (direct GPT-4 access)

### 3. Test Installation
```bash
# Run automated setup check
python setup_hackathon.py

# Test with sample code
python -m auditor.cli test
```

### 4. Start Scanning!
```bash
# Scan your code files
python -m auditor.cli scan --path app.py

# Analyze code snippets  
python -m auditor.cli analyze --code "os.system(user_input)" --language python
```

---

## 🎯 Hackathon Use Cases

### **Security Demo**
```bash
# Create vulnerable code
echo 'import os; os.system(user_input)' > demo.py

# Scan with AI analysis
python -m auditor.cli scan --path demo.py --model openai/gpt-4 --advanced

# Get detailed explanation
python -m auditor.cli analyze --code "os.system(user_input)" --language python
```

### **API Integration**
```bash
# Start API server
uvicorn app.main:app --reload

# Test API endpoint
curl -X POST "http://localhost:8000/audit" \
  -H "Content-Type: application/json" \
  -d '{"code": "exec(user_input)", "language": "python"}'
```

### **CI/CD Integration**
```bash
# Generate SARIF report for GitHub Actions
python -m auditor.cli scan --path . --output-format sarif --output-file security.sarif

# Generate GitHub-friendly report
python -m auditor.cli scan --path . --output-format github --output-file SECURITY.md
```

---

## 🤖 Available Models

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| `openai/gpt-4` | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 💰💰💰 | Production demos |
| `openai/gpt-3.5-turbo` | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 💰💰 | Fast development |
| `qwen/qwen-2.5-coder-32b-instruct:free` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 🆓 | Quick testing |

```bash
# List all models
python -m auditor.cli models

# Use specific model
python -m auditor.cli scan --path app.py --model openai/gpt-4
```

---

## 🔧 Common Commands

### **File Scanning**
```bash
# Single file
python -m auditor.cli scan --path vulnerable_app.py

# Directory scan
python -m auditor.cli scan --path ./src

# With AI insights
python -m auditor.cli scan --path app.py --advanced

# JSON output
python -m auditor.cli scan --path app.py --output-format json
```

### **Code Analysis**
```bash
# Python code
python -m auditor.cli analyze --code "exec(data)" --language python

# JavaScript code  
python -m auditor.cli analyze --code "eval(userInput)" --language javascript

# With specific model
python -m auditor.cli analyze --code "os.system(cmd)" --language python --model openai/gpt-4
```

### **Output Formats**
```bash
# Table (default)
python -m auditor.cli scan --path app.py

# JSON for processing
python -m auditor.cli scan --path app.py --output-format json

# GitHub Actions format
python -m auditor.cli scan --path app.py --output-format github

# SARIF for security tools
python -m auditor.cli scan --path app.py --output-format sarif
```

---

## 🚨 Troubleshooting

### **"No API keys found"**
```bash
# Check .env file exists
ls -la .env

# Verify content
cat .env | grep API_KEY

# Re-copy template if needed
cp .env.example .env
```

### **"Module not found"**
```bash
# Install dependencies
pip install -r requirements.txt

# Run from project root
python -m auditor.cli --help
```

### **"Command not found: auditor"**
```bash
# Use module format (always works)
python -m auditor.cli --help

# NOT: auditor --help
```

### **API Issues**
```bash
# Test API keys
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OpenRouter:', bool(os.getenv('OPENROUTER_API_KEY'))); print('OpenAI:', bool(os.getenv('OPENAI_API_KEY')))"

# Check model availability
python -m auditor.cli models
```

---

## 🏆 Demo Ideas

### **1. Live Security Scanning**
- Upload/paste code and get instant vulnerability detection
- Show AI-generated fixes in real-time
- Compare different AI models' analysis

### **2. Security Education Tool**
- Scan common vulnerable patterns
- Show detailed explanations from AI
- Generate secure code alternatives

### **3. CI/CD Integration**
- Set up GitHub Actions with SARIF output
- Automatically block deployments with critical vulnerabilities
- Generate security reports for PRs

### **4. Multi-Language Support**
- Scan Python, JavaScript, Java, Go code
- Show language-specific vulnerability patterns
- Compare security across different codebases

---

## 📊 Sample Vulnerable Code

Test the tool with these examples:

**Python (Command Injection)**
```python
import os
def run_user_command(cmd):
    os.system(cmd)  # VULNERABLE!
```

**JavaScript (XSS)**
```javascript
function displayUser(name) {
    document.innerHTML = "Hello " + name;  // VULNERABLE!
}
```

**SQL Injection**
```python
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"  # VULNERABLE!
    return db.execute(query)
```

**Hardcoded Secrets**
```python
API_KEY = "sk-1234567890abcdef"  # VULNERABLE!
AWS_SECRET = "AKIAIOSFODNN7EXAMPLE"  # VULNERABLE!
```

---

## 💡 Pro Tips

1. **Best Model for Demos**: Use `openai/gpt-4` for highest quality analysis
2. **Fast Testing**: Use `qwen/qwen-2.5-coder-32b-instruct:free` for quick scans
3. **Save Reports**: Always use `--output-file` to save results
4. **Advanced Analysis**: Use `--advanced` flag for detailed AI insights
5. **Multiple Formats**: Generate both human-readable and machine-readable outputs

---

## 🎯 Perfect for Hackathons!

✅ **2-minute setup** - Clone, install, configure  
✅ **Multiple AI models** - GPT-4, GPT-3.5, free alternatives  
✅ **Real security value** - Finds actual vulnerabilities  
✅ **Great demos** - AI explanations and fix suggestions  
✅ **Professional output** - SARIF, GitHub Actions formats  
✅ **CLI + API** - Both interfaces ready to use  

**Happy hacking! 🚀**