# 🪟 Windows Fix Guide - AI Code Security Auditor

If you're experiencing issues running the scanner on Windows (stuck at 0%), follow these solutions:

---

## ✅ Solution 1: Use Quick Scan Script (Easiest)

I've created a simplified script that works better on Windows:

```bash
# Instead of the CLI, use quick_scan.py
python quick_scan.py test_vulnerable.py
```

This bypasses the complex CLI framework and works directly.

---

## ✅ Solution 2: Update Your CLI Files

The CLI has been updated with Windows compatibility fixes. Make sure you have the latest version.

**What was fixed:**
- Added Windows ProactorEventLoop policy
- Better async/event loop handling
- Timeout protection

**To use the updated CLI:**
```bash
python -m auditor.cli scan --path test_vulnerable.py
```

---

## ✅ Solution 3: Diagnose the Issue

Run the diagnostic script to identify the specific problem:

```bash
python diagnose_issue.py
```

This will check:
- Python version
- Event loop policy
- Missing dependencies
- Async functionality

---

## 🔧 Common Issues & Fixes

### Issue 1: Stuck at 0% Progress

**Cause:** Windows async event loop issue

**Fix:**
```python
# Add this at the top of your script
import asyncio
import platform

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
```

✅ This is already fixed in the updated CLI

---

### Issue 2: RuntimeWarning about 'auditor.cli'

**Message:** `RuntimeWarning: 'auditor.cli' found in sys.modules`

**Fix:** This is just a warning and can be ignored. The code still works.

To suppress it:
```bash
python -W ignore -m auditor.cli scan --path test_vulnerable.py
```

---

### Issue 3: Missing Dependencies

**Cause:** Some packages not installed

**Fix:**
```bash
# Install all required packages
pip install -r requirements.txt

# Or install individually:
pip install click httpx openai bandit semgrep langgraph langchain chromadb
```

---

### Issue 4: Event Loop Already Running

**Error:** `RuntimeError: This event loop is already running`

**Fix:** Use the quick_scan.py script instead, or restart your Python environment:
```bash
deactivate
myenv\Scripts\activate
python -m auditor.cli scan --path test_vulnerable.py
```

---

## 🚀 Recommended Workflow for Windows

### Option A: Quick Scan (Recommended)

```bash
# Fast and reliable on Windows
python quick_scan.py your_file.py
```

### Option B: Full CLI

```bash
# Make sure you're in the project directory
cd A:\Project\AI-Generated-Code-Security-Auditor

# Activate virtual environment
myenv\Scripts\activate

# Run scan
python -m auditor.cli scan --path test_vulnerable.py
```

---

## 📋 Step-by-Step Troubleshooting

1. **Check Python Version**
   ```bash
   python --version
   # Should be Python 3.8 or higher
   ```

2. **Verify Virtual Environment**
   ```bash
   # Make sure you're in the venv
   where python
   # Should show path to myenv\Scripts\python.exe
   ```

3. **Check Dependencies**
   ```bash
   python diagnose_issue.py
   ```

4. **Test with Quick Scan**
   ```bash
   python quick_scan.py test_vulnerable.py
   ```

5. **If still stuck, try:**
   ```bash
   # Reinstall dependencies
   pip uninstall -y click httpx openai
   pip install click httpx openai
   
   # Try again
   python quick_scan.py test_vulnerable.py
   ```

---

## 🎯 Alternative Commands for Windows

If the main CLI is problematic, use these alternatives:

### Scan a file (without CLI)
```bash
python quick_scan.py your_file.py
```

### Analyze code snippet
```python
# Create a file: analyze_code.py
import asyncio
import platform

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from app.agents.security_agent import SecurityAgent

async def analyze():
    agent = SecurityAgent()
    result = await agent.run(
        code='os.system(user_input)',
        language='python',
        filename='test.py',
        preferred_model='llama-3.1-8b-instant',
        use_advanced_analysis=False
    )
    print(result)

asyncio.run(analyze())
```

Then run:
```bash
python analyze_code.py
```

---

## ✅ Verify Everything Works

Run this quick test:

```bash
# 1. Check Python
python --version

# 2. Check dependencies
python diagnose_issue.py

# 3. Quick scan test
python quick_scan.py test_vulnerable.py

# 4. If all good, try CLI
python -m auditor.cli scan --path test_vulnerable.py
```

---

## 💡 Pro Tips for Windows Users

1. **Always use virtual environment**
   ```bash
   python -m venv myenv
   myenv\Scripts\activate
   ```

2. **Use PowerShell or CMD, not Git Bash**
   - PowerShell: Better async support
   - CMD: More compatible
   - Git Bash: May have issues

3. **Run as Administrator if needed**
   - Right-click CMD/PowerShell
   - Select "Run as administrator"

4. **Check antivirus**
   - Some antivirus software blocks Python async operations
   - Temporarily disable or add exception

5. **Use the quick_scan.py for reliable results**
   - It's optimized for Windows
   - Faster and more stable

---

## 🔍 Debug Mode

To see what's happening during the scan:

```bash
# Set debug environment variable
set PYTHONVERBOSE=1
python -m auditor.cli scan --path test_vulnerable.py
```

Or use Python debugger:
```bash
python -m pdb -m auditor.cli scan --path test_vulnerable.py
```

---

## 📞 Still Having Issues?

If none of the above works:

1. **Check your setup:**
   - Python version: `python --version`
   - Virtual env: `where python`
   - Dependencies: `python diagnose_issue.py`

2. **Try the quick scan:**
   ```bash
   python quick_scan.py test_vulnerable.py
   ```

3. **Check the error logs:**
   - Look for specific error messages
   - Share the full error output for help

4. **Last resort - reinstall:**
   ```bash
   deactivate
   rmdir /s myenv
   python -m venv myenv
   myenv\Scripts\activate
   pip install -r requirements.txt
   python quick_scan.py test_vulnerable.py
   ```

---

## ✨ Summary

**Quick Fix:** Use `python quick_scan.py your_file.py`

**Full Fix:** 
1. Update CLI files (already done)
2. Use virtual environment
3. Run `python diagnose_issue.py`
4. Try `python quick_scan.py` first
5. Then try CLI if needed

**The quick_scan.py script is specifically designed for Windows and should work reliably!**

---

Good luck with your hackathon! 🚀
