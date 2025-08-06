#!/bin/bash
# Test installation from TestPyPI or PyPI
# Part of the deployment verification process

set -e

echo "🧪 Testing AI Code Security Auditor Installation..."
echo "================================================="

# Parse command line argument for source
SOURCE=${1:-testpypi}

if [ "$SOURCE" = "testpypi" ]; then
    INDEX_URL="--index-url https://test.pypi.org/simple/"
    REPO_NAME="TestPyPI"
else
    INDEX_URL=""
    REPO_NAME="PyPI"
fi

echo "📦 Testing installation from $REPO_NAME"

# Create clean test environment
echo "🔧 Creating clean test environment..."
rm -rf test_install_env
python -m venv test_install_env
source test_install_env/bin/activate

echo "📥 Installing package..."
pip install $INDEX_URL ai-code-security-auditor

echo "✅ Testing CLI functionality..."

# Test CLI help
echo "  Testing: auditor --help"
auditor --help > /dev/null

# Test models command
echo "  Testing: auditor models --help"  
auditor models --help > /dev/null

# Test scan command
echo "  Testing: auditor scan --help"
auditor scan --help > /dev/null

# Test analyze command
echo "  Testing: auditor analyze --help"
auditor analyze --help > /dev/null

# Test Python import
echo "  Testing: Python imports"
python -c "from app.main import app; print('✅ FastAPI app imports successfully')"

# Cleanup
deactivate
rm -rf test_install_env

echo ""
echo "🎉 All tests passed! Installation from $REPO_NAME works correctly."
echo ""
echo "✅ Verified functionality:"
echo "  - CLI tool accessible"  
echo "  - All major commands available"
echo "  - Python library imports work"
echo "  - Clean installation/uninstallation"