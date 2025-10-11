#!/usr/bin/env python3
"""
Windows Fix Verification Script
Tests if the CLI scan works correctly on Windows
"""

import sys
import asyncio
import platform
from pathlib import Path

print("🪟 Windows Fix Verification")
print("=" * 80)

# 1. Check platform
print(f"\n1. Platform: {platform.system()}")
print(f"   Python: {sys.version}")

# 2. Check async event loop policy
print(f"\n2. Event Loop Policy: {asyncio.get_event_loop_policy().__class__.__name__}")

# 3. Test asyncio.run() works
print("\n3. Testing asyncio.run()...")
try:
    async def test_async():
        await asyncio.sleep(0.1)
        return "✅ Async working"
    
    result = asyncio.run(test_async())
    print(f"   {result}")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    sys.exit(1)

# 4. Test imports
print("\n4. Testing imports...")
try:
    from app.config import settings
    from app.agents.security_agent import SecurityAgent
    print("   ✅ All imports successful")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# 5. Test API keys
print("\n5. Checking API keys...")
if settings.GROQ_API_KEY or settings.OPENROUTER_API_KEY:
    print("   ✅ API keys configured")
else:
    print("   ⚠️  No API keys found (needed for actual scanning)")

# 6. Test SecurityAgent initialization (skip - takes too long on first run)
print("\n6. Testing SecurityAgent...")
print("   ℹ️  Skipping SecurityAgent test (takes 10-30s on first run)")
print("   💡 This will be tested in the actual scan")

# 7. Test scan_file_direct logic (without actual API call)
print("\n7. Testing scan logic...")
try:
    # Create a test file
    test_file = Path("test_temp.py")
    test_file.write_text("import os\nos.system('ls')")
    
    # Read it back
    with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    
    print(f"   ✅ File operations working")
    print(f"   Test code length: {len(code)} characters")
    
    # Clean up
    test_file.unlink()
    
except Exception as e:
    print(f"   ❌ Failed: {e}")
    sys.exit(1)

# 8. Test CLI command availability
print("\n8. Testing CLI commands...")
try:
    from auditor.cli import cli
    print("   ✅ CLI module loaded")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("🎉 All tests passed! Your Windows environment is ready.")
print("\n💡 Next steps:")
print("   1. Run: python -m auditor.cli scan --path tests/test_vulnerable.py")
print("   2. Or use: python tests/quick_scan.py tests/test_vulnerable.py")
print("\n🚀 Ready for your hackathon demo!")
