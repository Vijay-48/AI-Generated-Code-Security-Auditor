# 🚀 AI Code Security Auditor - Quick Start Guide

## ⚡ Super Fast Setup (5 Minutes)

### 1. Check API Keys are Configured ✅

Your API keys are already configured in `.env` file:
- ✅ OpenRouter API Key
- ✅ GroqCloud API Key

### 2. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

### 3. Test Installation

```bash
# Check if everything works
python -m auditor.cli --help
```

### 4. View Available Models

```bash
python -m auditor.cli models
```

---

## 🎯 Basic Usage

### Scan a Single File

```bash
python -m auditor.cli scan --path myfile.py
```

### Scan Entire Directory

```bash
python -m auditor.cli scan --path ./src
```

### Scan with Specific Model

```bash
# Use GroqCloud's fast model
python -m auditor.cli scan --path myfile.py --model llama-3.1-8b-instant

# Use OpenRouter's Qwen model
python -m auditor.cli scan --path myfile.py --model qwen/qwen-2.5-coder-32b-instruct
```

### Advanced Analysis with AI Insights

```bash
python -m auditor.cli scan --path myfile.py --advanced
```

### Analyze Code Snippet Directly

```bash
python -m auditor.cli analyze \
  --code "os.system(user_input)" \
  --language python
```

---

## 📊 Output Formats

### Save as JSON

```bash
python -m auditor.cli scan --path app.py --output-format json --output-file results.json
```

### Generate GitHub Actions Report

```bash
python -m auditor.cli scan --path . --output-format github --output-file security-report.md
```

### Generate SARIF (for CI/CD)

```bash
python -m auditor.cli scan --path . --output-format sarif --output-file results.sarif
```

---

## 🔧 Model Configuration

### Currently Configured Models

All models are configured in `.env` file and can be changed:

**Primary Models:**
- `MODEL_PATCH_GENERATION=groq/compound` - For generating security fixes
- `MODEL_QUALITY_ASSESSMENT=qwen/qwen-2.5-72b-instruct` - For quality checks
- `MODEL_FAST_CLASSIFICATION=llama-3.1-8b-instant` - For fast scanning
- `MODEL_CODE_GENERATION=qwen/qwen-2.5-coder-32b-instruct` - Default model
- `MODEL_SECURITY_ANALYSIS=openai/gpt-oss-20b` - For security analysis
- `MODEL_DETAILED_EXPLANATION=meta-llama/llama-3.3-70b-instruct` - For explanations

**Secondary/Fallback Models:**
- Automatically used if primary models fail
- Configured via `MODEL_*_SECONDARY` variables in `.env`

### Change Models

Edit `.env` file to change any model:

```bash
# Example: Change code generation model
MODEL_CODE_GENERATION=groq/compound

# Example: Change classification model
MODEL_FAST_CLASSIFICATION=qwen/qwen-2.5-coder-32b-instruct
```

---

## 🎪 Hackathon Demo Commands

### Test with Sample Vulnerable Code

```bash
# Test the installation
python -m auditor.cli scan --path test_vulnerable.py
```

### Create Your Own Test File

```python
# Create test.py
import os

def run_command(user_input):
    os.system(user_input)  # Command injection!

API_KEY = "sk-1234567890"  # Hardcoded secret!
```

```bash
# Scan it
python -m auditor.cli scan --path test.py --advanced
```

### Scan a Real Project

```bash
# Scan your entire project
python -m auditor.cli scan --path ./your_project

# With severity filter (only show high/critical)
python -m auditor.cli scan --path ./your_project --severity-filter high

# Fail build on high severity issues
python -m auditor.cli scan --path ./your_project --fail-on-high
```

---

## 🔍 Supported Languages

- ✅ **Python** (`.py`)
- ✅ **JavaScript** (`.js`, `.jsx`)
- ✅ **TypeScript** (`.ts`, `.tsx`)
- ✅ **Java** (`.java`)
- ✅ **Go** (`.go`)

---

## 📋 Available Models

### GroqCloud Models (Ultra-fast)
- `groq/compound` - Python code execution
- `groq/compound-mini` - Lightweight version
- `openai/gpt-oss-20b` - Multi-purpose
- `openai/gpt-oss-120b` - Large model
- `llama-3.1-8b-instant` - Ultra-fast
- `llama-3.3-70b-versatile` - Advanced reasoning

### OpenRouter Models (Multi-model)
- `qwen/qwen-2.5-coder-32b-instruct` - Code generation
- `qwen/qwen-3-coder-480b-a35b` - Cutting edge
- `qwen/qwen-2.5-72b-instruct` - High capability
- `meta-llama/llama-3.3-70b-instruct` - Multilingual
- `mistralai/mistral-nemo` - 128K context
- `deepseek/deepseek-v3.1` - Free advanced model

---

## 🚨 Common Issues

### "No API keys found"
- Check `.env` file exists
- Verify API keys are set correctly
- Run: `python -m auditor.cli models` to check status

### "Module not found"
```bash
# Install missing dependencies
pip install -r requirements.txt
```

### "Bandit/Semgrep not found"
```bash
# Install security scanners
pip install bandit semgrep
```

---

## 🎯 Hackathon Tips

1. **Start Simple**: Test with `test_vulnerable.py` first
2. **Try Different Models**: Use `--model` flag to compare results
3. **Use Advanced Mode**: Add `--advanced` for AI insights
4. **Save Results**: Use `--output-file` to save reports
5. **Demo Multiple Formats**: Show JSON, GitHub, SARIF outputs
6. **Live Scanning**: Scan your hackathon project code live!

---

## 📚 More Documentation

- **Full Documentation**: Check `/docs` folder
- **CLI Commands**: See `docs/05-CLI_Commands.md`
- **Troubleshooting**: See `docs/ERROR_ANALYSIS_REPORT.md`

---

## 🏆 Win Your Hackathon!

**Key Features to Highlight:**
1. ✅ Multi-AI model support (OpenRouter + GroqCloud)
2. ✅ Real vulnerability detection (Bandit + Semgrep + AI)
3. ✅ Secret detection (API keys, passwords, credentials)
4. ✅ Multiple output formats (JSON, SARIF, GitHub Actions)
5. ✅ Automatic fallback models
6. ✅ Fast inference with GroqCloud
7. ✅ Advanced AI analysis and explanations
8. ✅ CI/CD ready (SARIF format)

**Demo Script:**
```bash
# 1. Show available models
python -m auditor.cli models

# 2. Scan vulnerable code
python -m auditor.cli scan --path test_vulnerable.py

# 3. Analyze with AI insights
python -m auditor.cli scan --path test_vulnerable.py --advanced

# 4. Generate hackathon report
python -m auditor.cli scan --path test_vulnerable.py --output-format github --output-file hackathon-security-report.md

# 5. Show the report
cat hackathon-security-report.md
```

---

**Good luck with your hackathon! 🎉**
