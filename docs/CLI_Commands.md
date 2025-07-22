# 📖 CLI Commands Reference

Complete reference for all AI Code Security Auditor command-line interface commands.

## 🔧 **Global Options**

```bash
--api-url TEXT     API base URL (default: http://localhost:8001)
--api-key TEXT     API authentication key  
--help             Show help message and exit
```

---

## 🔍 **Scanning Commands**

### **`auditor scan`** - Directory and File Scanning

Scan files or directories for security vulnerabilities.

#### **Basic Usage**
```bash
auditor scan [OPTIONS] [PATH]
```

#### **Options**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--path` | TEXT | `.` | Directory or file to scan |
| `--model` | TEXT | `deepcoder-14b-preview:free` | LLM model for analysis |
| `--output-format` | CHOICE | `table` | Output format: `table`, `json`, `github`, `markdown`, `sarif` |
| `--output-file` | TEXT | - | Save output to file |
| `--severity-filter` | CHOICE | `all` | Filter by severity: `all`, `critical`, `high`, `medium`, `low` |
| `--include` | TEXT | - | File patterns to include (can be repeated) |
| `--exclude` | TEXT | - | File patterns to exclude (can be repeated) |
| `--advanced/--no-advanced` | FLAG | False | Enable advanced multi-model analysis |
| `--fail-on-high/--no-fail-on-high` | FLAG | False | Exit with error on high/critical findings |

#### **Examples**

**Basic directory scan:**
```bash
# Scan current directory
auditor scan

# Scan specific directory  
auditor scan --path ./src
```

**Advanced filtering:**
```bash
# Filter by high severity only
auditor scan --severity-filter high

# Include only Python and JavaScript files
auditor scan --include "*.py" --include "*.js"

# Exclude test files and dependencies
auditor scan \
  --exclude "*/tests/*" \
  --exclude "*/node_modules/*" \
  --exclude "*/.git/*"
```

**Output formats:**
```bash
# GitHub Actions markdown format
auditor scan --output-format github --output-file security-report.md

# JSON for programmatic use
auditor scan --output-format json --output-file results.json

# SARIF for security tools integration
auditor scan --output-format sarif --output-file security.sarif
```

**AI model selection:**
```bash
# Use specific model
auditor scan --model "meta-llama/llama-3.3-70b-instruct:free"

# Enable advanced multi-model analysis
auditor scan --advanced
```

---

### **`auditor analyze`** - Direct Code Analysis

Analyze a code snippet directly without scanning files.

#### **Basic Usage**
```bash
auditor analyze [OPTIONS]
```

#### **Options**
| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--code` | TEXT | Yes | Code to analyze |
| `--language` | TEXT | Yes | Programming language (`python`, `javascript`, `java`, `go`) |
| `--model` | TEXT | No | LLM model for analysis |
| `--advanced/--no-advanced` | FLAG | False | Enable advanced analysis |

#### **Examples**

```bash
# Analyze Python code
auditor analyze \
  --code "import os; os.system(user_input)" \
  --language python

# Analyze with specific model
auditor analyze \
  --code "SELECT * FROM users WHERE id = " + userId \
  --language javascript \
  --model "agentica-org/deepcoder-14b-preview:free"

# Advanced analysis with multiple models
auditor analyze \
  --code "import subprocess; subprocess.call(cmd, shell=True)" \
  --language python \
  --advanced
```

---

## 🤖 **Model Management**

### **`auditor models`** - List Available Models

Display all available AI models and their recommended use cases.

#### **Basic Usage**
```bash
auditor models
```

#### **Example Output**
```
🤖 Available Models:
==================================================
  • deepcoder-14b-preview: agentica-org/deepcoder-14b-preview:free
  • kimi-dev-72b: moonshotai/kimi-dev-72b:free
  • qwen-2.5-coder-32b-instruct: qwen/qwen-2.5-coder-32b-instruct:free
  • llama-3.3-70b-instruct: meta-llama/llama-3.3-70b-instruct:free

💡 Recommendations:
  • code_patches: deepcoder-14b-preview
  • quality_assessment: llama-3.3-70b-instruct
  • fast_classification: qwen-2.5-coder-32b-instruct
  • security_explanations: kimi-dev-72b
```

---

## 📊 **Phase 9: Advanced Analytics Commands**

### **`auditor trends-detailed`** - Vulnerability Trend Analysis

Analyze vulnerability trends over time with advanced features.

#### **Basic Usage**
```bash
auditor trends-detailed [OPTIONS]
```

#### **Options**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--period` | INTEGER | 30 | Number of days to analyze |
| `--granularity` | CHOICE | `daily` | Time granularity: `hourly`, `daily`, `weekly` |
| `--include-forecast` | FLAG | False | Include trend forecasting |
| `--output` | CHOICE | `table` | Output format: `table`, `json`, `csv` |
| `--save` | TEXT | - | Save output to file |
| `--visual` | FLAG | False | Enable enhanced visualizations with sparklines |

#### **Examples**

```bash
# Basic trend analysis (last 30 days)
auditor trends-detailed

# Weekly analysis with forecasting
auditor trends-detailed --period 90 --granularity weekly --include-forecast

# Export to CSV with visual enhancements
auditor trends-detailed --period 60 --output csv --save trends.csv --visual
```

---

### **`auditor top-rules`** - Security Rule Analysis

Analyze the most frequently triggered security rules.

#### **Basic Usage**
```bash
auditor top-rules [OPTIONS]
```

#### **Options**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--limit` | INTEGER | 10 | Number of top rules to show |
| `--time-range` | TEXT | `30d` | Time range for analysis |
| `--severity` | CHOICE | - | Filter by severity: `critical`, `high`, `medium`, `low` |
| `--tool` | CHOICE | - | Filter by tool: `bandit`, `semgrep` |
| `--output` | CHOICE | `table` | Output format: `table`, `json`, `csv` |
| `--save` | TEXT | - | Save output to file |

#### **Examples**

```bash
# Top 10 rules (default)
auditor top-rules

# High severity rules only from Bandit
auditor top-rules --severity high --tool bandit --limit 15

# Export top 20 rules to CSV
auditor top-rules --limit 20 --output csv --save top-rules.csv
```

---

### **`auditor performance`** - Performance Analysis

Analyze scanning performance and optimization opportunities.

#### **Basic Usage**
```bash
auditor performance [OPTIONS]
```

#### **Options**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--include-cache` | FLAG | True | Include cache performance metrics |
| `--include-models` | FLAG | True | Include LLM model performance |
| `--breakdown-language` | FLAG | False | Break down by programming language |
| `--output` | CHOICE | `table` | Output format: `table`, `json`, `csv` |
| `--save` | TEXT | - | Save output to file |

#### **Examples**

```bash
# Comprehensive performance analysis
auditor performance --include-models --breakdown-language

# Cache performance only
auditor performance --include-cache --output json

# Export performance report
auditor performance --output csv --save performance-report.csv
```

---

### **`auditor generate-report`** - Report Generation

Generate comprehensive security analytics reports.

#### **Basic Usage**
```bash
auditor generate-report [OPTIONS]
```

#### **Options**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--report-type` | CHOICE | `security_summary` | Report type: `security_summary`, `vulnerability_trends`, `performance_analysis`, `top_rules_analysis` |
| `--time-range` | TEXT | `7d` | Time range: `1h`, `24h`, `7d`, `30d`, `90d`, `365d` |
| `--format` | CHOICE | `markdown` | Output format: `markdown`, `json`, `csv`, `text` |
| `--save` | TEXT | - | Save report to file |
| `--email` | TEXT | - | Email address to send report (future feature) |

#### **Examples**

```bash
# Weekly security summary
auditor generate-report \
  --report-type security_summary \
  --time-range 7d \
  --format markdown \
  --save weekly-report.md

# Monthly trends analysis
auditor generate-report \
  --report-type vulnerability_trends \
  --time-range 30d \
  --format json \
  --save trends-analysis.json

# Performance optimization report
auditor generate-report \
  --report-type performance_analysis \
  --time-range 30d \
  --format markdown
```

---

## 🏛️ **Legacy Analytics Commands**

### **`auditor summary`** - Scan Summary

Show summary of a specific scan or latest scan.

#### **Options**
| Option | Type | Description |
|--------|------|-------------|
| `--scan-id` | TEXT | Specific scan ID (optional) |
| `--rule` | TEXT | Filter by rule name (partial match) |
| `--severity` | CHOICE | Filter by severity level |
| `--output` | CHOICE | Output format: `table`, `json`, `yaml` |
| `--save` | TEXT | Save output to file |
| `--visual` | FLAG | Enable enhanced visuals with charts |
| `--color-scheme` | CHOICE | Color scheme: `default`, `monochrome`, `dark`, `security` |

---

### **`auditor trends`** - Basic Trends

Display vulnerability trends with export options.

#### **Options**
| Option | Type | Description |
|--------|------|-------------|
| `--days` | INTEGER | Number of days for trends (default: 30) |
| `--output` | CHOICE | Output format: `ascii`, `table`, `csv`, `json` |
| `--width` | INTEGER | Chart width for ASCII output (default: 40) |
| `--visual` | FLAG | Enable enhanced ASCII visualizations |

---

### **`auditor repos`** - Repository Statistics

Show repository statistics with filtering.

#### **Options**
| Option | Type | Description |
|--------|------|-------------|
| `--limit` | INTEGER | Number of repositories to show (default: 20) |
| `--min-score` | FLOAT | Minimum security score filter |
| `--language` | CHOICE | Filter by programming language |
| `--since` | TEXT | Show repos since date (YYYY-MM-DD) |

---

### **`auditor history`** - Scan History

Show scan history with advanced filtering.

#### **Options**
| Option | Type | Description |
|--------|------|-------------|
| `--limit` | INTEGER | Number of scans to show (default: 20) |
| `--since` | TEXT | Show scans since date (YYYY-MM-DD) |
| `--until` | TEXT | Show scans until date (YYYY-MM-DD) |
| `--min-score` | FLOAT | Minimum security score filter |
| `--max-score` | FLOAT | Maximum security score filter |
| `--repo` | TEXT | Filter by repository URL (partial match) |
| `--scan-type` | CHOICE | Filter by scan type |

---

## 🎨 **Visual and Configuration Commands**

### **`auditor visual-test`** - Visual Capabilities Test

Test terminal visual capabilities and display sample charts.

#### **Options**
| Option | Type | Description |
|--------|------|-------------|
| `--test-colors` | FLAG | Test color support and display color palette |
| `--test-charts` | FLAG | Display sample charts and visualizations |
| `--color-scheme` | CHOICE | Color scheme to test: `default`, `monochrome`, `dark`, `security` |

---

### **`auditor config`** - Configuration Management

Manage CLI configuration settings.

#### **Options**
| Option | Type | Description |
|--------|------|-------------|
| `--format` | CHOICE | Configuration format: `yaml`, `json` (default: yaml) |
| `--reset` | FLAG | Reset configuration to defaults |

---

## 💡 **Usage Tips**

### **Pattern Matching**
- Use glob patterns for `--include` and `--exclude`
- Patterns are case-sensitive
- Use multiple flags for multiple patterns: `--exclude "*.test.js" --exclude "*/node_modules/*"`

### **Time Ranges**
- **1h** = Last hour
- **24h** = Last 24 hours  
- **7d** = Last 7 days
- **30d** = Last 30 days
- **90d** = Last quarter
- **365d** = Last year

### **Severity Levels**
- **critical** = Critical security issues requiring immediate attention
- **high** = High severity issues that should be fixed soon
- **medium** = Medium severity issues for review
- **low** = Low severity issues and warnings

### **Output Formats**
- **table** = Rich formatted table for terminal viewing
- **json** = Structured JSON for programmatic integration
- **csv** = Comma-separated values for spreadsheet analysis
- **github** = GitHub Actions markdown for PR comments
- **sarif** = Static Analysis Results Interchange Format
- **markdown** = Formatted markdown for documentation

---

## 🚨 **Common Issues & Solutions**

### **CLI Argument Parsing Errors**

**❌ Incorrect:**
```bash
auditor scan --exclude "*/tests/*" "*/node_modules/*"
```

**✅ Correct:**
```bash
auditor scan --exclude "*/tests/*" --exclude "*/node_modules/*"
```

### **Model Not Found Errors**
- Check available models with: `auditor models`
- Use exact model names from the list
- Ensure OpenRouter API key is set

### **Permission Denied Errors**
- Check file permissions: `chmod +x auditor/cli.py`
- Ensure write permissions for output files
- Use `sudo` if needed for system directories

---

## 🔗 **Integration Examples**

### **Pre-commit Hook**
```bash
#!/bin/bash
# .git/hooks/pre-commit
auditor scan . --severity-filter high --fail-on-high
```

### **CI/CD Integration**
```yaml
# .github/workflows/security.yml
- name: Security Scan
  run: |
    auditor scan . \
      --output-format github \
      --save security-report.md \
      --fail-on-high
```

### **Cron Job for Reports**
```bash
# Weekly security report
0 9 * * 1 auditor generate-report --report-type security_summary --time-range 7d --save /reports/weekly-$(date +%Y-%m-%d).md
```