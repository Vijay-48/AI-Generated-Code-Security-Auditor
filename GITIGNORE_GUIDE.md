# 📋 .gitignore Guide - Protecting Your Repository

## 🎯 Purpose

The `.gitignore` file protects your repository by:
- ✅ **Preventing sensitive data leaks** (API keys, passwords, credentials)
- ✅ **Reducing repository size** (excluding large files like node_modules, models)
- ✅ **Keeping repo clean** (no build artifacts, temp files, logs)
- ✅ **Improving performance** (faster git operations)

---

## 🔒 What's Being Ignored

### 1. Sensitive Data (CRITICAL!)

These files contain secrets and MUST NEVER be committed:

```
.env                    # Environment variables with API keys
*.env                   # All environment files
*_api_key*             # Any file with "api_key" in name
*_secret*              # Any file with "secret" in name
*.pem, *.key, *.cert   # SSL certificates and private keys
id_rsa, id_rsa.pub     # SSH keys
config/secrets.yml     # Configuration with secrets
aws-credentials.json   # AWS credentials
```

**Why:** Committing these exposes your API keys to the world!

### 2. Virtual Environments (LARGE!)

```
venv/
env/
myenv/
.venv/
virtualenv/
node_modules/          # Can be 100MB-1GB+
```

**Why:** Virtual environments can be 100MB-1GB in size and are easily recreated.

**To recreate:**
```bash
# Python
python -m venv myenv
myenv\Scripts\activate
pip install -r requirements.txt

# Node.js
npm install  # or yarn install
```

### 3. Machine Learning Models (VERY LARGE!)

```
models/
*.pkl, *.pickle        # Pickled models
*.h5, *.hdf5          # Keras models
*.pth, *.pt           # PyTorch models
*.bin, *.onnx         # Binary model files
.cache/huggingface/   # Hugging Face cache (100MB-10GB+)
.cache/sentence_transformers/  # Sentence transformer models (100MB+)
chroma_db/            # Vector database (can be large)
```

**Why:** Models can be 100MB-10GB each. They should be downloaded on first run.

### 4. Build Artifacts & Dependencies

```
__pycache__/          # Python bytecode
*.pyc, *.pyo         # Compiled Python files
build/, dist/        # Build outputs
node_modules/        # Node.js packages
.eggs/, *.egg-info/  # Python package artifacts
target/              # Java build directory
```

**Why:** These are generated and can be rebuilt anytime.

### 5. Databases

```
*.db, *.sqlite, *.sqlite3  # SQLite databases
chroma_db/                 # ChromaDB vector store
*.mongodb                  # MongoDB dumps
dump.rdb                   # Redis dumps
```

**Why:** Database files can be large and contain user data.

### 6. IDE & Editor Settings

```
.vscode/             # VSCode settings
.idea/               # PyCharm/IntelliJ settings
*.swp, *.swo        # Vim swap files
.DS_Store           # macOS metadata
Thumbs.db           # Windows thumbnails
```

**Why:** These are user-specific and shouldn't be shared.

### 7. Logs & Temporary Files

```
*.log               # Log files
logs/              # Log directory
*.tmp, *.temp      # Temporary files
*.bak, *.backup    # Backup files
test_output/       # Test results
```

**Why:** These files can grow large and are regenerated.

### 8. Test & Coverage Output

```
.pytest_cache/
.coverage
htmlcov/
test_results/
*.sarif            # Security scan results
*_report.json      # Generated reports
```

**Why:** Test outputs are regenerated on each run.

---

## ✅ What's NOT Ignored (Exceptions)

These important files ARE committed:

```
!README.md           # Project documentation
!LICENSE            # License file
!CHANGELOG.md       # Change history
!.gitkeep          # Keeps empty directories
!.env.example      # Template without secrets
!requirements.txt  # Python dependencies list
!package.json      # Node.js dependencies list
```

---

## 🚨 How to Check What's Ignored

### Before Committing - Check Status
```bash
# See what will be committed
git status

# See what's being ignored
git status --ignored
```

### Check if a Specific File is Ignored
```bash
# Check if file is ignored
git check-ignore -v myfile.txt

# Check all ignored files in directory
git check-ignore -v **/*
```

### See All Tracked Files
```bash
# List all files git is tracking
git ls-files

# Count tracked files
git ls-files | wc -l
```

---

## 🔧 How to Use .gitignore

### 1. Initial Setup (First Time)

```bash
# The .gitignore is already created in your repo
# Just verify it exists
cat .gitignore

# Create your .env file from template
cp .env.example .env

# Add your API keys to .env (this file will be ignored)
nano .env  # or use any editor
```

### 2. Add Untracked Files

```bash
# See what's new
git status

# Add files (ignoring .gitignore patterns)
git add .

# Commit
git commit -m "Add new features"
```

### 3. If You Accidentally Committed Sensitive Data

**⚠️ WARNING: This is serious! Your API keys may be exposed!**

```bash
# Remove file from git but keep local copy
git rm --cached .env

# Commit the removal
git commit -m "Remove .env from tracking"

# Push
git push

# IMPORTANT: Rotate all exposed API keys immediately!
# - Generate new keys at provider websites
# - Update your local .env file
# - Never commit the new keys
```

**🔑 Rotate Your Keys:**
- Groq: https://console.groq.com/keys
- OpenRouter: https://openrouter.ai/keys
- OpenAI: https://platform.openai.com/api-keys

---

## 📊 Repository Size Benefits

### Before .gitignore:
```
Total Size: 2-5 GB
├── myenv/: 500MB-1GB
├── node_modules/: 200-500MB
├── chroma_db/: 100-500MB
├── models/: 500MB-2GB
├── __pycache__/: 50-100MB
└── logs/: 50-200MB
```

### After .gitignore:
```
Total Size: 10-50 MB
├── Source code: 5-20MB
├── Documentation: 2-10MB
├── Configuration: 1-5MB
└── Tests: 2-15MB
```

**Result: 98-99% size reduction!** 🎉

---

## 🛡️ Security Best Practices

### 1. Never Commit These

❌ `.env` files
❌ API keys or passwords
❌ Private keys (`.pem`, `.key`)
❌ SSH keys (`id_rsa`)
❌ Database credentials
❌ SSL certificates
❌ AWS credentials
❌ JWT secrets

### 2. Use Environment Variables

**Bad:**
```python
# DON'T DO THIS!
API_KEY = "sk-1234567890abcdef"
```

**Good:**
```python
# DO THIS INSTEAD!
import os
API_KEY = os.environ.get('API_KEY')
```

### 3. Create Template Files

Always provide `.env.example` with dummy values:
```bash
# .env.example (safe to commit)
GROQ_API_KEY=your_api_key_here
OPENROUTER_API_KEY=your_api_key_here

# .env (never commit - in .gitignore)
GROQ_API_KEY=gsk_actual_key_12345
OPENROUTER_API_KEY=sk-or-actual_key_67890
```

### 4. Pre-commit Checks

Add to your workflow:
```bash
# Before every commit, check for secrets
git diff --cached | grep -i "api_key\|password\|secret"

# If anything shows up, DON'T COMMIT!
```

---

## 🔍 Common Issues & Solutions

### Issue 1: File Still Being Tracked
**Problem:** Added file to .gitignore but git still tracks it

**Solution:**
```bash
# Remove from git tracking (keeps local file)
git rm --cached filename

# Or remove entire directory
git rm -r --cached directory/

# Commit the change
git commit -m "Stop tracking ignored files"
```

### Issue 2: Large Repository Size
**Problem:** Repository is too large

**Solution:**
```bash
# Check what's taking space
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  awk '/^blob/ {print substr($0,6)}' | sort -nr -k2 | head -20

# If you find large files, add them to .gitignore
# Then remove from history (be careful!)
```

### Issue 3: Accidentally Pushed Secrets
**Problem:** API keys exposed in commit history

**Solution:**
```bash
# 1. Immediately rotate the exposed keys!

# 2. Remove from history (use with caution)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# 3. Force push (warning: rewrites history)
git push origin --force --all

# 4. Update .gitignore to prevent future mistakes
```

---

## 💡 Pro Tips

### 1. Global .gitignore
Create a global ignore file for OS-specific files:
```bash
# Set global gitignore
git config --global core.excludesfile ~/.gitignore_global

# Add OS-specific files
echo ".DS_Store" >> ~/.gitignore_global
echo "Thumbs.db" >> ~/.gitignore_global
```

### 2. Check Ignored Files Before Committing
```bash
# Dry run - see what would be added
git add -n .

# Review carefully
git status

# Only then commit
git commit -m "Your message"
```

### 3. Use Git Hooks
Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Prevent committing .env files
if git diff --cached --name-only | grep -q "\.env$"; then
    echo "ERROR: Attempting to commit .env file!"
    echo "This file contains secrets and should not be committed."
    exit 1
fi
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

### 4. Regular Audits
```bash
# Monthly check for accidentally tracked files
git ls-files | grep -E "(\.env$|secret|password|\.key$|\.pem$)"

# If anything shows up, investigate and remove
```

---

## 📝 Quick Reference

### Check What's Ignored
```bash
git status --ignored
git check-ignore -v *
```

### Stop Tracking File
```bash
git rm --cached filename
git commit -m "Stop tracking file"
```

### Clean Up Untracked Files
```bash
# Preview what will be removed
git clean -n

# Remove untracked files
git clean -f

# Remove untracked files and directories
git clean -fd
```

### Verify .gitignore Works
```bash
# Create test file that should be ignored
echo "test" > test.log

# Check if ignored
git status  # Should not show test.log

# Clean up
rm test.log
```

---

## ✅ Checklist Before Pushing

- [ ] Verified no `.env` files are being committed
- [ ] Checked `git status` for sensitive files
- [ ] Confirmed no API keys in code
- [ ] No large files (>50MB) being committed
- [ ] No database files being committed
- [ ] No model files being committed
- [ ] Reviewed `git diff` before commit
- [ ] .gitignore is up to date

---

## 🎯 Summary

**Essential Rules:**
1. ✅ Never commit `.env` files
2. ✅ Never commit API keys or secrets
3. ✅ Exclude large files (models, node_modules, venv)
4. ✅ Keep repository clean and small
5. ✅ Use `.env.example` as template
6. ✅ Rotate keys immediately if exposed

**Your .gitignore protects:**
- 🔒 Your secrets and API keys
- 💾 Repository size (saves 98-99%)
- ⚡ Git performance
- 🧹 Clean project structure

**Remember:** Once committed, git history is permanent! Always check before pushing!

---

## 📞 Need Help?

If you accidentally committed secrets:
1. **Immediately rotate the exposed keys** ⚠️
2. Remove file from tracking: `git rm --cached .env`
3. Add to .gitignore if not already there
4. Commit and push the changes
5. Consider rewriting history if needed (advanced)

**The .gitignore file is your first line of defense against data leaks!** 🛡️
