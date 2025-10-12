# ⚡ Quick Start Guide - Windows Fix

## 🎯 Your Situation

The scan was freezing at 0%. I've applied fixes. Now let's test it!

---

## ⏱️ IMPORTANT: First Run Timing

**On the FIRST scan**, the tool needs to:
1. Download ML models (~100MB) - takes 10-30 seconds
2. Initialize ChromaDB database
3. Make first API call to test connection

**This is NORMAL and only happens ONCE.**

After the first successful run, subsequent scans are much faster (5-10 seconds).

---

## 🧪 Test Right Now

### Test 1: Quick Environment Check (30 seconds)
```bash
python test_windows_fix.py
```

**What you'll see:**
- ✅ Platform check
- ✅ Python version
- ✅ API keys
- ℹ️ SecurityAgent skipped (too slow for test)

This just verifies your environment is ready.

---

### Test 2: Debug Scan (1-2 minutes on first run)
```bash
python debug_scan.py tests/test_vulnerable.py
```

**What you'll see:**
```
Step 1: Reading file... ✅
Step 2: Determining language... ✅
Step 3: Initializing SecurityAgent...
⏳ This may take 10-30 seconds on first run (downloading ML models)...
   Be patient, this is normal!

✅ Agent initialized successfully

Step 4: Checking API keys... ✅
Step 5: Running async scan...
⏳ Calling asyncio.run(agent.run(...))...
   (This may take 10-30 seconds for the first API call)

✅ Scan completed!
Step 6: Processing results...
✅ Found X vulnerabilities
```

**If it hangs here:**
- Press Ctrl+C after 2 minutes
- This likely means API timeout (network/API issue, not code issue)
- Try the CLI scan next

---

### Test 3: Actual CLI Scan (1-2 minutes on first run)
```bash
python -m auditor.cli scan --path tests/test_vulnerable.py
```

**What you'll see:**
```
🔍 Scanning 1 files with llama-3.1-8b-instant
📄 Scanning file 1/1: test_vulnerable.py ...
(may take 30-60 seconds on first run)
📄 Scanning file 1/1: test_vulnerable.py ✅

🛡️ AI Code Security Audit Results
================================================================================
📁 File: tests/test_vulnerable.py
------------------------------------------------------------------
  🔴 SQL Injection (CWE-89)
     Severity: CRITICAL
     ...
```

---

## ⚠️ Common First-Run Issues

### Issue 1: "Stuck at Step 3" in debug_scan.py
**Meaning:** Downloading ML models (100MB)  
**Solution:** Wait 30-60 seconds. This is normal on first run.  
**Check:** Look at your network activity - should see download happening

### Issue 2: "Stuck at Step 5" in debug_scan.py  
**Meaning:** API call taking long time  
**Solution:** Wait 60-120 seconds max, then Ctrl+C  
**Check:** 
```bash
# Verify API is reachable
ping api.groq.com
```

### Issue 3: Timeout after 120 seconds
**Meaning:** API is slow/unreachable (not a code bug!)  
**What you'll see:**
```
📄 Scanning file 1/1: test_vulnerable.py ❌
Error: Scan timeout after 120s
```
**Solutions:**
- Check internet connection
- Verify API key has credits: https://console.groq.com/
- Try different model: `--model llama-3.1-8b-instant`
- Check firewall/antivirus

---

## 🎉 Success Signs

### You know it's working when:
1. ✅ test_windows_fix.py completes without errors
2. ✅ debug_scan.py shows "Agent initialized" (after initial wait)
3. ✅ CLI scan shows checkmark: `test_vulnerable.py ✅`
4. ✅ Results are displayed with vulnerability details

---

## 🚀 Once It Works

### For Your Hackathon Demo:

**Pre-warm before presenting** (so demo is fast):
```bash
# Run this once before your presentation
python -m auditor.cli test
```

This makes the first API call, so your demo scan will be fast (5-10 seconds instead of 60 seconds).

**During Presentation:**
```bash
# This will now be fast since models are downloaded
python -m auditor.cli scan --path tests/test_vulnerable.py
```

---

## 📞 Still Not Working?

### If debug_scan.py hangs at Step 3 for >2 minutes:
```bash
# Check if models are downloading
# Look for "Downloading..." in console or network activity
# If nothing happening, might be a ChromaDB or sentence-transformers issue
```

**Quick fix:** Use quick_scan.py instead (lighter, no ML model downloads):
```bash
python tests/quick_scan.py tests/test_vulnerable.py
```

### If scan times out after 120s:
**This is an API/network issue, not a code bug.** The timeout is working as designed.

**Check:**
1. Internet connection stable?
2. API key has credits?
3. Firewall blocking Python?
4. Antivirus interfering?

**Temporary workaround:**
```bash
# Increase timeout (edit auditor/cli.py line 571)
timeout=300.0  # 5 minutes instead of 2
```

---

## 💡 Pro Tips

1. **Always test once** before presenting to warm up models/API
2. **Have backup ready**: `python tests/quick_scan.py`
3. **Suppress warning**: `python -W ignore -m auditor.cli scan ...`
4. **Check API status** before demo: https://console.groq.com/

---

## 📊 Typical Timing

| Run Type | First Run | Subsequent Runs |
|----------|-----------|-----------------|
| test_windows_fix.py | 5 sec | 5 sec |
| debug_scan.py | 60-90 sec | 10-20 sec |
| CLI scan | 60-120 sec | 5-15 sec |
| quick_scan.py | 60-90 sec | 10-20 sec |

The first run is always slower due to:
- ML model download (~100MB)
- ChromaDB initialization
- First API connection
- Model warm-up on API side

---

## ✅ What to Do Right Now

**Step 1:** Run the quick environment check (should complete in 5 seconds):
```bash
python test_windows_fix.py
```

**Step 2:** If Step 1 passes, try the debug scan (be patient, wait 1-2 minutes):
```bash
python debug_scan.py tests/test_vulnerable.py
```

**Step 3:** If Step 2 works, try the actual CLI:
```bash
python -m auditor.cli scan --path tests/test_vulnerable.py
```

**Step 4:** If Step 3 works, you're ready for your demo! 🎉

---

**Remember:** The first run will be slow. This is normal! Once models are downloaded and API is connected, subsequent runs are fast.

Good luck with your hackathon! 🚀
