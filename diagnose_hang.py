#!/usr/bin/env python3
"""
Diagnose Why Scan is Hanging
"""

import sys
import time
import platform
from pathlib import Path

print("=" * 80)
print("🔍 Diagnosing Scan Hang Issue")
print("=" * 80)
print()

# Test 1: Check Python and Platform
print("1️⃣  System Information:")
print(f"   Platform: {platform.system()}")
print(f"   Python: {sys.version}")
print()

# Test 2: Check imports
print("2️⃣  Testing imports...")
try:
    import asyncio
    import chromadb
    from sentence_transformers import SentenceTransformer
    print("   ✅ All packages installed")
except ImportError as e:
    print(f"   ❌ Missing package: {e}")
    sys.exit(1)
print()

# Test 3: Check if models are already downloaded
print("3️⃣  Checking cached models...")

# Check SentenceTransformer cache
import os
from pathlib import Path

home = Path.home()
st_cache = home / ".cache" / "torch" / "sentence_transformers"

if st_cache.exists():
    model_dirs = list(st_cache.glob("*"))
    if model_dirs:
        print(f"   ✅ SentenceTransformer models cached: {len(model_dirs)} found")
        for model_dir in model_dirs[:3]:
            size_mb = sum(f.stat().st_size for f in model_dir.rglob('*') if f.is_file()) / 1024 / 1024
            print(f"      - {model_dir.name}: {size_mb:.1f}MB")
    else:
        print("   ⚠️  No models cached - will download on first run")
else:
    print("   ⚠️  No cache directory - models will download on first run")
print()

# Test 4: Check ChromaDB
print("4️⃣  Checking ChromaDB...")
chroma_path = Path("./chroma_db")
if chroma_path.exists():
    db_size = sum(f.stat().st_size for f in chroma_path.rglob('*') if f.is_file()) / 1024
    print(f"   ✅ ChromaDB exists: {db_size:.1f}KB")
else:
    print("   ⚠️  ChromaDB not initialized - will create on first run")
print()

# Test 5: Test SentenceTransformer loading (this is where it hangs!)
print("5️⃣  Testing SentenceTransformer loading...")
print("   ⏳ Loading model (this might take 30-90s on FIRST RUN)...")
print("   💡 If this hangs, press Ctrl+C and check your internet connection")
print()

start = time.time()
try:
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    elapsed = time.time() - start
    print(f"   ✅ Model loaded in {elapsed:.1f}s")
    
    if elapsed > 30:
        print("   ⚠️  Loading took >30s - this is normal on FIRST run")
        print("   ⚠️  Next time will be faster (~1-2s)")
    else:
        print("   ✅ Model was cached - loading was fast")
except Exception as e:
    print(f"   ❌ Failed to load model: {e}")
    print()
    print("   Possible causes:")
    print("   1. No internet connection")
    print("   2. Firewall blocking download")
    print("   3. Insufficient disk space")
    print("   4. Download interrupted")
    print()
    sys.exit(1)
print()

# Test 6: Test ChromaDB initialization
print("6️⃣  Testing ChromaDB initialization...")
start = time.time()
try:
    from chromadb.config import Settings as ChromaSettings
    
    client = chromadb.PersistentClient(
        path="./chroma_db",
        settings=ChromaSettings(allow_reset=True)
    )
    
    elapsed = time.time() - start
    print(f"   ✅ ChromaDB initialized in {elapsed:.1f}s")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    sys.exit(1)
print()

# Test 7: Test API keys
print("7️⃣  Checking API keys...")
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from app.config import settings
    
    has_groq = bool(settings.GROQ_API_KEY)
    has_openrouter = bool(settings.OPENROUTER_API_KEY)
    
    if has_groq:
        print("   ✅ GROQ API key configured")
    if has_openrouter:
        print("   ✅ OpenRouter API key configured")
    
    if not has_groq and not has_openrouter:
        print("   ❌ No API keys configured!")
        print("   💡 Add keys to .env file")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Failed: {e}")
    sys.exit(1)
print()

# Test 8: Test SecurityAgent initialization (THE CRITICAL TEST!)
print("8️⃣  Testing SecurityAgent initialization...")
print("   ⏳ This is where the CLI hangs - testing now...")
print("   💡 If this takes >2 minutes, there's a problem")
print()

start = time.time()
try:
    from app.agents.security_agent import SecurityAgent
    
    print("   📦 Creating SecurityAgent instance...")
    agent = SecurityAgent()
    
    elapsed = time.time() - start
    print(f"   ✅ SecurityAgent initialized in {elapsed:.1f}s")
    
    if elapsed > 60:
        print("   ⚠️  Initialization took >60s - this is slow")
        print("   ⚠️  Check your system resources and internet")
except KeyboardInterrupt:
    elapsed = time.time() - start
    print(f"\n   ⚠️  Interrupted after {elapsed:.1f}s")
    print("   💡 This is where the scan hangs!")
    print()
    print("   Possible causes:")
    print("   1. Model download in progress (wait 2 minutes)")
    print("   2. Network issue (check internet)")
    print("   3. Antivirus blocking (disable temporarily)")
    print("   4. Low disk space")
    print("   5. Firewall blocking Python")
    sys.exit(1)
except Exception as e:
    elapsed = time.time() - start
    print(f"   ❌ Failed after {elapsed:.1f}s: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
print()

# Test 9: Quick scan test
print("9️⃣  Testing actual scan...")
print("   🔍 Running a quick scan...")
print()

start = time.time()
try:
    import asyncio
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    test_code = 'os.system(user_input)'
    
    async def quick_test():
        result = await agent.run(
            code=test_code,
            language="python",
            filename="test.py",
            preferred_model=settings.MODEL_CODE_GENERATION,
            use_advanced_analysis=False
        )
        return result
    
    result = asyncio.run(quick_test())
    
    elapsed = time.time() - start
    vulns = result.get('vulnerabilities', [])
    
    print(f"   ✅ Scan completed in {elapsed:.1f}s")
    print(f"   📊 Found {len(vulns)} vulnerabilities")
except KeyboardInterrupt:
    elapsed = time.time() - start
    print(f"\n   ⚠️  Scan interrupted after {elapsed:.1f}s")
    print("   💡 Scan is taking too long - likely API timeout")
    print()
    print("   Check:")
    print("   1. Internet connection")
    print("   2. API key validity")
    print("   3. API rate limits")
except Exception as e:
    elapsed = time.time() - start
    print(f"   ❌ Scan failed after {elapsed:.1f}s: {e}")

print()
print("=" * 80)
print("🎯 Diagnosis Complete")
print("=" * 80)
print()
print("If all tests passed, the scanner is working!")
print("If any test failed or hung, that's the issue.")
print()
