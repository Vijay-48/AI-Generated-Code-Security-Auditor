# 🚀 Installation Guide - AI Code Security Auditor

**Quick installation for hackathon and development use**

## ⚡ Quick Install (2 minutes)

### Step 1: Clone Repository
```bash
git clone https://github.com/Vijay-48/AI-Generated-Code-Security-Auditor.git
cd AI-Generated-Code-Security-Auditor
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure API Key
```bash
# Copy environment template
cp .env.example .env

# Edit .env file and add your API key:
nano .env  # or use any text editor
```

**Add to .env file:**
```bash
# Choose one (or both):
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENAI_API_KEY=sk-your_openai_api_key_here
```

### Step 4: Test Installation
```bash
# Run setup verification
python setup_hackathon.py

# Test CLI
python -m auditor.cli --help

# Run sample test
python -m auditor.cli test
```

---

## 🔑 Getting API Keys

### Option 1: OpenRouter (Recommended)
1. Visit: https://openrouter.ai/
2. Create free account
3. Go to API Keys section
4. Create new key
5. Copy and paste into `.env` as `OPENROUTER_API_KEY`

**Benefits:**
- Access to multiple models (GPT-4, Claude, LLaMA)
- Often cheaper than direct API access
- Free tier available

### Option 2: OpenAI Direct
1. Visit: https://platform.openai.com/
2. Create account and add payment method
3. Go to API Keys section
4. Create new key (starts with `sk-`)
5. Copy and paste into `.env` as `OPENAI_API_KEY`

**Benefits:**
- Direct access to latest GPT models
- Fastest response times
- Full OpenAI feature access

---

## 🧪 Verification Tests

### Test 1: Basic CLI
```bash
python -m auditor.cli --help
```
**Expected:** Help text with available commands

### Test 2: Model Availability
```bash  
python -m auditor.cli models
```
**Expected:** List of available AI models with status

### Test 3: Sample Scan
```bash
echo 'import os; os.system(user_input)' > test.py
python -m auditor.cli scan --path test.py
rm test.py
```
**Expected:** Vulnerability detection report

### Test 4: API Server (Optional)
```bash
# Start server
uvicorn app.main:app --reload --port 8000

# Test in another terminal
curl http://localhost:8000/health
```
**Expected:** JSON health response

---

## 🔧 Troubleshooting

### "No module named 'app'"
```bash
# Ensure you're in project root directory
pwd  # Should end with AI-Generated-Code-Security-Auditor
python -m auditor.cli --help
```

### "No API keys found"
```bash
# Check .env file exists
ls -la .env

# Check content
cat .env | grep API_KEY

# Recreate if needed
cp .env.example .env
```

### "Command not found: auditor"
```bash
# Always use module format
python -m auditor.cli --help

# NOT: auditor --help (this won't work)
```

### "Import errors"
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check Python version (need 3.8+)
python --version
```

### API Key Issues
```bash
# Verify API keys are set
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('OpenRouter:', bool(os.getenv('OPENROUTER_API_KEY')))
print('OpenAI:', bool(os.getenv('OPENAI_API_KEY')))
"
```

---

## 🎯 Next Steps

Once installed successfully:

1. **Read the docs**: `docs/README_HACKATHON.md`
2. **Try demo commands**: `HACKATHON_SETUP.md`
3. **Scan your code**: `python -m auditor.cli scan --path your_project/`
4. **Start API server**: `uvicorn app.main:app --reload`
5. **Explore API docs**: http://localhost:8000/docs

---

## 📦 What Gets Installed

### Core Dependencies
- **FastAPI** - Web framework for API server
- **Click** - CLI framework
- **OpenAI** - AI model integration
- **Bandit/Semgrep** - Security scanners
- **Rich** - Terminal formatting

### Total Size
- ~500MB (includes AI/ML dependencies)
- ~2 minutes install time on average connection

### Python Version
- Minimum: Python 3.8
- Recommended: Python 3.10+
- Tested on: Python 3.11

---

Ready to start scanning? 🛡️