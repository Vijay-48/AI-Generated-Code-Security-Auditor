#!/bin/bash
# AI Code Security Auditor - Example Session Demo
# This script demonstrates the key capabilities of the auditor

set -e

echo "🛡️  AI Code Security Auditor - Production Demo"
echo "=============================================="
echo "Version: 2.0.0 | Phase 9: Advanced Analytics"
echo ""

# Check if auditor is installed
if ! command -v auditor &> /dev/null; then
    echo "❌ Auditor not found. Installing..."
    pip install ai-code-security-auditor
fi

# Check API key
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "⚠️  OPENROUTER_API_KEY not set. Some features will be limited."
    echo "   Get your free key at: https://openrouter.ai/"
    echo ""
fi

echo "🔍 1. BASIC SECURITY SCANNING"
echo "------------------------------"
echo "Scanning current directory for vulnerabilities..."
auditor scan . --output-format table --limit 5

echo ""
echo "📊 2. ADVANCED ANALYTICS - PHASE 9 FEATURES"
echo "--------------------------------------------"

echo "📈 Vulnerability Trends Analysis (last 30 days):"
auditor trends-detailed --period 30 --granularity daily

echo ""
echo "🔝 Top Security Rules Analysis:"
auditor top-rules --limit 5 --output table

echo ""
echo "⚡ Performance Analysis:"
auditor performance --include-models

echo ""
echo "📄 3. REPORT GENERATION"
echo "----------------------"
echo "Generating comprehensive security summary..."
auditor generate-report \
  --report-type security_summary \
  --time-range 7d \
  --format markdown \
  --save ./demo-security-report.md

if [ -f "./demo-security-report.md" ]; then
    echo "✅ Report generated: ./demo-security-report.md"
    echo "Preview:"
    head -n 15 ./demo-security-report.md
else
    echo "⚠️  Report generation failed"
fi

echo ""
echo "🤖 4. AI MODEL INFORMATION"
echo "-------------------------"
echo "Available AI models for analysis:"
auditor models

echo ""
echo "🔍 5. DIRECT CODE ANALYSIS"
echo "-------------------------"
echo "Analyzing sample vulnerable code..."
auditor analyze \
  --code "import os; password='secret123'; os.system(f'echo {user_input}')" \
  --language python

echo ""
echo "🚀 6. GITHUB ACTIONS FORMAT"
echo "---------------------------"
echo "Generating GitHub Actions compatible report..."
auditor scan . \
  --output-format github \
  --save ./demo-github-report.md \
  --severity-filter medium

if [ -f "./demo-github-report.md" ]; then
    echo "✅ GitHub Actions report: ./demo-github-report.md"
fi

echo ""
echo "📊 7. JSON EXPORT FOR INTEGRATIONS"
echo "----------------------------------"
auditor scan . --output-format json --save ./demo-scan-results.json
if [ -f "./demo-scan-results.json" ]; then
    echo "✅ JSON results: ./demo-scan-results.json"
    echo "File size: $(du -h ./demo-scan-results.json | cut -f1)"
fi

echo ""
echo "🎯 DEMO COMPLETED SUCCESSFULLY!"
echo "==============================="
echo "Files generated:"
ls -la ./demo-*.md ./demo-*.json 2>/dev/null || echo "No demo files found"

echo ""
echo "🚀 Next Steps:"
echo "• Visit http://localhost:8001/docs for API documentation"
echo "• Run 'auditor --help' for more CLI options"
echo "• Check out the complete README.md for advanced usage"
echo "• Start the API server with: uvicorn app.main:app --port 8001"

echo ""
echo "🛡️  Thank you for trying AI Code Security Auditor v2.0!"
echo "⭐ Star us on GitHub if this tool helps secure your code!"