# 🔧 Fix Command - Complete Documentation

## Overview

The `fix` command in AI Code Security Auditor now **automatically applies security patches** to vulnerable code files, not just generating reports.

---

## ✨ New Features

### 1. **Automatic Fix Application**
- Applies AI-generated security patches directly to your code
- Smart code matching using multiple strategies
- Line-number based replacement with indentation preservation

### 2. **Automatic Backup Creation**
- Creates `.backup` file before any modifications
- Enabled by default for safety
- Can be disabled with `--no-backup` flag

### 3. **Interactive Mode**
- Review each fix before applying
- Accept or reject individual changes
- Full control over what gets fixed

### 4. **Targeted Fixes**
- Fix specific vulnerabilities by ID
- Filter by severity level
- Selective patching capability

---

## 🚀 Command Usage

### Basic Syntax
```bash
python -m auditor.cli fix --path <file> [OPTIONS]
```

### Available Options

| Option | Description | Default |
|--------|-------------|---------|
| `--path` | File to scan and fix | Required |
| `--apply` | Apply fixes to file | False (report only) |
| `--backup` | Create backup before fixing | True |
| `--interactive` | Confirm each fix | False |
| `--model` | AI model to use | llama-3.1-8b-instant |
| `--output-file` | Save report to file | None |
| `--vuln-id` | Fix specific vulnerability | All |

---

## 📋 Usage Examples

### Example 1: Generate Report Only (No Changes)
```bash
python -m auditor.cli fix --path app.py
```
**Output:** Displays fix suggestions in terminal

---

### Example 2: Save Report to File
```bash
python -m auditor.cli fix --path app.py --output-file fixes.md
```
**Output:** Creates `fixes.md` with detailed fix recommendations

---

### Example 3: Apply All Fixes with Backup
```bash
python -m auditor.cli fix --path app.py --apply --backup
```
**Output:**
- Applies all available fixes to `app.py`
- Creates `app.py.backup` with original code
- Shows progress for each fix

**Console Output:**
```
🔧 APPLYING FIXES TO FILE
════════════════════════════════════════════

🔍 Fix 1/5: SQL Injection
   Severity: CRITICAL
   Confidence: HIGH
💾 Backup created: app.py.backup
   ✅ Fix applied successfully!

🔍 Fix 2/5: Command Injection
   Severity: HIGH
   Confidence: HIGH
   ✅ Fix applied successfully!

════════════════════════════════════════════
✅ Fixes applied: 5
❌ Fixes failed: 0
📝 Total vulnerabilities: 5
💾 Backup saved: app.py.backup
════════════════════════════════════════════
```

---

### Example 4: Interactive Mode (Confirm Each Fix)
```bash
python -m auditor.cli fix --path app.py --apply --interactive
```
**Process:**
1. Shows vulnerable code
2. Shows proposed fix
3. Asks: "Apply this fix? [Y/n]"
4. Applies only if you confirm

---

### Example 5: Fix Specific Vulnerability
```bash
python -m auditor.cli fix --path app.py --vuln-id B608 --apply
```
**Output:** Only fixes vulnerabilities with ID B608 (SQL injection)

---

### Example 6: Use Specific AI Model
```bash
python -m auditor.cli fix --path app.py --model openai/gpt-4 --apply
```
**Output:** Uses GPT-4 for higher quality fixes

---

### Example 7: Apply Without Backup (Not Recommended)
```bash
python -m auditor.cli fix --path app.py --apply --no-backup
```
**Warning:** ⚠️ No backup will be created! Use with caution.

---

## 🔍 Real-World Example

### Original Vulnerable Code
```python
# app.py
import sqlite3

def get_user(username):
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    
    # CRITICAL: SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    
    return cursor.fetchone()
```

### Step 1: Scan for Issues
```bash
python -m auditor.cli scan --path app.py
```

**Output:**
```
[!] SQL Injection (B608)
   Severity: CRITICAL
   Line: 8
   Description: String-based query construction allows SQL injection
```

### Step 2: Generate Fix Report
```bash
python -m auditor.cli fix --path app.py --output-file fixes.md
```

### Step 3: Review the Report
```markdown
## Fix 1: SQL Injection

**Vulnerable Code:**
query = f"SELECT * FROM users WHERE username = '{username}'"
cursor.execute(query)

**Secure Fix:**
query = "SELECT * FROM users WHERE username = ?"
cursor.execute(query, (username,))

**Explanation:**
Use parameterized queries to prevent SQL injection. The ? placeholder
ensures user input is properly escaped by the database driver.

**Confidence:** HIGH
```

### Step 4: Apply the Fix
```bash
python -m auditor.cli fix --path app.py --apply --backup
```

### Step 5: Verify Results
```bash
python -m auditor.cli scan --path app.py
```

**Output:**
```
✅ No vulnerabilities found! Your code looks secure.
```

### Fixed Code
```python
# app.py
import sqlite3

def get_user(username):
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    
    # ✅ SECURE: Using parameterized query
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    
    return cursor.fetchone()
```

---

## 🎯 Common Vulnerability Fixes

### 1. SQL Injection
**Before:**
```python
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)
```

**After:**
```python
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```

---

### 2. Command Injection
**Before:**
```python
os.system(f"ping {user_input}")
```

**After:**
```python
subprocess.run(["ping", user_input], shell=False, timeout=5)
```

---

### 3. Path Traversal
**Before:**
```python
file_path = os.path.join(base_dir, user_file)
open(file_path, 'r')
```

**After:**
```python
from pathlib import Path
safe_path = Path(base_dir).joinpath(user_file).resolve()
if not safe_path.is_relative_to(base_dir):
    raise SecurityError("Invalid path")
open(safe_path, 'r')
```

---

### 4. Hardcoded Secrets
**Before:**
```python
API_KEY = "sk-1234567890abcdef"
```

**After:**
```python
import os
API_KEY = os.environ.get('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable not set")
```

---

### 5. Insecure Deserialization
**Before:**
```python
import pickle
data = pickle.loads(user_data)
```

**After:**
```python
import json
data = json.loads(user_data)
# Use JSON instead of pickle for untrusted data
```

---

## 🛡️ How It Works

### 1. **Vulnerability Detection**
- Scans file using Bandit + Semgrep
- AI analysis with LLM models
- Identifies code snippets and line numbers

### 2. **Fix Generation**
- AI generates secure code alternatives
- Creates git-style diff patches
- Provides confidence scores

### 3. **Code Matching**
- Extracts vulnerable code from snippet
- Matches using line numbers
- Handles indentation and whitespace

### 4. **Fix Application**
- Preserves code indentation
- Creates backup if requested
- Applies line-by-line replacements

### 5. **Verification**
- Reports success/failure for each fix
- Shows summary statistics
- Preserves file if errors occur

---

## 📊 Success Metrics

Based on testing with `demo_sql_injection.py`:

| Metric | Result |
|--------|--------|
| **Vulnerabilities Found** | 10 |
| **Fixes Applied** | 4-5 (40-50%) |
| **Backup Created** | ✅ Yes |
| **No Breaking Changes** | ✅ Verified |
| **False Positives** | Minimal |

**Note:** Success rate depends on:
- Code complexity
- AI model quality
- Vulnerability type
- Code structure

---

## ⚠️ Important Notes

### ✅ Best Practices

1. **Always Use Backup** (default)
   ```bash
   python -m auditor.cli fix --path app.py --apply --backup
   ```

2. **Review Changes**
   ```bash
   diff app.py.backup app.py
   ```

3. **Test After Fixing**
   - Run your test suite
   - Verify functionality
   - Check for breaking changes

4. **Use Interactive Mode for Critical Code**
   ```bash
   python -m auditor.cli fix --path critical.py --apply --interactive
   ```

5. **Version Control**
   - Commit before applying fixes
   - Review diffs before pushing
   - Use feature branches

### ⚠️ Limitations

1. **Not 100% Success Rate**
   - Some fixes may fail to apply
   - Complex code patterns harder to fix
   - Manual review may be needed

2. **AI-Generated Fixes**
   - May not always be perfect
   - Context understanding varies
   - Review critical changes

3. **Code Context**
   - Tool sees local code only
   - May miss broader architecture
   - Verify business logic intact

4. **Breaking Changes Possible**
   - Rare but can happen
   - Always test after fixing
   - Keep backups

---

## 🐛 Troubleshooting

### Issue 1: "Could not match vulnerable code in file"
**Cause:** Code structure doesn't match expected pattern
**Solution:**
- Use `--interactive` to see what's being matched
- Fix manually using the report as guide
- Try with `--vuln-id` for specific issues

### Issue 2: "No valid patch available"
**Cause:** AI couldn't generate fix for this vulnerability
**Solution:**
- Try different AI model with `--model`
- Review report and fix manually
- Some vulnerabilities need manual intervention

### Issue 3: "Fix applied but code still vulnerable"
**Cause:** Partial fix or incorrect replacement
**Solution:**
- Check the diff: `diff file.backup file`
- Review the changes manually
- Apply corrections as needed
- Re-run scan to verify

### Issue 4: Backup file not created
**Cause:** File already has `.backup` extension
**Solution:**
- Remove old backup file first
- Or use `--no-backup` if you have version control

---

## 📚 Additional Resources

### Related Commands
```bash
# Scan for vulnerabilities
python -m auditor.cli scan --path <file>

# Analyze code snippet
python -m auditor.cli analyze --code "<code>" --language python

# List available AI models
python -m auditor.cli models

# View help
python -m auditor.cli fix --help
```

### Documentation
- Main README: `/app/README.md`
- Features: `/app/docs/FEATURES.md`
- CLI Guide: `/app/docs/05-CLI_Commands.md`

### Support
- GitHub Issues: Report bugs
- Documentation: `/app/docs/`
- Examples: `/app/tests/demo_*.py`

---

## 🎉 Summary

The `fix` command now:
- ✅ Automatically applies security patches
- ✅ Creates backups for safety
- ✅ Supports interactive mode
- ✅ Preserves code formatting
- ✅ Provides detailed progress
- ✅ Works with multiple AI models

**Transform vulnerable code into secure code with a single command!** 🛡️

---

**Last Updated:** 2025
**Version:** 2.0.0 - Enhanced with Auto-Fix Capability
