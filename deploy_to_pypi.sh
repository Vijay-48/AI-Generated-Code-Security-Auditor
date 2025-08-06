#!/bin/bash
# Deploy AI Code Security Auditor to Production PyPI
# Step 2 of the 30-minute deployment plan

set -e

echo "🚀 Deploying AI Code Security Auditor to Production PyPI..."
echo "======================================================="

# Check if API token is set
if [ -z "$PYPI_API_TOKEN" ]; then
    echo "❌ Error: PYPI_API_TOKEN environment variable not set"
    echo "Please set your production PyPI API token:"
    echo "export PYPI_API_TOKEN=pypi-YOUR_PYPI_TOKEN_HERE"
    exit 1
fi

# Validate package first
echo "🔍 Validating package..."
twine check dist/*

# Set authentication
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=$PYPI_API_TOKEN

# Confirm deployment
echo "⚠️  You are about to deploy to PRODUCTION PyPI."
echo "This action cannot be undone."
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 1
fi

# Upload to production PyPI
echo "📦 Uploading to production PyPI..."
twine upload dist/*

echo ""
echo "🎉 SUCCESS! Package is now LIVE on PyPI"
echo ""
echo "🌍 Global Installation:"
echo "   pip install ai-code-security-auditor"
echo ""
echo "📊 View your package: https://pypi.org/project/ai-code-security-auditor/"
echo ""
echo "📋 Next Steps:"
echo "1. Test global installation:"
echo "   pip install ai-code-security-auditor"
echo "   auditor --help"
echo ""
echo "2. Create GitHub release:"
echo "   git tag -a v2.0.0 -m \"Initial PIP package release\""
echo "   git push origin v2.0.0"
echo ""
echo "3. Monitor downloads and feedback"