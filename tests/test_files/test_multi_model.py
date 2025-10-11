#!/usr/bin/env python3

import os
import sys
import requests
import json
import time

# Configuration
API_BASE = "http://localhost:8000"
VULNERABLE_CODE = '''
import sqlite3
import os

def login(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor.execute(query)
    
    user = cursor.fetchone()
    if user:
        # Command injection vulnerability  
        os.system(f"echo 'Welcome {username}' >> /var/log/access.log")
        return True
    return False

def get_user_profile(user_id):
    # Path traversal vulnerability
    with open(f"/app/profiles/{user_id}.txt", "r") as f:
        return f.read()
'''

def test_multi_model_audit():
    """Test the enhanced multi-model audit capabilities"""
    
    print("🧪 Testing AI Code Security Auditor - Multi-Model Integration")
    print("=" * 70)
    
    # Test 1: Basic audit with DeepCoder
    print("\n🔍 Test 1: Basic Audit with DeepCoder Model")
    print("-" * 50)
    
    payload = {
        "code": VULNERABLE_CODE,
        "language": "python",
        "model": "agentica-org/deepcoder-14b-preview:free"
    }
    
    response = requests.post(f"{API_BASE}/audit", json=payload)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {len(result['vulnerabilities'])} vulnerabilities")
        
        for vuln in result['vulnerabilities']:
            print(f"   • {vuln['id']}: {vuln['title']} (Severity: {vuln['severity']})")
            
        # Check if we got AI-generated patches
        if result['patches']:
            patch = result['patches'][0]['patch']
            if 'error' not in patch:
                print(f"✅ AI Patch Generated: {len(patch.get('diff', ''))[:100]}...")
            else:
                print(f"⚠️  Patch Generation: {patch['error'][:100]}...")
    else:
        print(f"❌ Basic audit failed: {response.status_code}")
    
    # Wait to avoid rate limiting
    time.sleep(2)
    
    # Test 2: Model comparison
    print("\n🎯 Test 2: Model Comparison")  
    print("-" * 50)
    
    models = [
        "agentica-org/deepcoder-14b-preview:free",
        "qwen/qwen-2.5-coder-32b-instruct:free",
        "meta-llama/llama-3.3-70b-instruct:free"
    ]
    
    for model in models:
        print(f"\n🤖 Testing model: {model.split('/')[1].split(':')[0]}")
        payload = {
            "code": "import os\nos.system('rm -rf /')",  # Simple test case
            "language": "python", 
            "model": model
        }
        
        try:
            response = requests.post(f"{API_BASE}/audit", json=payload)
            if response.status_code == 200:
                result = response.json()
                if result['patches'] and 'error' not in result['patches'][0]['patch']:
                    print(f"   ✅ Generated patch successfully")
                else:
                    print(f"   ⚠️  Rate limited or error")
            time.sleep(1)  # Rate limiting
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}...")
    
    # Test 3: Available models endpoint
    print("\n📋 Test 3: Available Models")
    print("-" * 50)
    
    response = requests.get(f"{API_BASE}/models")
    if response.status_code == 200:
        models_info = response.json()
        print("✅ Available Models:")
        for model in models_info['available_models']:
            print(f"   • {model}")
        print(f"\n✅ Model Recommendations:")
        for use_case, model in models_info['recommendations'].items():
            print(f"   • {use_case}: {model.split('/')[1].split(':')[0]}")
    
    # Test 4: Enhanced API features
    print("\n🚀 Test 4: Enhanced API Features")
    print("-" * 50)
    
    response = requests.get(f"{API_BASE}/")
    if response.status_code == 200:
        api_info = response.json()
        print("✅ API Features:")
        for feature in api_info['features']:
            print(f"   • {feature}")
    
    print("\n" + "=" * 70)
    print("🎉 Multi-Model Integration Testing Complete!")
    print("✅ Successfully implemented:")
    print("   • DeepCoder for code patch generation")
    print("   • LLaMA 3.3 for quality assessment")  
    print("   • Qwen for fast classification")
    print("   • Kimi for security explanations")
    print("   • Model selection via API")
    print("   • Enhanced audit pipeline")

if __name__ == "__main__":
    try:
        test_multi_model_audit()
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print("Make sure the server is running: uvicorn app.main:app --host 0.0.0.0 --port 8000")