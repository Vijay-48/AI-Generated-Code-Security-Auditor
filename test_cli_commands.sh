#!/bin/bash

echo "=========================================="
echo "🧪 Testing AI Code Security Auditor CLI"
echo "=========================================="
echo ""

# Test 1: Basic scan
echo "📝 Test 1: Basic scan"
python -m auditor.cli scan --path test_vulnerable.py 2>&1 | grep -q "Scan complete"
if [ $? -eq 0 ]; then
    echo "✅ PASS: Basic scan works"
else
    echo "❌ FAIL: Basic scan failed"
fi
echo ""

# Test 2: JSON output
echo "📝 Test 2: JSON output"
python -m auditor.cli scan --path test_vulnerable.py --output-format json --output-file /tmp/test_output.json 2>&1 | grep -q "Scan complete"
if [ $? -eq 0 ] && [ -f /tmp/test_output.json ]; then
    echo "✅ PASS: JSON output works"
else
    echo "❌ FAIL: JSON output failed"
fi
echo ""

# Test 3: Fix generation
echo "📝 Test 3: Fix generation"
python -m auditor.cli fix --path test_vulnerable.py --output-file /tmp/test_fixes.md 2>&1 | grep -q "Summary"
if [ $? -eq 0 ] && [ -f /tmp/test_fixes.md ]; then
    echo "✅ PASS: Fix generation works"
else
    echo "❌ FAIL: Fix generation failed"
fi
echo ""

# Test 4: Code analysis
echo "📝 Test 4: Code analysis"
python -m auditor.cli analyze --code "os.system(user_input)" --language python 2>&1 | grep -q "Analysis Results"
if [ $? -eq 0 ]; then
    echo "✅ PASS: Code analysis works"
else
    echo "❌ FAIL: Code analysis failed"
fi
echo ""

# Test 5: Models list
echo "📝 Test 5: Models list"
python -m auditor.cli models 2>&1 | grep -q "Available AI Models"
if [ $? -eq 0 ]; then
    echo "✅ PASS: Models list works"
else
    echo "❌ FAIL: Models list failed"
fi
echo ""

# Test 6: Advanced scan
echo "📝 Test 6: Advanced scan"
python -m auditor.cli scan --path test_vulnerable.py --advanced 2>&1 | grep -q "Scan complete"
if [ $? -eq 0 ]; then
    echo "✅ PASS: Advanced scan works"
else
    echo "❌ FAIL: Advanced scan failed"
fi
echo ""

echo "=========================================="
echo "🎉 All tests completed!"
echo "=========================================="
