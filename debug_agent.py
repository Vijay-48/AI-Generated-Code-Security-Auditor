#!/usr/bin/env python3
"""
Debug script to test the security agent directly
"""
import asyncio
import sys
import os
sys.path.append('/app')

from app.agents.security_agent import SecurityAgent

async def test_agent():
    agent = SecurityAgent()
    
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
    
    print("Testing security agent with vulnerable Python code...")
    try:
        state = await agent.run(
            code=vulnerable_code,
            language="python",
            filename="test.py"
        )
        
        print(f"Scan results: {state.get('scan_results', {})}")
        print(f"Number of vulnerabilities found: {len(state.get('vulnerabilities', []))}")
        
        for vuln in state.get('vulnerabilities', []):
            print(f"- {vuln.get('id')}: {vuln.get('title')} (Severity: {vuln.get('severity')})")
            
    except Exception as e:
        print(f"Error during agent execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent())