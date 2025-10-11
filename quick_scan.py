#!/usr/bin/env python3
"""
Quick Scan Script - Simplified for Windows compatibility
Direct scanning without complex CLI framework
"""

import sys
import asyncio
import platform
from pathlib import Path

# Fix for Windows async issues
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.scanner import SecurityScanner

async def quick_scan(file_path: str):
    """Quick scan of a file"""
    print(f"🔍 Scanning: {file_path}")
    print()
    
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        
        # Determine language
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
        
        # Scan
        scanner = SecurityScanner()
        results = await scanner.scan_code(code, language, file_path)
        
        # Display results
        vulnerabilities = results.get('vulnerabilities', [])
        
        if not vulnerabilities:
            print("✅ No vulnerabilities found!")
            return
        
        print(f"🚨 Found {len(vulnerabilities)} vulnerabilities:\n")
        print("=" * 80)
        
        for i, vuln in enumerate(vulnerabilities, 1):
            severity_emoji = {
                'CRITICAL': '🔴',
                'HIGH': '🟠',
                'MEDIUM': '🟡',
                'LOW': '🟢'
            }.get(vuln.get('severity', 'LOW'), '🔵')
            
            print(f"\n{severity_emoji} {i}. {vuln.get('title', 'Unknown Issue')}")
            print(f"   ID: {vuln.get('id', 'N/A')}")
            print(f"   Severity: {vuln.get('severity', 'Unknown')}")
            print(f"   Line: {vuln.get('line_number', 'N/A')}")
            print(f"   Description: {vuln.get('description', 'No description')}")
        
        print("\n" + "=" * 80)
        print(f"\n📊 Total: {len(vulnerabilities)} vulnerabilities")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_scan.py <file_path>")
        print("\nExample:")
        print("  python quick_scan.py test_vulnerable.py")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    # Run scan
    asyncio.run(quick_scan(file_path))

if __name__ == '__main__':
    main()
