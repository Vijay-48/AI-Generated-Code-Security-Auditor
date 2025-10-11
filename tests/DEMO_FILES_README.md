# 🎯 Demo Vulnerable Files - Hackathon Presentation

This folder contains **10 vulnerable code files** for demonstrating the AI Code Security Auditor during your hackathon presentation.

---

## 📁 Available Demo Files

### Python Files (7 files)
1. **`demo_sql_injection.py`** - SQL Injection vulnerabilities
   - String concatenation in queries
   - Format string vulnerabilities
   - DELETE injection

2. **`demo_command_injection.py`** - Command Injection attacks
   - os.system() vulnerabilities
   - subprocess.call() with shell=True
   - exec() vulnerabilities

3. **`demo_hardcoded_secrets.py`** - Hardcoded Credentials
   - API keys (AWS, GitHub, Stripe, OpenAI)
   - Database passwords
   - Private keys and JWT secrets

4. **`demo_xss_vulnerabilities.py`** - Cross-Site Scripting
   - Reflected XSS
   - Stored XSS
   - DOM-based XSS

5. **`demo_insecure_crypto.py`** - Weak Cryptography
   - MD5/SHA1 password hashing
   - Weak random number generation
   - Predictable session IDs

6. **`demo_path_traversal.py`** - Path Traversal attacks
   - Directory traversal
   - Arbitrary file read/write
   - Template injection

7. **`demo_insecure_deserialization.py`** - Code Injection
   - Unsafe pickle deserialization
   - eval() and exec() vulnerabilities
   - YAML deserialization

### JavaScript File (1 file)
8. **`demo_javascript_vulns.js`** - Node.js Vulnerabilities
   - SQL Injection
   - Command Injection
   - XSS, NoSQL Injection
   - Prototype Pollution

### Java File (1 file)
9. **`demo_java_vulns.java`** - Java Security Issues
   - SQL Injection
   - XXE (XML External Entity)
   - Insecure Deserialization
   - LDAP Injection

### Go File (1 file)
10. **`demo_golang_vulns.go`** - Go Security Vulnerabilities
    - SQL Injection
    - Command Injection
    - SSRF (Server-Side Request Forgery)
    - Weak Crypto

---

## 🚀 Quick Demo Commands

### Scan Individual Files

```bash
# Python files
python -m auditor.cli scan --path tests/demo_sql_injection.py
python -m auditor.cli scan --path tests/demo_command_injection.py
python -m auditor.cli scan --path tests/demo_hardcoded_secrets.py
python -m auditor.cli scan --path tests/demo_xss_vulnerabilities.py

# JavaScript file
python -m auditor.cli scan --path tests/demo_javascript_vulns.js

# Java file
python -m auditor.cli scan --path tests/demo_java_vulns.java

# Go file
python -m auditor.cli scan --path tests/demo_golang_vulns.go
```

### Scan All Demo Files at Once

```bash
# Scan entire tests directory
python -m auditor.cli scan --path tests/

# Scan with specific output format
python -m auditor.cli scan --path tests/ --output-format json --output-file demo_results.json

# Scan with severity filter (show only high/critical)
python -m auditor.cli scan --path tests/ --severity-filter high
```

---

## 🎬 Presentation Flow Suggestions

### 1. Start with SQL Injection (Most Common)
```bash
python -m auditor.cli scan --path tests/demo_sql_injection.py
```
**What to highlight:**
- Shows 3 different SQL injection patterns
- AI-powered detection
- Clear severity ratings

### 2. Show Hardcoded Secrets (Critical Issue)
```bash
python -m auditor.cli scan --path tests/demo_hardcoded_secrets.py
```
**What to highlight:**
- Detects API keys (AWS, GitHub, Stripe)
- Database credentials
- Critical severity issues

### 3. Demonstrate Command Injection
```bash
python -m auditor.cli scan --path tests/demo_command_injection.py
```
**What to highlight:**
- Multiple command injection patterns
- os.system(), subprocess, exec vulnerabilities

### 4. Show Multi-Language Support
```bash
# JavaScript
python -m auditor.cli scan --path tests/demo_javascript_vulns.js

# Java
python -m auditor.cli scan --path tests/demo_java_vulns.java

# Go
python -m auditor.cli scan --path tests/demo_golang_vulns.go
```
**What to highlight:**
- Works across 7+ programming languages
- Same quality detection for all languages

### 5. Generate AI-Powered Fixes
```bash
python -m auditor.cli fix --path tests/demo_sql_injection.py
```
**What to highlight:**
- AI generates code fixes
- Shows before/after diffs
- Provides security explanations

### 6. Scan Entire Directory
```bash
python -m auditor.cli scan --path tests/ --output-format github
```
**What to highlight:**
- Batch scanning capability
- Different output formats
- Summary statistics

---

## 📊 Expected Results

### demo_sql_injection.py
- **Expected vulnerabilities:** 3-5
- **Severity:** CRITICAL/HIGH
- **Types:** CWE-89 (SQL Injection)

### demo_command_injection.py
- **Expected vulnerabilities:** 5-7
- **Severity:** CRITICAL/HIGH
- **Types:** CWE-78 (Command Injection), CWE-95 (Code Injection)

### demo_hardcoded_secrets.py
- **Expected vulnerabilities:** 8-12
- **Severity:** CRITICAL
- **Types:** CWE-798 (Hardcoded Credentials)

### demo_xss_vulnerabilities.py
- **Expected vulnerabilities:** 4-6
- **Severity:** HIGH/MEDIUM
- **Types:** CWE-79 (Cross-Site Scripting)

### demo_insecure_crypto.py
- **Expected vulnerabilities:** 6-8
- **Severity:** HIGH/MEDIUM
- **Types:** CWE-327 (Weak Crypto), CWE-330 (Weak Random)

### demo_path_traversal.py
- **Expected vulnerabilities:** 5-7
- **Severity:** HIGH
- **Types:** CWE-22 (Path Traversal)

### demo_insecure_deserialization.py
- **Expected vulnerabilities:** 7-10
- **Severity:** CRITICAL
- **Types:** CWE-502 (Deserialization), CWE-95 (Code Injection)

---

## 🎯 Hackathon Presentation Tips

### Time Management
- **2 minutes:** Quick scan of demo_sql_injection.py
- **2 minutes:** Show hardcoded secrets detection
- **2 minutes:** Demonstrate multi-language support
- **2 minutes:** Generate AI fixes
- **2 minutes:** Scan entire directory

### What to Emphasize
1. ✅ **AI-Powered Detection** - Not just regex patterns
2. ✅ **Multi-Language Support** - Python, JS, Java, Go
3. ✅ **Automated Fixes** - AI generates secure code
4. ✅ **Severity Ratings** - Critical, High, Medium, Low
5. ✅ **CI/CD Integration** - Can be automated

### Common Questions to Prepare For

**Q: How accurate is the detection?**
A: Uses AI models trained on millions of code examples, combined with traditional static analysis tools (Bandit, Semgrep).

**Q: Can it fix the vulnerabilities?**
A: Yes! Use `--fix` command to generate AI-powered code fixes with explanations.

**Q: What languages are supported?**
A: Python, JavaScript, TypeScript, Java, Go, PHP, Ruby, C/C++

**Q: Can this integrate with CI/CD?**
A: Yes! Supports GitHub Actions, GitLab CI, Jenkins. Outputs SARIF format.

---

## 🔧 Advanced Demo Commands

### Generate JSON Report
```bash
python -m auditor.cli scan --path tests/ --output-format json --output-file security_report.json
```

### GitHub Actions Format
```bash
python -m auditor.cli scan --path tests/ --output-format github --output-file github_report.md
```

### SARIF Format (for security tools)
```bash
python -m auditor.cli scan --path tests/ --output-format sarif --output-file results.sarif
```

### Filter by Severity
```bash
# Show only critical vulnerabilities
python -m auditor.cli scan --path tests/ --severity-filter critical

# Show high and above
python -m auditor.cli scan --path tests/ --severity-filter high
```

### Use Specific AI Model
```bash
python -m auditor.cli scan --path tests/demo_sql_injection.py --model groq/compound
```

---

## 📈 Statistics to Mention

Across all 10 demo files:
- **Total vulnerabilities:** 50-70 expected
- **Critical severity:** 15-20
- **High severity:** 20-25
- **Medium severity:** 10-15
- **Languages covered:** 4 (Python, JavaScript, Java, Go)
- **CWE categories:** 15+ different types

---

## 💡 Pro Tips

1. **Pre-warm the API** before presenting:
   ```bash
   python -m auditor.cli test
   ```

2. **Have results ready** in case of network issues:
   ```bash
   python -m auditor.cli scan --path tests/ --output-file backup_results.md
   ```

3. **Show the vulnerable code** alongside the detection

4. **Explain real-world impact** of each vulnerability type

5. **Demonstrate the fix command** for at least one file

---

## 🎉 Summary

These demo files showcase:
- ✅ **10 different files** with real vulnerabilities
- ✅ **4 programming languages** (Python, JS, Java, Go)
- ✅ **15+ vulnerability types** (SQL Injection, XSS, etc.)
- ✅ **50-70 total vulnerabilities** for impressive demo
- ✅ **AI-powered detection & fixes**

Perfect for demonstrating the full capabilities of your AI Code Security Auditor to the hackathon jury!

Good luck! 🚀
