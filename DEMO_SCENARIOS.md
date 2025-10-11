# 🎬 AI Code Security Auditor - Demo Scenarios

Ready-to-use demo scenarios for your presentation. Copy-paste these commands!

---

## 🚀 QUICK START DEMO (5 minutes)

Perfect for short presentations. Shows all key features quickly.

### Setup (Do this before presentation)

```bash
# 1. Open terminal and navigate to project
cd A:\Project\AI-Generated-Code-Security-Auditor

# 2. Activate virtual environment
myenv\Scripts\activate  # Windows
source myenv/bin/activate  # Linux/Mac

# 3. Set large font in terminal for visibility
# Right-click → Properties → Font → Size 20

# 4. Clear terminal
cls  # Windows
clear  # Linux/Mac

# 5. Test that everything works
python -m auditor.cli test
```

---

### Scenario 1: Basic Vulnerability Detection (1 min)

**What to say:**
> "Let me show you how quickly this tool detects vulnerabilities."

**Command:**
```bash
python -m auditor.cli scan --path test_vulnerable.py
```

**What to highlight:**
- Speed: "Notice it scanned in just a few seconds"
- Severity levels: "Critical, High, Medium, Low - color-coded"
- Details: "Each finding shows line number, description, and severity"
- Count: "Found 13 vulnerabilities in this small file"

**Key line to read aloud:**
> "We detected SQL injection, command injection, hardcoded secrets, and unsafe deserialization."

---

### Scenario 2: AI-Powered Fix Generation (2 min)

**What to say:**
> "Now here's where it gets interesting - watch as AI generates actual fixes for these issues."

**Command:**
```bash
python -m auditor.cli fix --path test_vulnerable.py --output-file demo_fixes.md
```

**Then open the file:**
```bash
notepad demo_fixes.md  # Windows
cat demo_fixes.md | head -50  # Linux/Mac
```

**What to highlight:**
- "For each vulnerability, we get:"
  - Detailed explanation of the security risk
  - Exact code changes needed (diff format)
  - Confidence level
  - Potential issues to watch for
  - Additional recommendations

**Key line to read aloud:**
> "This isn't just a bug report - it's a security tutorial for each issue."

---

### Scenario 3: Code Snippet Analysis (1 min)

**What to say:**
> "We can also analyze code snippets on the fly, perfect for checking something quickly."

**Command:**
```bash
python -m auditor.cli analyze --code "exec(user_data)" --language python
```

**What to highlight:**
- Instant analysis
- No need to save to file
- Great for learning/exploration

**Alternative dangerous code to demo:**
```bash
# SQL Injection
python -m auditor.cli analyze --code "query = 'SELECT * FROM users WHERE id=' + user_id" --language python

# Command Injection
python -m auditor.cli analyze --code "os.system('ping ' + user_input)" --language python
```

---

### Scenario 4: JSON Output for CI/CD (30 sec)

**What to say:**
> "For CI/CD integration, we can output in machine-readable formats."

**Command:**
```bash
python -m auditor.cli scan --path test_vulnerable.py --output-format json --output-file results.json
```

**Show the file:**
```bash
type results.json  # Windows
cat results.json  # Linux/Mac
```

**What to highlight:**
- "Perfect for automated pipelines"
- "Can fail builds on high severity"
- "Integrates with any CI/CD system"

---

## 🎯 DETAILED DEMO (10 minutes)

For longer presentations with more interaction.

### Scenario 5: Directory Scanning

**What to say:**
> "The tool can scan entire projects, not just single files."

**Setup:**
Create a small project structure:
```bash
mkdir demo_project
cd demo_project
echo "import os; os.system(user_input)" > insecure1.py
echo "exec(request.data)" > insecure2.py
echo "password = 'hardcoded123'" > insecure3.py
cd ..
```

**Command:**
```bash
python -m auditor.cli scan --path demo_project
```

**What to highlight:**
- Scans multiple files
- Aggregates results
- Shows per-file breakdown

---

### Scenario 6: Advanced Mode

**What to say:**
> "Advanced mode provides deeper AI analysis with detailed explanations."

**Command:**
```bash
python -m auditor.cli scan --path test_vulnerable.py --advanced
```

**What to highlight:**
- Takes longer but more thorough
- Additional security insights
- Educational explanations

---

### Scenario 7: Filtering by Severity

**What to say:**
> "We can filter to focus on the most critical issues first."

**Command:**
```bash
# Show only critical and high severity
python -m auditor.cli scan --path test_vulnerable.py --severity-filter high
```

**What to highlight:**
- Helps prioritize remediation
- Reduces noise for large projects
- Critical issues first

---

### Scenario 8: Different Output Formats

**Markdown/GitHub format:**
```bash
python -m auditor.cli scan --path test_vulnerable.py --output-format markdown
```

**SARIF format (for security tools):**
```bash
python -m auditor.cli scan --path test_vulnerable.py --output-format sarif --output-file results.sarif
```

**What to say:**
> "Different teams need different formats. We support table, JSON, Markdown, SARIF, and GitHub Actions formats."

---

### Scenario 9: Specific Vulnerability Fix

**What to say:**
> "You can also generate fixes for specific vulnerabilities only."

**Command:**
```bash
# Fix only SQL injection issues
python -m auditor.cli fix --path test_vulnerable.py --vuln-id B608
```

**What to highlight:**
- Targeted remediation
- Useful for incremental fixes
- Focus on highest priority

---

### Scenario 10: Model Selection

**What to say:**
> "We support multiple AI models - you can choose based on your needs."

**Fast model:**
```bash
python -m auditor.cli scan --path test_vulnerable.py --model llama-3.1-8b-instant
```

**Powerful model:**
```bash
python -m auditor.cli scan --path test_vulnerable.py --model llama-3.3-70b-versatile
```

**What to highlight:**
- Trade-off between speed and accuracy
- Fast model for quick checks
- Powerful model for thorough analysis

---

## 💡 BACKUP DEMOS (If main demo fails)

### Demo B1: Quick Scan Script

If the CLI hangs, use the quick scan:

```bash
python quick_scan.py test_vulnerable.py
```

**What to say:**
> "We also have a simplified scanner for Windows users. Let me show you that instead."

---

### Demo B2: Show Pre-Generated Results

Have these files ready before presentation:

```bash
# Generate before presentation
python -m auditor.cli scan --path test_vulnerable.py --output-file scan_results.txt
python -m auditor.cli fix --path test_vulnerable.py --output-file fix_results.md
```

**If demo fails:**
```bash
# Show pre-generated results
type scan_results.txt
notepad fix_results.md
```

**What to say:**
> "Let me show you a scan I ran earlier to save time."

---

### Demo B3: Models List

Always works, shows preparation:

```bash
python -m auditor.cli models
```

**What to say:**
> "Let me show you the AI models we support and their capabilities."

---

## 🎤 DEMO SCRIPT WITH NARRATION

### Full 5-Minute Demo Script

**[Clear screen, show prompt]**

> "I'm going to demonstrate three core features of our AI Code Security Auditor in just five minutes."

**[Type command slowly so audience can see]**

```bash
python -m auditor.cli scan --path test_vulnerable.py
```

**[Wait for results, scroll through]**

> "In less than 10 seconds, the tool analyzed this Python file and identified 13 security vulnerabilities. See here - SQL injection on line 13, command injection on line 9, hardcoded AWS credentials on line 18. Each finding includes severity, line number, and description."

**[Pause for effect]**

> "But detection is just the beginning. Watch this."

**[Type next command]**

```bash
python -m auditor.cli fix --path test_vulnerable.py --output-file fixes.md
```

**[Open the file]**

> "For each vulnerability, our AI generates a complete fix. Look at this SQL injection fix here. It shows the exact code diff, explains why it's vulnerable, suggests parameterized queries as the solution, and even warns about potential issues. This isn't just a scanner - it's a security mentor."

**[Quick third demo]**

```bash
python -m auditor.cli analyze --code "exec(user_data)" --language python
```

> "We can also analyze code snippets instantly. Perfect for learning or quick checks during development. Notice it immediately identified this as a critical code execution vulnerability and explained why it's dangerous."

**[Conclusion]**

> "Three features: fast detection, intelligent fixes, instant analysis. All powered by AI, all free and open-source. Questions?"

---

## 🎯 INTERACTIVE DEMO IDEAS

### Idea 1: Ask Audience for Vulnerable Code

**What to say:**
> "Does anyone want to suggest a potentially vulnerable line of code? I'll analyze it live."

**Be ready for common suggestions:**
```bash
# If they say "eval"
python -m auditor.cli analyze --code "eval(input())" --language python

# If they say "SQL"
python -m auditor.cli analyze --code "query = 'SELECT * FROM users WHERE name=' + username" --language python

# If they say "password"
python -m auditor.cli analyze --code "password = 'admin123'" --language python
```

---

### Idea 2: Compare Before/After

**Show vulnerable code:**
```python
# Create vulnerable.py
def login(username):
    query = f"SELECT * FROM users WHERE name='{username}'"
    return db.execute(query)
```

**Scan it:**
```bash
python -m auditor.cli fix --path vulnerable.py
```

**Show the fix, then create fixed version:**
```python
# Create secure.py
def login(username):
    query = "SELECT * FROM users WHERE name=?"
    return db.execute(query, (username,))
```

**Scan the fixed version:**
```bash
python -m auditor.cli scan --path secure.py
```

**Show no vulnerabilities!**

---

### Idea 3: Progressive Complexity

**Start simple:**
```bash
echo "password = 'test123'" > simple.py
python -m auditor.cli scan --path simple.py
```

**Add more issues:**
```bash
echo "os.system(user_input)" >> simple.py
python -m auditor.cli scan --path simple.py
```

**Show count increasing**

---

## 📊 METRICS TO MENTION DURING DEMO

- **Speed:** "Scanned in 8 seconds"
- **Coverage:** "13 different vulnerability types detected"
- **Accuracy:** "High confidence fixes with AI validation"
- **Scale:** "Can scan entire projects with thousands of files"
- **Cost:** "Completely free, no API costs to users"

---

## 🛡️ DEMO SAFETY TIPS

### Before Demo:

1. **Test everything** - Run all commands at least once
2. **Check API key** - Ensure Groq API key is valid and has quota
3. **Clean terminal** - Start with clear screen
4. **Large font** - Make it readable for audience
5. **Have backups** - Screenshots of successful runs
6. **Test internet** - Ensure stable connection
7. **Close unnecessary apps** - Reduce distraction/lag

### During Demo:

1. **Speak while typing** - Narrate what you're doing
2. **Pause for results** - Let audience absorb information
3. **Highlight key points** - Point to important output
4. **Stay calm** - If error occurs, have backup ready
5. **Engage audience** - Ask if they can see the screen

### If Something Fails:

1. **Don't panic** - "Let me try the alternative approach"
2. **Use backup** - Pre-generated results or screenshots
3. **Explain anyway** - "This would normally show..."
4. **Turn to teaching** - Explain the concept without demo
5. **Move on** - Don't waste time debugging live

---

## 🎬 SAMPLE TIMELINE

**Minute 0-1:** Introduction + Problem statement
**Minute 1-2:** Basic scan demo
**Minute 2-4:** Fix generation demo (main feature)
**Minute 4-5:** Quick code analysis + CI/CD format
**Minute 5+:** Questions

---

## 🏆 WINNING DEMO TIPS

1. **Practice 5+ times** - Until it's smooth
2. **Time yourself** - Stay within limits
3. **Prepare for failure** - Have Plan B, C
4. **Show enthusiasm** - Your energy matters
5. **Explain impact** - "This saves hours of manual review"
6. **Be confident** - You built this!

---

## 📝 COMMANDS CHEAT SHEET (Print This!)

```bash
# Basic scan
python -m auditor.cli scan --path test_vulnerable.py

# Generate fixes
python -m auditor.cli fix --path test_vulnerable.py --output-file fixes.md

# Analyze code
python -m auditor.cli analyze --code "exec(data)" --language python

# JSON output
python -m auditor.cli scan --path test_vulnerable.py --output-format json

# List models
python -m auditor.cli models

# Test installation
python -m auditor.cli test

# Quick scan (backup)
python quick_scan.py test_vulnerable.py
```

---

**You're ready! Go win that hackathon! 🚀**

Remember: The tool is impressive, but your presentation sells it. Be confident, be clear, be passionate!
