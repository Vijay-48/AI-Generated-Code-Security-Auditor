#!/usr/bin/env python3
"""
Debug script to test the scanner directly
"""
import asyncio
import sys
import os
sys.path.append('/app')

from app.services.scanner import SecurityScanner

async def test_scanner():
    scanner = SecurityScanner()
    
    vulnerable_code = '''
import os
import subprocess

def insecure_function(user_input):
    # SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    
    # Command injection vulnerability  
    os.system(f"echo {user_input}")
    
    # Another command injection
    subprocess.call(f"ls {user_input}", shell=True)
    
    return query
'''
    
    print("Testing scanner with vulnerable Python code...")
    try:
        results = await scanner.scan_code(vulnerable_code, "python", "test.py")
        print(f"Scan results: {results}")
        print(f"Number of vulnerabilities found: {len(results.get('vulnerabilities', []))}")
        
        for vuln in results.get('vulnerabilities', []):
            print(f"- {vuln.get('id')}: {vuln.get('title')} (Severity: {vuln.get('severity')})")
            
    except Exception as e:
        print(f"Error during scanning: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_scanner())