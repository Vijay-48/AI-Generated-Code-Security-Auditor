#!/usr/bin/env python3
"""
AI Code Security Auditor - Hackathon Setup Script
Quick setup and verification for hackathon use
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print welcome banner"""
    print("""
🛡️ AI CODE SECURITY AUDITOR v2.0.0
=====================================
Hackathon-ready AI security scanner

📖 Quick Setup Guide:
1. Install dependencies: pip install -r requirements.txt
2. Set API key in .env file
3. Test: python -m auditor.cli test
4. Start scanning: python -m auditor.cli scan --path myfile.py
    """)

def check_python_version():
    """Check if Python version is supported"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8+ required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'fastapi', 'click', 'requests', 'openai', 'httpx', 
        'pydantic', 'bandit', 'rich', 'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed")
    return True

def check_env_file():
    """Check if .env file exists and has API keys"""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists():
        if env_example.exists():
            print("❌ .env file not found")
            print("💡 Run: cp .env.example .env")
            print("   Then edit .env and add your API keys")
        else:
            print("❌ Neither .env nor .env.example found")
            create_basic_env()
        return False
    
    # Check if API keys are set
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        openrouter_key = os.getenv('OPENROUTER_API_KEY', '').strip()
        openai_key = os.getenv('OPENAI_API_KEY', '').strip()
        
        if not openrouter_key and not openai_key:
            print("❌ No API keys found in .env")
            print("💡 Add to .env file:")
            print("   OPENROUTER_API_KEY=your_key_here")
            print("   or")
            print("   OPENAI_API_KEY=sk-your_key_here")
            return False
        
        if openrouter_key:
            print("✅ OpenRouter API key found")
        if openai_key:
            print("✅ OpenAI API key found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking .env file: {e}")
        return False

def create_basic_env():
    """Create a basic .env file template"""
    env_content = """# AI Code Security Auditor Configuration
# Get API keys from:
# - OpenRouter: https://openrouter.ai/
# - OpenAI: https://platform.openai.com/api-keys

# Choose at least one:
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Default model (optional)
DEFAULT_MODEL=openai/gpt-4

# API Configuration (optional)
API_HOST=0.0.0.0
API_PORT=8000
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env template file")
        print("💡 Edit .env and add your API keys")
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

def test_cli():
    """Test if CLI is working"""
    try:
        result = subprocess.run([
            sys.executable, '-m', 'auditor.cli', '--help'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ CLI working correctly")
            return True
        else:
            print("❌ CLI test failed")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ CLI test timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing CLI: {e}")
        return False

def show_quick_start():
    """Show quick start commands"""
    print("""
🚀 QUICK START COMMANDS:
========================

# Test installation:
python -m auditor.cli test

# Scan a file:
echo 'import os; os.system(user_input)' > test.py
python -m auditor.cli scan --path test.py
rm test.py

# Analyze code directly:
python -m auditor.cli analyze --code "exec(user_input)" --language python

# List available models:
python -m auditor.cli models

# Start API server (optional):
uvicorn app.main:app --reload
# Then visit: http://localhost:8000/docs

📖 Full documentation in README.md
🐛 Issues? Check troubleshooting section in README.md
    """)

def main():
    """Main setup function"""
    print_banner()
    
    all_good = True
    
    # Check Python version
    if not check_python_version():
        all_good = False
    
    # Check dependencies
    if not check_dependencies():
        all_good = False
    
    # Check environment file
    if not check_env_file():
        all_good = False
    
    # Test CLI (only if everything else is OK)
    if all_good:
        if not test_cli():
            all_good = False
    
    print("\n" + "="*50)
    
    if all_good:
        print("🎉 SETUP COMPLETE! Ready for hackathon!")
        show_quick_start()
    else:
        print("❌ Setup incomplete. Please fix the issues above.")
        print("\n💡 Common solutions:")
        print("   • pip install -r requirements.txt")
        print("   • cp .env.example .env (then edit .env)")
        print("   • python -m auditor.cli --help")
    
    return 0 if all_good else 1

if __name__ == '__main__':
    sys.exit(main())