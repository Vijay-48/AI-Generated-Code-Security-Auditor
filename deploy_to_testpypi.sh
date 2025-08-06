#!/bin/bash
# Deploy AI Code Security Auditor to TestPyPI
# Step 1 of the 30-minute deployment plan

set -e

echo "🚀 Deploying AI Code Security Auditor to TestPyPI..."
echo "==============================================="

# Check if API token is set
if [ -z "$TESTPYPI_API_TOKEN" ]; then
    echo "❌ Error: TESTPYPI_API_TOKEN environment variable not set"
    echo "Please set your TestPyPI API token:"
    echo "export TESTPYPI_API_TOKEN=pypi-YOUR_TESTPYPI_TOKEN_HERE"
    exit 1
fi

# Validate package first
echo "🔍 Validating package..."
twine check dist/*

# Set authentication
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=$TESTPYPI_API_TOKEN

# Upload to TestPyPI
echo "📦 Uploading to TestPyPI..."
twine upload --repository testpypi dist/*

echo ""
echo "🎉 Success! Package uploaded to TestPyPI"
echo ""
echo "📋 Next Steps:"
echo "1. Test installation:"
echo "   python -m venv test_env"
echo "   source test_env/bin/activate"
echo "   pip install --index-url https://test.pypi.org/simple/ ai-code-security-auditor"
echo "   auditor --help"
echo ""
echo "2. If successful, deploy to production PyPI:"
echo "   ./deploy_to_pypi.sh"
echo ""
echo "📊 View your package: https://test.pypi.org/project/ai-code-security-auditor/"