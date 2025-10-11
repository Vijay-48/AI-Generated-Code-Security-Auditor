#!/bin/bash

echo "🚀 AI Code Security Auditor - Final Feature Test"
echo "=================================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0

# Test function
test_command() {
    echo -n "Testing: $1... "
    eval "$2" > /tmp/test_output.txt 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASS++))
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((FAIL++))
        echo "  Error: $(cat /tmp/test_output.txt | head -3)"
    fi
}

echo "📋 Feature Tests"
echo "=================="
echo ""

# Test 1: CLI Help
test_command "CLI Help" "python -m auditor.cli --help"

# Test 2: Models Command
test_command "Models Command" "python -m auditor.cli models"

# Test 3: Scan Command
test_command "Scan Single File" "timeout 60 python -m auditor.cli scan --path test_vulnerable.py"

# Test 4: Analyze Command  
test_command "Analyze Code Snippet" "timeout 30 python -m auditor.cli analyze --code 'os.system(user_input)' --language python"

# Test 5: JSON Output
test_command "JSON Output Format" "timeout 60 python -m auditor.cli scan --path test_vulnerable.py --output-format json --output-file /tmp/test_results.json"

# Test 6: GitHub Format
test_command "GitHub Output Format" "timeout 60 python -m auditor.cli scan --path test_vulnerable.py --output-format github --output-file /tmp/test_github.md"

# Test 7: SARIF Format
test_command "SARIF Output Format" "timeout 60 python -m auditor.cli scan --path test_vulnerable.py --output-format sarif --output-file /tmp/test_sarif.json"

# Test 8: Directory Scan
test_command "Directory Scan" "timeout 90 python -m auditor.cli scan --path /app/auditor"

# Test 9: Severity Filter
test_command "Severity Filter" "timeout 60 python -m auditor.cli scan --path test_vulnerable.py --severity-filter high"

# Test 10: Specific Model
test_command "Specific Model (Groq)" "timeout 60 python -m auditor.cli scan --path test_vulnerable.py --model llama-3.1-8b-instant"

echo ""
echo "=================================================="
echo "📊 Test Summary"
echo "=================================================="
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo ""

# Check generated files
echo "📁 Generated Files Check"
echo "========================"
if [ -f /tmp/test_results.json ]; then
    echo "✅ JSON report generated"
    file_size=$(wc -c < /tmp/test_results.json)
    echo "   Size: ${file_size} bytes"
else
    echo "❌ JSON report not found"
fi

if [ -f /tmp/test_github.md ]; then
    echo "✅ GitHub report generated"
    file_size=$(wc -c < /tmp/test_github.md)
    echo "   Size: ${file_size} bytes"
else
    echo "❌ GitHub report not found"
fi

if [ -f /tmp/test_sarif.json ]; then
    echo "✅ SARIF report generated"
    file_size=$(wc -c < /tmp/test_sarif.json)
    echo "   Size: ${file_size} bytes"
else
    echo "❌ SARIF report not found"
fi

echo ""

# Final verdict
if [ $FAIL -eq 0 ]; then
    echo "=================================================="
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo "=================================================="
    echo ""
    echo "✅ Your AI Code Security Auditor is ready for the hackathon!"
    echo ""
    echo "Quick commands:"
    echo "  python -m auditor.cli models"
    echo "  python -m auditor.cli scan --path <your_file>"
    echo "  python -m auditor.cli analyze --code '<code>' --language python"
    echo ""
    exit 0
else
    echo "=================================================="
    echo -e "${YELLOW}⚠️  SOME TESTS FAILED${NC}"
    echo "=================================================="
    echo ""
    echo "Failed tests: $FAIL"
    echo "This might be due to timeouts or AI model calls."
    echo "Core functionality is working if basic tests passed."
    echo ""
    exit 1
fi
