# 🏆 AI Code Security Auditor - Hackathon Edition

## 🚀 One-Minute Setup

```bash
# 1. Install dependencies (one-time setup)
bash setup.sh

# 2. You're ready! Test it:
python -m auditor.cli scan --path test_vulnerable.py
```

**That's it!** Your API keys are already configured in `.env`

---

## ⚡ Quick Demo Commands

### Show Available AI Models
```bash
python -m auditor.cli models
```

### Scan Your Code
```bash
# Scan a single file
python -m auditor.cli scan --path myfile.py

# Scan entire project
python -m auditor.cli scan --path ./your_project

# Scan with advanced AI analysis
python -m auditor.cli scan --path myfile.py --advanced
```

### Analyze Code Snippet
```bash
python -m auditor.cli analyze \
  --code "os.system(user_input)" \
  --language python
```

### Generate Reports
```bash
# GitHub-style markdown report
python -m auditor.cli scan --path . --output-format github --output-file security-report.md

# JSON for automation
python -m auditor.cli scan --path . --output-format json --output-file results.json

# SARIF for CI/CD (GitHub Security, Azure DevOps)
python -m auditor.cli scan --path . --output-format sarif --output-file results.sarif
```

---

## 🎯 Key Features

### 🤖 Dual-AI Provider
- **GroqCloud** - Ultra-fast inference (Llama, GPT-OSS, Compound) ✅ Working
- **OpenRouter** - 20+ models (Qwen, Mistral, DeepSeek) 🔒 Needs Credits

### 🔍 Triple-Layer Scanning
1. **Bandit** - Python security linter
2. **Semgrep** - Multi-language semantic analysis  
3. **AI Analysis** - LLM-powered detection

### 🔐 Secret Detection
- AWS Keys, API Tokens, Passwords
- GitHub Tokens, JWT, Private Keys
- Database Credentials

### 📊 Multiple Output Formats
- Table (terminal), JSON, Markdown, SARIF
- GitHub Actions format
- CI/CD ready

### 🛠️ AI-Powered Features
- Automatic fix suggestions
- Security explanations
- Vulnerability classification
- Risk assessment

---

## 🌟 Supported Languages

✅ Python (`.py`)
✅ JavaScript (`.js`, `.jsx`)
✅ TypeScript (`.ts`, `.tsx`)
✅ Java (`.java`)
✅ Go (`.go`)

---

## 💡 Hackathon Demo Script

```bash
# Step 1: Show available models
python -m auditor.cli models

# Step 2: Scan test file
python -m auditor.cli scan --path test_vulnerable.py

# Step 3: Advanced analysis
python -m auditor.cli scan --path test_vulnerable.py --advanced

# Step 4: Generate hackathon report
python -m auditor.cli scan --path test_vulnerable.py \
  --output-format github \
  --output-file hackathon-security-report.md

# Step 5: Show the report
cat hackathon-security-report.md

# Step 6: Scan your own project
python -m auditor.cli scan --path ./your_hackathon_project
```

---

## 🔧 Configuration

All settings in `.env` file:

```bash
# API Keys (Already configured!)
GROQ_API_KEY=gsk_...
OPENROUTER_API_KEY=sk-or-v1-...

# Primary Models (Using GroqCloud - Fast & Working!)
MODEL_PATCH_GENERATION=groq/compound
MODEL_QUALITY_ASSESSMENT=llama-3.3-70b-versatile
MODEL_FAST_CLASSIFICATION=llama-3.1-8b-instant
MODEL_CODE_GENERATION=llama-3.1-8b-instant
MODEL_SECURITY_ANALYSIS=openai/gpt-oss-20b
MODEL_DETAILED_EXPLANATION=llama-3.3-70b-versatile

# Fallback Models (Automatic failover)
MODEL_PATCH_GENERATION_SECONDARY=openai/gpt-oss-20b
MODEL_QUALITY_ASSESSMENT_SECONDARY=llama-3.1-8b-instant
MODEL_FAST_CLASSIFICATION_SECONDARY=openai/gpt-oss-20b
MODEL_DETAILED_EXPLANATION_SECONDARY=openai/gpt-oss-20b
```

**To change models**: Just edit `.env` and restart the scan. No code changes needed!

---

## ⚠️ Important Notes

### ✅ GroqCloud is Working
All GroqCloud models are configured and working perfectly:
- `groq/compound` - Code execution
- `llama-3.1-8b-instant` - Ultra-fast
- `llama-3.3-70b-versatile` - High quality
- `openai/gpt-oss-20b` - Multi-purpose

### 🔒 OpenRouter Needs Credits
OpenRouter API key is configured but needs credits.
- See `OPENROUTER_NOTE.md` for details
- Add credits at: https://openrouter.ai/settings/credits
- Or continue with GroqCloud (fully functional!)

---

## 📚 Documentation

- `README.md` - Full project README
- `QUICKSTART.md` - Quick start guide
- `FEATURES.md` - Complete feature list
- `OPENROUTER_NOTE.md` - OpenRouter setup info
- `/docs` - Comprehensive documentation

---

## 🧪 Test Your Setup

```bash
# Run comprehensive tests
bash final_test.sh

# Or test manually
python -m auditor.cli --help
python -m auditor.cli models
python -m auditor.cli scan --path test_vulnerable.py
```

---

## 🎪 Example Output

### Scanning Output
```
🔍 Scanning 1 files with llama-3.1-8b-instant

📁 File: test_vulnerable.py
------------------------------------------------------------
  🔴 start_process_with_a_shell (B605)
     Severity: HIGH
     Line: 9
     Description: Starting a process with a shell, possible injection detected

  🟠 Secret Detected: AWS Access Key (SECRET_AWS_ACCESS_KEY)
     Severity: CRITICAL
     Line: 18
     Description: AWS Access Key ID detected

📊 Scan complete: 13 vulnerabilities found across 1 files
```

### GitHub Report
```markdown
# 🛡️ AI Security Audit Results

## 🚨 13 vulnerabilities detected

| File | Issue | Severity | Line | AI Fix |
|------|-------|----------|------|--------|
| test_vulnerable.py | Command Injection | HIGH | 9 | ✅ |
| test_vulnerable.py | AWS Secret Key | CRITICAL | 18 | ✅ |
```

---

## 🏆 Winning the Hackathon

### Highlight These Features:
1. ✅ **Dual-AI Integration** - GroqCloud + OpenRouter
2. ✅ **Triple-Layer Scanning** - Bandit + Semgrep + AI
3. ✅ **Real Vulnerability Detection** - Not just demos
4. ✅ **Multiple AI Models** - 20+ models to choose from
5. ✅ **Automatic Fallback** - Reliability built-in
6. ✅ **CI/CD Ready** - SARIF format support
7. ✅ **Multi-Language** - Python, JS, TS, Java, Go
8. ✅ **Professional Output** - Multiple report formats

### Demo Flow:
1. Show model configuration
2. Scan vulnerable code live
3. Generate professional report
4. Show AI-powered fixes
5. Demonstrate on real project

---

## 🐛 Troubleshooting

### "No API keys found"
- Check `.env` file exists
- API keys are already configured!

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Bandit/Semgrep not found"
```bash
pip install bandit semgrep
```

### Need Help?
- Check `docs/ERROR_ANALYSIS_REPORT.md`
- Read `FEATURES.md` for complete details

---

## 📞 Support

- **Documentation**: `/docs` folder
- **Features**: `FEATURES.md`
- **Quick Start**: `QUICKSTART.md`
- **API Setup**: `OPENROUTER_NOTE.md`

---

## ✅ Ready Checklist

- [x] Dependencies installed
- [x] API keys configured
- [x] GroqCloud working
- [x] CLI commands tested
- [x] Sample scans successful
- [x] Reports generating

---

**You're ready to win! 🎉**

**Good luck with your hackathon tomorrow!** 🚀

---

*Version: 2.0.0 - Hackathon Edition*
*Last Updated: 2025*
