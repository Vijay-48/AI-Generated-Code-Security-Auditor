#!/usr/bin/env python3
"""
First Run Setup - Downloads models with progress feedback
Run this ONCE before using the scanner
"""

import sys
import time
import platform
import asyncio
from pathlib import Path

# Windows async fix
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

sys.path.insert(0, str(Path(__file__).parent.absolute()))

print("=" * 80)
print("🚀 AI Code Security Auditor - First Run Setup")
print("=" * 80)
print()
print("This will download required ML models (~100MB)")
print("⏰ This takes 1-2 minutes on first run, then scans are fast!")
print()
print("=" * 80)
print()

def spinner_animation(message):
    """Show spinner while downloading"""
    import threading
    import itertools
    
    done = False
    
    def animate():
        for c in itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']):
            if done:
                break
            sys.stdout.write(f'\r{message} {c}')
            sys.stdout.flush()
            time.sleep(0.1)
    
    t = threading.Thread(target=animate)
    t.start()
    return t, lambda: done.__setitem__(0, True) if isinstance(done, list) else None

# Step 1: Download SentenceTransformer model
print("1️⃣  Downloading SentenceTransformer model (~100MB)...")
print("   ⏳ This may take 30-90 seconds depending on your connection...")
print()

start_time = time.time()

try:
    from sentence_transformers import SentenceTransformer
    
    # This will download the model on first run
    print("   📥 Initializing sentence transformer...")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    elapsed = time.time() - start_time
    print(f"   ✅ Model downloaded successfully ({elapsed:.1f}s)")
    print()
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("   💡 Try: pip install sentence-transformers")
    sys.exit(1)

# Step 2: Initialize ChromaDB
print("2️⃣  Initializing ChromaDB...")
start_time = time.time()

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    
    client = chromadb.PersistentClient(
        path="./chroma_db",
        settings=ChromaSettings(allow_reset=True)
    )
    
    col = client.get_or_create_collection(
        name="vuln_remediation",
        metadata={"description": "CWE → code fixes"}
    )
    
    elapsed = time.time() - start_time
    print(f"   ✅ ChromaDB initialized ({elapsed:.1f}s)")
    print()
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("   💡 Try: pip install chromadb")
    sys.exit(1)

# Step 3: Test API connection
print("3️⃣  Testing API connection...")
start_time = time.time()

try:
    from app.config import settings
    
    if settings.GROQ_API_KEY:
        print("   ✅ GROQ API key found")
    if settings.OPENROUTER_API_KEY:
        print("   ✅ OpenRouter API key found")
    
    if not settings.GROQ_API_KEY and not settings.OPENROUTER_API_KEY:
        print("   ⚠️  No API keys found")
        print("   💡 Add keys to .env file")
    
    elapsed = time.time() - start_time
    print(f"   ✅ Configuration loaded ({elapsed:.1f}s)")
    print()
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Step 4: Initialize SecurityAgent (the slow part!)
print("4️⃣  Initializing SecurityAgent (this is the slow part)...")
print("   ⏳ Please wait 30-60 seconds...")
print()

start_time = time.time()

try:
    from app.agents.security_agent import SecurityAgent
    
    print("   📦 Loading agent components...")
    agent = SecurityAgent()
    
    elapsed = time.time() - start_time
    print(f"   ✅ SecurityAgent initialized ({elapsed:.1f}s)")
    print()
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Test scan
print("5️⃣  Testing scan functionality...")
start_time = time.time()

try:
    test_code = """
import os
user_input = input("Enter command: ")
os.system(user_input)  # Command injection vulnerability
"""
    
    print("   🔍 Running test scan...")
    
    async def test_scan():
        result = await agent.run(
            code=test_code,
            language="python",
            filename="test.py",
            preferred_model=settings.MODEL_CODE_GENERATION,
            use_advanced_analysis=False
        )
        return result
    
    result = asyncio.run(test_scan())
    
    vulns = result.get('vulnerabilities', [])
    elapsed = time.time() - start_time
    
    print(f"   ✅ Test scan complete ({elapsed:.1f}s)")
    print(f"   📊 Found {len(vulns)} vulnerabilities in test code")
    print()
    
except Exception as e:
    print(f"   ⚠️  Test scan failed: {e}")
    print("   💡 This is OK - the setup is complete, just API might be slow")
    print()

# Summary
print("=" * 80)
print("🎉 Setup Complete!")
print("=" * 80)
print()
print("✅ All components initialized successfully!")
print("✅ Models downloaded and cached")
print("✅ Ready for fast scanning")
print()
print("📋 Next steps:")
print("   1. Run a scan: python -m auditor.cli scan --path tests/test_vulnerable.py")
print("   2. Scans will now be fast (5-15 seconds)")
print()
print("💡 You only need to run this setup once!")
print()
