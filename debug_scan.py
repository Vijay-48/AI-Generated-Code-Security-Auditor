#!/usr/bin/env python3
"""
Debug scan to find where the hang occurs
"""

import sys
import asyncio
import platform
from pathlib import Path

# Windows fix
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

sys.path.insert(0, str(Path(__file__).parent.absolute()))

from app.agents.security_agent import SecurityAgent
from app.config import settings

def debug_scan(file_path: str):
    """Debug scan with verbose output"""
    print(f"🔍 Debug Scan Starting...")
    print(f"Platform: {platform.system()}")
    print(f"Python: {sys.version}")
    print(f"File: {file_path}")
    print()
    
    try:
        # Step 1: Read file
        print("Step 1: Reading file...")
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        print(f"✅ File read successfully ({len(code)} chars)")
        print()
        
        # Step 2: Determine language
        print("Step 2: Determining language...")
        ext = Path(file_path).suffix
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'javascript',
            '.tsx': 'javascript',
            '.java': 'java',
            '.go': 'go'
        }
        language = language_map.get(ext, 'python')
        print(f"✅ Language: {language}")
        print()
        
        # Step 3: Initialize agent
        print("Step 3: Initializing SecurityAgent...")
        print("⏳ This may take 10-30 seconds on first run (downloading ML models)...")
        print("   Be patient, this is normal!")
        print()
        
        agent = SecurityAgent()
        print(f"✅ Agent initialized successfully")
        print()
        
        # Step 4: Check API keys
        print("Step 4: Checking API keys...")
        if settings.GROQ_API_KEY:
            print(f"✅ GROQ_API_KEY configured")
        if settings.OPENROUTER_API_KEY:
            print(f"✅ OPENROUTER_API_KEY configured")
        if not settings.GROQ_API_KEY and not settings.OPENROUTER_API_KEY:
            print(f"❌ No API keys configured!")
            return
        print()
        
        # Step 5: Run scan (this is where it might hang)
        print("Step 5: Running async scan...")
        print("⏳ Calling asyncio.run(agent.run(...))...")
        print("   (This may take 10-30 seconds for the first API call)")
        print()
        
        async def run_with_timeout():
            try:
                result = await asyncio.wait_for(
                    agent.run(
                        code=code,
                        language=language,
                        filename=Path(file_path).name,
                        preferred_model=settings.MODEL_CODE_GENERATION,
                        use_advanced_analysis=False
                    ),
                    timeout=60.0  # 60 second timeout
                )
                return result
            except asyncio.TimeoutError:
                return {"error": "Timeout after 60 seconds", "vulnerabilities": []}
        
        result = asyncio.run(run_with_timeout())
        
        print("✅ Scan completed!")
        print()
        
        # Step 6: Display results
        print("Step 6: Processing results...")
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            vulnerabilities = result.get('vulnerabilities', [])
            print(f"✅ Found {len(vulnerabilities)} vulnerabilities")
            
            for i, vuln in enumerate(vulnerabilities[:3], 1):
                print(f"\n  {i}. {vuln.get('title', 'Unknown')}")
                print(f"     Severity: {vuln.get('severity', 'Unknown')}")
                print(f"     Line: {vuln.get('line_number', 'N/A')}")
        
        print()
        print("🎉 Debug scan completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Scan interrupted by user (Ctrl+C)")
        print("💡 The scan was taking too long - likely an API timeout issue")
    except Exception as e:
        print(f"\n❌ Error occurred: {type(e).__name__}: {e}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python debug_scan.py <file_path>")
        print("\nExample:")
        print("  python debug_scan.py tests/test_vulnerable.py")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    debug_scan(file_path)
