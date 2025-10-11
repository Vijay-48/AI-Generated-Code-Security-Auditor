# 📂 External Folder Scanning Guide

Quick reference for scanning files and directories anywhere on your computer.

---

## 🎯 Basic Commands

### Scan a Single File
```bash
# Windows
python -m auditor.cli scan --path C:\Users\YourName\Documents\myfile.py

# Linux/Mac
python -m auditor.cli scan --path /home/user/documents/myfile.py
```

### Scan an Entire Directory
```bash
# Windows
python -m auditor.cli scan --path C:\Users\YourName\Projects\MyApp

# Linux/Mac  
python -m auditor.cli scan --path /home/user/projects/myapp
```

### Scan Current Directory
```bash
python -m auditor.cli scan --path .
```

### Scan Parent Directory
```bash
python -m auditor.cli scan --path ..
```

---

## 🎨 Output Formats

### Save as JSON
```bash
python -m auditor.cli scan --path C:\MyProject --output-format json --output-file report.json
```

### Save as Markdown
```bash
python -m auditor.cli scan --path C:\MyProject --output-format markdown --output-file report.md
```

### Save as GitHub Actions Format
```bash
python -m auditor.cli scan --path C:\MyProject --output-format github --output-file github_report.md
```

### Save as SARIF (Security tools)
```bash
python -m auditor.cli scan --path C:\MyProject --output-format sarif --output-file results.sarif
```

---

## 🔍 Filtering Options

### Include Specific Files
```bash
# Only Python files
python -m auditor.cli scan --path C:\MyProject --include "*.py"

# Multiple patterns
python -m auditor.cli scan --path C:\MyProject --include "*.js" --include "*.ts"
```

### Exclude Specific Files
```bash
# Exclude test files
python -m auditor.cli scan --path C:\MyProject --exclude "*/tests/*"

# Exclude multiple patterns
python -m auditor.cli scan --path C:\MyProject --exclude "*/node_modules/*" --exclude "*/build/*"
```

### Severity Filtering
```bash
# Only critical vulnerabilities
python -m auditor.cli scan --path C:\MyProject --severity-filter critical

# High and above
python -m auditor.cli scan --path C:\MyProject --severity-filter high

# Medium and above
python -m auditor.cli scan --path C:\MyProject --severity-filter medium
```

---

## 🚀 Real-World Examples

### Example 1: Scan a GitHub Repository
```bash
# Clone the repo
git clone https://github.com/username/repo.git C:\Projects\repo

# Scan it
python -m auditor.cli scan --path C:\Projects\repo

# Generate report
python -m auditor.cli scan --path C:\Projects\repo --output-file security_report.md
```

### Example 2: Scan Your Own Project
```bash
# Navigate to project
cd C:\MyProjects\WebApp

# Scan backend only
python -m auditor.cli scan --path .\backend

# Scan frontend only
python -m auditor.cli scan --path .\frontend

# Scan everything
python -m auditor.cli scan --path .
```

### Example 3: Scan Network Share (Windows)
```bash
python -m auditor.cli scan --path \\server\share\project
```

### Example 4: Scan with Specific Model
```bash
# Use faster model
python -m auditor.cli scan --path C:\MyProject --model llama-3.1-8b-instant

# Use more powerful model
python -m auditor.cli scan --path C:\MyProject --model groq/compound
```

---

## 📊 Advanced Options

### Advanced Analysis (Slower, More Detailed)
```bash
python -m auditor.cli scan --path C:\MyProject --advanced
```

### Fail on High Severity (CI/CD)
```bash
python -m auditor.cli scan --path C:\MyProject --fail-on-high
```

### Combined Options
```bash
python -m auditor.cli scan \
    --path C:\MyProject \
    --output-format json \
    --output-file results.json \
    --severity-filter high \
    --exclude "*/tests/*" \
    --advanced
```

---

## 🗂️ Supported File Types

| Language | Extensions |
|----------|-----------|
| Python | `.py` |
| JavaScript | `.js`, `.jsx` |
| TypeScript | `.ts`, `.tsx` |
| Java | `.java` |
| Go | `.go` |

---

## 🎯 Common Use Cases

### 1. Security Audit Before Deployment
```bash
cd C:\Production\MyApp
python -m auditor.cli scan --path . --severity-filter high --output-file pre_deployment_audit.md
```

### 2. Code Review for Pull Request
```bash
# Scan only changed files
python -m auditor.cli scan --path C:\MyApp\src\new_feature
```

### 3. Hackathon Project Demo
```bash
# Scan demo files
python -m auditor.cli scan --path C:\HackathonProject\tests

# Generate nice report
python -m auditor.cli scan --path C:\HackathonProject --output-format github --output-file demo_report.md
```

### 4. Client Project Audit
```bash
# Scan client's codebase
python -m auditor.cli scan --path C:\Clients\CompanyName\project --output-file audit_report_2025.md
```

---

## 💡 Pro Tips

### 1. Automatic Exclusions
These are automatically skipped (no need to exclude manually):
- `node_modules/`
- `venv/`, `env/`, `myenv/`
- `.git/`
- `__pycache__/`
- `build/`, `dist/`
- `.log`, `.tmp` files

### 2. Speed Up Scanning
```bash
# Use faster model
python -m auditor.cli scan --path C:\MyProject --model llama-3.1-8b-instant

# Skip advanced analysis
python -m auditor.cli scan --path C:\MyProject --no-advanced
```

### 3. Batch Scanning Large Projects
```bash
# Scan in modules
python -m auditor.cli scan --path C:\MyProject\module1
python -m auditor.cli scan --path C:\MyProject\module2
python -m auditor.cli scan --path C:\MyProject\module3
```

### 4. Create Security Dashboard
```bash
# Generate JSON for parsing
python -m auditor.cli scan --path C:\MyProject --output-format json --output-file results.json

# Then parse with your own scripts
python parse_results.py results.json
```

---

## ⚠️ Important Notes

### Windows Path Issues
If you have spaces in paths, use quotes:
```bash
python -m auditor.cli scan --path "C:\Users\My Name\My Project"
```

### Large Projects
For projects with 1000+ files:
- First scan takes 5-10 minutes
- Subsequent scans are faster (caching)
- Consider scanning by modules

### Network Shares
Scanning network shares works but may be slow:
```bash
python -m auditor.cli scan --path \\server\share\project
```

---

## 🔥 Quick Demo Commands

```bash
# Demo 1: Scan test files
python -m auditor.cli scan --path tests/

# Demo 2: Scan with specific vulnerabilities
python -m auditor.cli scan --path tests/demo_sql_injection.py

# Demo 3: Scan and generate fixes
python -m auditor.cli fix --path tests/demo_sql_injection.py

# Demo 4: Scan external project
python -m auditor.cli scan --path C:\ExternalProject

# Demo 5: Full audit with report
python -m auditor.cli scan --path C:\MyProject --output-format markdown --output-file security_audit.md
```

---

## 📞 Troubleshooting

### Issue: "No supported files found"
**Solution:** Make sure the directory contains `.py`, `.js`, `.ts`, `.java`, or `.go` files

### Issue: Scan takes too long
**Solution:** Use `--exclude` to skip large directories like `node_modules/`

### Issue: Path not found
**Solution:** Use absolute paths or check spelling:
```bash
# Check if path exists (Windows)
dir C:\MyProject

# Check if path exists (Linux/Mac)
ls /home/user/project
```

---

## ✅ Summary

**Scan any directory:**
```bash
python -m auditor.cli scan --path <directory>
```

**Save report:**
```bash
python -m auditor.cli scan --path <directory> --output-file report.md
```

**Filter by severity:**
```bash
python -m auditor.cli scan --path <directory> --severity-filter high
```

**That's it!** 🎉

Now you can scan any project on your computer for security vulnerabilities!
