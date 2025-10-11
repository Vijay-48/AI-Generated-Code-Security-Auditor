# 🛡️ AI Code Security Auditor - CLI Usage Guide

Complete guide for using the AI Code Security Auditor command-line interface.

## 📋 Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Available Commands](#available-commands)
3. [Command Examples](#command-examples)
4. [Output Formats](#output-formats)
5. [Model Configuration](#model-configuration)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Groq API key (get from https://console.groq.com/keys)

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys
# Edit .env file and add your Groq API key:
GROQ_API_KEY=your_groq_api_key_here
```

### Verify Installation

```bash
# Test the installation
python -m auditor.cli test

# Check available models
python -m auditor.cli models
```

---

## 📝 Available Commands

### 1. `scan` - Scan files for security vulnerabilities

Scans one or more files for security issues using static analysis and AI.

**Usage:**
```bash
python -m auditor.cli scan --path <file_or_directory> [OPTIONS]
```

**Options:**
- `--path` (required): File or directory to scan
- `--model`: AI model to use (default: llama-3.1-8b-instant)
- `--output-format`: Output format (table, json, markdown, sarif, github)
- `--output-file`: Save output to file
- `--severity-filter`: Filter by severity (all, critical, high, medium, low)
- `--include`: Include file patterns (glob)
- `--exclude`: Exclude file patterns (glob)
- `--advanced`: Enable advanced AI analysis
- `--fail-on-high`: Exit with error on high/critical findings

### 2. `fix` - Generate code fix suggestions

Scans a file and provides AI-generated code fixes for vulnerabilities.

**Usage:**
```bash
python -m auditor.cli fix --path <file> [OPTIONS]
```

**Options:**
- `--path` (required): File to scan and fix
- `--model`: AI model to use for fix generation
- `--output-file`: Save fixes to file (markdown format)
- `--vuln-id`: Fix specific vulnerability ID only

### 3. `analyze` - Analyze code snippet

Analyzes a code snippet directly without scanning files.

**Usage:**
```bash
python -m auditor.cli analyze --code <code> --language <language> [OPTIONS]
```

**Options:**
- `--code` (required): Code snippet to analyze
- `--language` (required): Programming language (python, javascript, java, go)
- `--model`: AI model to use
- `--advanced`: Enable advanced analysis

### 4. `models` - List available models

Shows all available AI models and their capabilities.

**Usage:**
```bash
python -m auditor.cli models
```

### 5. `test` - Test installation

Runs a quick test to verify everything is working.

**Usage:**
```bash
python -m auditor.cli test
```

---

## 🎯 Command Examples

### Basic Scanning

```bash
# Scan a single file
python -m auditor.cli scan --path app.py

# Scan entire directory
python -m auditor.cli scan --path ./src

# Scan with specific model
python -m auditor.cli scan --path app.py --model llama-3.3-70b-versatile

# Scan with advanced AI analysis
python -m auditor.cli scan --path app.py --advanced
```

### Generate Fixes

```bash
# Generate fixes for a file
python -m auditor.cli fix --path vulnerable_code.py

# Save fixes to markdown file
python -m auditor.cli fix --path app.py --output-file fixes.md

# Fix specific vulnerability only
python -m auditor.cli fix --path app.py --vuln-id B605
```

### Output Formats

```bash
# JSON output
python -m auditor.cli scan --path app.py --output-format json

# Save to file
python -m auditor.cli scan --path app.py --output-format json --output-file results.json

# GitHub Actions format
python -m auditor.cli scan --path app.py --output-format github

# SARIF format (for security tools)
python -m auditor.cli scan --path app.py --output-format sarif --output-file results.sarif
```

### Filtering Results

```bash
# Show only high and critical issues
python -m auditor.cli scan --path app.py --severity-filter high

# Show only critical issues
python -m auditor.cli scan --path app.py --severity-filter critical

# Fail CI/CD on high severity
python -m auditor.cli scan --path app.py --fail-on-high
```

### Advanced Scanning

```bash
# Include specific patterns
python -m auditor.cli scan --path ./src --include "*.py" --include "*.js"

# Exclude specific patterns
python -m auditor.cli scan --path ./src --exclude "test_*.py" --exclude "*/migrations/*"

# Combined filtering
python -m auditor.cli scan --path ./src \
  --include "*.py" \
  --exclude "*/tests/*" \
  --exclude "*/venv/*" \
  --severity-filter medium
```

### Code Snippet Analysis

```bash
# Analyze Python code
python -m auditor.cli analyze \
  --code "os.system(user_input)" \
  --language python

# Analyze with advanced mode
python -m auditor.cli analyze \
  --code "exec(user_data)" \
  --language python \
  --advanced

# Use specific model
python -m auditor.cli analyze \
  --code "eval(request.GET['code'])" \
  --language python \
  --model llama-3.3-70b-versatile
```

---

## 📊 Output Formats

### Table Format (Default)

Human-readable table with emojis and colors.

```
🛡️ AI Code Security Audit Results
================================================================================

📁 File: app.py
------------------------------------------------------------
  🔴 SQL Injection (CWE-89)
     Severity: CRITICAL
     Line: 42
     Description: Unsanitized user input in SQL query
     🤖 AI Fix Available: HIGH confidence
```

### JSON Format

Machine-readable JSON for integration.

```json
[
  {
    "file_path": "app.py",
    "vulnerabilities": [
      {
        "id": "CWE-89",
        "title": "SQL Injection",
        "severity": "CRITICAL",
        "line_number": 42,
        "description": "Unsanitized user input in SQL query"
      }
    ]
  }
]
```

### Markdown/GitHub Format

Formatted for GitHub Actions and pull requests.

```markdown
# 🛡️ AI Security Audit Results

## 🚨 5 vulnerabilities detected

| File | Issue | Severity | Line | AI Fix |
|------|-------|----------|------|--------|
| `app.py` | SQL Injection | CRITICAL | 42 | ✅ |
```

### SARIF Format

Standard format for security tools integration.

```json
{
  "version": "2.1.0",
  "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "AI Code Security Auditor"
        }
      },
      "results": [...]
    }
  ]
}
```

---

## 🤖 Model Configuration

### Available Models (Groq)

All models are configured to use Groq for reliability and speed:

- **llama-3.1-8b-instant** - Ultra-fast, good for quick scans
- **llama-3.3-70b-versatile** - More capable, better for complex analysis
- **groq/compound** - Advanced reasoning with code execution
- **openai/gpt-oss-20b** - Strong multi-purpose analysis

### Model Selection

```bash
# Use fast model for quick scans
python -m auditor.cli scan --path app.py --model llama-3.1-8b-instant

# Use powerful model for thorough analysis
python -m auditor.cli scan --path app.py --model llama-3.3-70b-versatile

# Check current configuration
python -m auditor.cli models
```

### Environment Variables

Configure default models in `.env`:

```bash
MODEL_CODE_GENERATION=llama-3.1-8b-instant
MODEL_SECURITY_ANALYSIS=llama-3.3-70b-versatile
MODEL_PATCH_GENERATION=llama-3.3-70b-versatile
```

---

## 🔧 Troubleshooting

### No API keys found

**Error:** `❌ No API keys found!`

**Solution:**
```bash
# Add Groq API key to .env file
echo "GROQ_API_KEY=your_key_here" >> .env
```

### Module not found errors

**Error:** `ModuleNotFoundError: No module named 'xxx'`

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt
```

### No files found

**Error:** `❌ No supported files found to scan`

**Solution:**
- Ensure the path is correct
- Check file extensions are supported (.py, .js, .jsx, .ts, .tsx, .java, .go)
- Files in excluded directories won't be scanned (node_modules, venv, etc.)

### Model API errors

**Error:** `GroqCloud API error: ...`

**Solution:**
- Check your API key is valid
- Verify you have API quota remaining
- Try a different model with `--model` flag

---

## 📚 Additional Resources

### Supported Languages

- Python (.py)
- JavaScript (.js, .jsx)
- TypeScript (.ts, .tsx)
- Java (.java)
- Go (.go)

### Excluded Directories (Default)

The scanner automatically excludes:
- `__pycache__`
- `node_modules`
- `.git`
- `venv`, `env`, `myenv`, `.venv`
- `build`, `dist`, `target`
- `.pytest_cache`, `.coverage*`, `htmlcov`

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Security Scan
  run: |
    python -m auditor.cli scan \
      --path ./src \
      --output-format sarif \
      --output-file results.sarif \
      --fail-on-high
```

---

## 🎉 Quick Start Examples

### 1. Scan a Python project

```bash
python -m auditor.cli scan --path ./my_project
```

### 2. Generate fixes for vulnerable code

```bash
python -m auditor.cli fix --path vulnerable.py --output-file fixes.md
```

### 3. Analyze a dangerous code snippet

```bash
python -m auditor.cli analyze \
  --code "exec(request.POST['code'])" \
  --language python
```

### 4. CI/CD integration

```bash
python -m auditor.cli scan \
  --path ./src \
  --output-format json \
  --output-file scan-results.json \
  --fail-on-high
```

---

## 🏆 Best Practices

1. **Regular Scans:** Run scans on every commit or pull request
2. **Use Advanced Mode:** Enable `--advanced` for important code
3. **Review Fixes:** Always manually review AI-generated fixes
4. **Severity Filtering:** Focus on critical/high issues first
5. **Save Reports:** Use `--output-file` to track progress over time

---

## 💡 Tips

- Start with `--model llama-3.1-8b-instant` for speed
- Use `--advanced` for better accuracy (slower)
- Combine multiple output formats for different audiences
- Use `--fail-on-high` in CI/CD pipelines
- Generate fixes with `fix` command for quick remediation

---

**Need Help?** Run `python -m auditor.cli --help` for more information!
