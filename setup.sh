#!/bin/bash

echo "🛡️  AI Code Security Auditor - Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "📌 Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✅ Python $python_version detected"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
echo "This may take a few minutes..."
echo ""

pip install -q --upgrade pip

# Core dependencies
echo "  → Installing core dependencies..."
pip install -q click rich colorama tqdm

# AI/LLM dependencies
echo "  → Installing AI/LLM libraries..."
pip install -q httpx openai pydantic pydantic-settings python-dotenv

# LangChain and LangGraph
echo "  → Installing LangChain and LangGraph..."
pip install -q langgraph langchain langchain-core

# Vector database
echo "  → Installing ChromaDB and embeddings..."
pip install -q chromadb sentence-transformers

# Security scanners
echo "  → Installing security scanners..."
pip install -q bandit semgrep

# FastAPI (optional, for API server)
echo "  → Installing FastAPI (optional)..."
pip install -q fastapi uvicorn

echo ""
echo "✅ All dependencies installed!"
echo ""

# Check API keys
echo "🔑 Checking API keys..."
if [ -f .env ]; then
    if grep -q "GROQ_API_KEY=gsk_" .env; then
        echo "  ✅ GroqCloud API key found"
    else
        echo "  ⚠️  GroqCloud API key not configured"
    fi
    
    if grep -q "OPENROUTER_API_KEY=sk-or-" .env; then
        echo "  ✅ OpenRouter API key found"
    else
        echo "  ⚠️  OpenRouter API key not configured"
    fi
else
    echo "  ❌ .env file not found!"
    echo "  Please create .env file with your API keys"
fi
echo ""

# Test installation
echo "🧪 Testing installation..."
python -m auditor.cli --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ CLI is working!"
else
    echo "❌ CLI test failed. Please check for errors above."
    exit 1
fi
echo ""

# Test with models command
echo "🤖 Testing model configuration..."
python -m auditor.cli models > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Model configuration is working!"
else
    echo "⚠️  Model command had issues. Check API keys."
fi
echo ""

# Success message
echo "=========================================="
echo "🎉 Setup Complete!"
echo "=========================================="
echo ""
echo "Quick Start:"
echo "  1. View available models:"
echo "     python -m auditor.cli models"
echo ""
echo "  2. Test with sample file:"
echo "     python -m auditor.cli scan --path test_vulnerable.py"
echo ""
echo "  3. Scan your code:"
echo "     python -m auditor.cli scan --path /path/to/your/code"
echo ""
echo "  4. Get help:"
echo "     python -m auditor.cli --help"
echo ""
echo "📚 Read QUICKSTART.md for more examples!"
echo ""
