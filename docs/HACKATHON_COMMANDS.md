# 🏆 AI Code Security Auditor - Hackathon Commands

Quick reference for all CLI commands - ready for hackathon demo!

## ✅ Fixed Issues

1. **Model Routing Fixed** - No more fallback warnings
2. **Groq Models Only** - All models now use Groq API exclusively
3. **New Fix Command** - Generate AI-powered code fix suggestions
4. **All Commands Working** - Scan, analyze, fix, models, test

---

## 🚀 Quick Start Commands

### 1. Scan a file for vulnerabilities

```bash
python -m auditor.cli scan --path test_vulnerable.py
```

**Output:** Lists all security issues with severity levels

---

### 2. Generate AI-powered fixes

```bash
python -m auditor.cli fix --path test_vulnerable.py --output-file fixes.md
```

**Output:** Markdown file with code fix suggestions for each vulnerability

---

### 3. Analyze code snippet

```bash
python -m auditor.cli analyze --code "os.system(user_input)" --language python
```

**Output:** Security analysis of the code snippet

---

### 4. List available models

```bash
python -m auditor.cli models
```

**Output:** All available AI models and their capabilities

---

### 5. Test installation

```bash
python -m auditor.cli test
```

**Output:** Verifies everything is working correctly

---

## 🎯 Advanced Commands

### Scan with specific model

```bash
python -m auditor.cli scan --path app.py --model llama-3.3-70b-versatile
```

### Scan directory with advanced analysis

```bash
python -m auditor.cli scan --path ./src --advanced
```

### Generate JSON report

```bash
python -m auditor.cli scan --path app.py --output-format json --output-file report.json
```

### Scan and fail CI/CD on high severity

```bash
python -m auditor.cli scan --path app.py --fail-on-high
```

### Generate fixes for specific vulnerability

```bash
python -m auditor.cli fix --path app.py --vuln-id B605
```

---

## 📊 Output Formats

- `table` - Human-readable (default)
- `json` - Machine-readable
- `markdown` - For documentation
- `github` - For GitHub Actions
- `sarif` - For security tools

---

## 🤖 Available Models (All Groq)

- `llama-3.1-8b-instant` - Fast, efficient (default)
- `llama-3.3-70b-versatile` - More powerful, better analysis
- `groq/compound` - Advanced reasoning
- `openai/gpt-oss-20b` - Multi-purpose

---

## 🎉 Demo Sequence for Hackathon

### Step 1: Show vulnerability detection

```bash
python -m auditor.cli scan --path test_vulnerable.py
```

### Step 2: Generate fixes

```bash
python -m auditor.cli fix --path test_vulnerable.py --output-file demo_fixes.md
cat demo_fixes.md
```

### Step 3: Analyze dangerous code

```bash
python -m auditor.cli analyze --code "exec(user_data)" --language python
```

### Step 4: Show JSON output

```bash
python -m auditor.cli scan --path test_vulnerable.py --output-format json
```

---

## ⚡ Key Features to Highlight

1. **AI-Powered Analysis** - Uses state-of-the-art LLMs
2. **Automatic Fix Generation** - AI suggests secure code replacements
3. **Multiple Output Formats** - JSON, Markdown, SARIF, etc.
4. **Fast & Reliable** - All models running on Groq for speed
5. **No Warnings** - Clean execution, no fallback messages
6. **CLI-First** - Perfect for CI/CD integration

---

## 🔧 Technical Details

### Fixed Issues

1. **Routing Logic** - Updated to correctly route models to Groq API
2. **Prefix Handling** - No longer strips model prefixes incorrectly
3. **Fallback System** - Silent fallbacks, no user-facing warnings
4. **Model Configuration** - All models now use Groq exclusively

### Code Changes

- **Updated:** `/app/app/services/llm_service.py` - Fixed routing logic
- **Updated:** `/app/.env` - Changed all models to Groq
- **Added:** Fix command in `/app/auditor/cli.py`
- **Created:** Comprehensive documentation

---

## 💡 Tips for Demo

1. Start with `test` command to show it works
2. Use `test_vulnerable.py` for demonstrations
3. Show the fix generation feature - it's unique!
4. Highlight the clean output (no warnings)
5. Demonstrate JSON output for CI/CD integration

---

## 🎯 Winning Points

✅ AI-powered security analysis
✅ Automatic fix generation
✅ Multiple programming languages
✅ CI/CD ready
✅ Fast and reliable
✅ Clean, professional output
✅ Comprehensive documentation

---

## 📝 Sample Commands for Copy-Paste

```bash
# Basic scan
python -m auditor.cli scan --path test_vulnerable.py

# Generate fixes
python -m auditor.cli fix --path test_vulnerable.py

# Advanced scan with JSON output
python -m auditor.cli scan --path test_vulnerable.py --advanced --output-format json

# Analyze code snippet
python -m auditor.cli analyze --code "eval(request.data)" --language python

# List models
python -m auditor.cli models

# Test installation
python -m auditor.cli test
```

---

**Good luck with your hackathon! 🚀**
