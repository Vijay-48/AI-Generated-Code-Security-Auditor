#!/usr/bin/env python3
"""
Debug script to test the FastAPI agent initialization
"""
import asyncio
import sys
import os
sys.path.append('/app')

# Import exactly as in main.py
from app.agents.security_agent import SecurityAgent

async def test_fastapi_agent():
    # Initialize agent exactly as in main.py
    agent = SecurityAgent()
    
    vulnerable_code = '''import os
import subprocess

def insecure_function(user_input):
    # SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    
    # Command injection vulnerability  
    os.system(f"echo {user_input}")
    
    # Another command injection
    subprocess.call(f"ls {user_input}", shell=True)
    
    return query'''
    
    print("Testing FastAPI-style agent initialization...")
    try:
        # Call exactly as in the FastAPI endpoint
        state = await agent.run(
            code=vulnerable_code,
            language="python",
            filename="test.py",
            preferred_model=None,
            use_advanced_analysis=False
        )
        
        print(f"Scan results summary: {state.get('scan_results', {}).get('summary', {})}")
        print(f"Number of vulnerabilities found: {len(state.get('vulnerabilities', []))}")
        
        if state.get('vulnerabilities'):
            print("Vulnerabilities found:")
            for vuln in state.get('vulnerabilities', []):
                print(f"- {vuln.get('id')}: {vuln.get('title')} (Severity: {vuln.get('severity')})")
        else:
            print("No vulnerabilities found - this is the issue!")
            
    except Exception as e:
        print(f"Error during agent execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fastapi_agent())