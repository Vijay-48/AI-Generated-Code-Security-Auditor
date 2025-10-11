"""
Diagnostic script to identify scanning issues
"""
import sys
import asyncio
import platform

print("=" * 60)
print("🔍 Diagnostic Tool - Scanning Issue")
print("=" * 60)
print()

# Check Python version
print(f"Python Version: {sys.version}")
print(f"Platform: {platform.system()} {platform.release()}")
print()

# Check event loop policy on Windows
if platform.system() == "Windows":
    print("⚠️  Windows detected - checking event loop policy...")
    policy = asyncio.get_event_loop_policy()
    print(f"Current policy: {type(policy).__name__}")
    print()

# Test async functionality
print("Testing async functionality...")
try:
    async def test_async():
        return "Async works!"
    
    result = asyncio.run(test_async())
    print(f"✅ {result}")
except Exception as e:
    print(f"❌ Async test failed: {e}")
print()

# Check required modules
print("Checking required modules...")
required_modules = [
    'click',
    'httpx',
    'openai',
    'bandit',
    'semgrep',
    'langgraph',
    'langchain',
    'chromadb'
]

missing = []
for module in required_modules:
    try:
        __import__(module)
        print(f"✅ {module}")
    except ImportError:
        print(f"❌ {module} - MISSING")
        missing.append(module)

if missing:
    print()
    print(f"⚠️  Missing modules: {', '.join(missing)}")
    print(f"Run: pip install {' '.join(missing)}")
else:
    print()
    print("✅ All required modules installed")

print()
print("=" * 60)
print("Diagnostic complete")
print("=" * 60)
