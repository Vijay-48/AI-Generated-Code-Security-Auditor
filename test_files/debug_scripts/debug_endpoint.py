#!/usr/bin/env python3
"""
Debug script to test the exact FastAPI endpoint logic
"""
import asyncio
import sys
import os
sys.path.append('/app')

# Import exactly as in main.py
from app.agents.security_agent import SecurityAgent
from app.main import AuditRequest

async def test_endpoint_logic():
    # Initialize agent exactly as in main.py
    agent = SecurityAgent()
    
    # Create request exactly as FastAPI would
    request_data = {
        "code": "\nimport os\nimport subprocess\n\ndef insecure_function(user_input):\n    # SQL Injection vulnerability\n    query = f\"SELECT * FROM users WHERE name = '{user_input}'\"\n    \n    # Command injection vulnerability  \n    os.system(f\"echo {user_input}\")\n    \n    # Another command injection\n    subprocess.call(f\"ls {user_input}\", shell=True)\n    \n    return query\n",
        "language": "python",
        "filename": "test.py"
    }
    
    request = AuditRequest(**request_data)
    
    print("Testing exact FastAPI endpoint logic...")
    print(f"Request code length: {len(request.code)}")
    print(f"Request language: {request.language}")
    print(f"Request filename: {request.filename}")
    
    try:
        # Call exactly as in the FastAPI endpoint
        state = await agent.run(
            code=request.code,
            language=request.language,
            filename=request.filename or "",
            preferred_model=request.model,
            use_advanced_analysis=request.use_advanced_analysis
        )
        
        print(f"Scan results summary: {state.get('scan_results', {}).get('summary', {})}")
        print(f"Number of vulnerabilities found: {len(state.get('vulnerabilities', []))}")
        
        if state.get('vulnerabilities'):
            print("Vulnerabilities found:")
            for vuln in state.get('vulnerabilities', []):
                print(f"- {vuln.get('id')}: {vuln.get('title')} (Severity: {vuln.get('severity')})")
        else:
            print("No vulnerabilities found!")
            print("Scan results:", state.get('scan_results'))
            
    except Exception as e:
        print(f"Error during agent execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_endpoint_logic())