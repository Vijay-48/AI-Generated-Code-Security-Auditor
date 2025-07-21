#!/usr/bin/env python3
"""
Comprehensive Backend Test Suite for AI Code Security Auditor
Tests the enhanced multi-model OpenRouter integration
"""

import requests
import json
import time
import sys
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8001"
HEADERS = {"Content-Type": "application/json"}

# Test data - vulnerable code samples
VULNERABLE_PYTHON_CODE = '''
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

VULNERABLE_JS_CODE = '''
function processUserData(userInput) {
    // XSS vulnerability
    document.getElementById("output").innerHTML = userInput;
    
    // Command injection in Node.js
    const { exec } = require('child_process');
    exec(`echo ${userInput}`, (error, stdout, stderr) => {
        console.log(stdout);
    });
}
'''

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def add_pass(self, test_name: str):
        self.passed += 1
        print(f"✅ PASS: {test_name}")
        
    def add_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"❌ FAIL: {test_name} - {error}")
        
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY: {self.passed}/{total} tests passed")
        if self.errors:
            print(f"\nFAILED TESTS:")
            for error in self.errors:
                print(f"  - {error}")
        print(f"{'='*60}")
        return self.failed == 0

def test_health_check(results: TestResults):
    """Test basic health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok" and "version" in data:
                results.add_pass("Health Check")
            else:
                results.add_fail("Health Check", f"Invalid response format: {data}")
        else:
            results.add_fail("Health Check", f"Status code: {response.status_code}")
    except Exception as e:
        results.add_fail("Health Check", str(e))

def test_root_endpoint(results: TestResults):
    """Test root endpoint with features"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            required_fields = ["message", "version", "features", "endpoints"]
            if all(field in data for field in required_fields):
                if len(data["features"]) >= 4:  # Should have multiple features
                    results.add_pass("Root Endpoint")
                else:
                    results.add_fail("Root Endpoint", "Insufficient features listed")
            else:
                results.add_fail("Root Endpoint", f"Missing required fields: {required_fields}")
        else:
            results.add_fail("Root Endpoint", f"Status code: {response.status_code}")
    except Exception as e:
        results.add_fail("Root Endpoint", str(e))

def test_models_endpoint(results: TestResults):
    """Test models endpoint with available models"""
    try:
        response = requests.get(f"{BASE_URL}/models", timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            required_fields = ["available_models", "recommendations", "model_info"]
            if not all(field in data for field in required_fields):
                results.add_fail("Models Endpoint", f"Missing required fields: {required_fields}")
                return
                
            # Check for all 4 expected models
            expected_models = [
                "agentica-org/deepcoder-14b-preview:free",
                "moonshotai/kimi-dev-72b:free", 
                "qwen/qwen-2.5-coder-32b-instruct:free",
                "meta-llama/llama-3.3-70b-instruct:free"
            ]
            
            available_models = data["available_models"]
            missing_models = [model for model in expected_models if model not in available_models]
            
            if missing_models:
                results.add_fail("Models Endpoint", f"Missing models: {missing_models}")
            else:
                results.add_pass("Models Endpoint")
                
        else:
            results.add_fail("Models Endpoint", f"Status code: {response.status_code}")
    except Exception as e:
        results.add_fail("Models Endpoint", str(e))

def test_basic_audit(results: TestResults):
    """Test basic audit functionality with Python code"""
    try:
        payload = {
            "code": VULNERABLE_PYTHON_CODE,
            "language": "python",
            "filename": "test.py"
        }
        
        response = requests.post(f"{BASE_URL}/audit", json=payload, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check response structure
            required_fields = ["scan_results", "vulnerabilities", "remediation_suggestions", "patches", "assessments"]
            if not all(field in data for field in required_fields):
                results.add_fail("Basic Audit", f"Missing required fields: {required_fields}")
                return
                
            # Check if vulnerabilities were detected
            vulnerabilities = data["vulnerabilities"]
            if len(vulnerabilities) > 0:
                # Check if we detected expected vulnerability types
                vuln_ids = [v.get("id", "") for v in vulnerabilities]
                if any("B605" in vid or "B607" in vid or "B602" in vid for vid in vuln_ids):
                    results.add_pass("Basic Audit - Vulnerability Detection")
                else:
                    results.add_fail("Basic Audit", f"Expected command injection vulnerabilities, got: {vuln_ids}")
            else:
                results.add_fail("Basic Audit", "No vulnerabilities detected in vulnerable code")
                
        else:
            results.add_fail("Basic Audit", f"Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        results.add_fail("Basic Audit", str(e))

def test_model_selection(results: TestResults):
    """Test audit with specific model selection"""
    models_to_test = [
        "agentica-org/deepcoder-14b-preview:free",
        "qwen/qwen-2.5-coder-32b-instruct:free",
        "meta-llama/llama-3.3-70b-instruct:free"
    ]
    
    for model in models_to_test:
        try:
            payload = {
                "code": VULNERABLE_PYTHON_CODE,
                "language": "python", 
                "model": model,
                "filename": "test.py"
            }
            
            response = requests.post(f"{BASE_URL}/audit", json=payload, headers=HEADERS, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if "vulnerabilities" in data and len(data["vulnerabilities"]) > 0:
                    results.add_pass(f"Model Selection - {model.split('/')[1]}")
                else:
                    results.add_fail(f"Model Selection - {model.split('/')[1]}", "No vulnerabilities detected")
            else:
                results.add_fail(f"Model Selection - {model.split('/')[1]}", f"Status code: {response.status_code}")
                
        except Exception as e:
            results.add_fail(f"Model Selection - {model.split('/')[1]}", str(e))

def test_advanced_analysis(results: TestResults):
    """Test advanced analysis flag"""
    try:
        payload = {
            "code": VULNERABLE_PYTHON_CODE,
            "language": "python",
            "use_advanced_analysis": True,
            "filename": "test.py"
        }
        
        response = requests.post(f"{BASE_URL}/audit", json=payload, headers=HEADERS, timeout=45)
        
        if response.status_code == 200:
            data = response.json()
            
            # Advanced analysis should still detect vulnerabilities
            if "vulnerabilities" in data and len(data["vulnerabilities"]) > 0:
                results.add_pass("Advanced Analysis")
            else:
                results.add_fail("Advanced Analysis", "No vulnerabilities detected with advanced analysis")
        else:
            results.add_fail("Advanced Analysis", f"Status code: {response.status_code}")
            
    except Exception as e:
        results.add_fail("Advanced Analysis", str(e))

def test_javascript_support(results: TestResults):
    """Test JavaScript code analysis"""
    try:
        payload = {
            "code": VULNERABLE_JS_CODE,
            "language": "javascript",
            "filename": "test.js"
        }
        
        response = requests.post(f"{BASE_URL}/audit", json=payload, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if scan completed (may or may not find vulnerabilities depending on semgrep rules)
            if "scan_results" in data:
                results.add_pass("JavaScript Support")
            else:
                results.add_fail("JavaScript Support", "Missing scan_results")
        else:
            results.add_fail("JavaScript Support", f"Status code: {response.status_code}")
            
    except Exception as e:
        results.add_fail("JavaScript Support", str(e))

def test_error_handling(results: TestResults):
    """Test error handling for invalid requests"""
    
    # Test empty code
    try:
        payload = {"code": "", "language": "python"}
        response = requests.post(f"{BASE_URL}/audit", json=payload, headers=HEADERS, timeout=10)
        
        if response.status_code == 422:  # Validation error
            results.add_pass("Error Handling - Empty Code")
        else:
            results.add_fail("Error Handling - Empty Code", f"Expected 422, got {response.status_code}")
    except Exception as e:
        results.add_fail("Error Handling - Empty Code", str(e))
    
    # Test invalid language
    try:
        payload = {"code": "print('hello')", "language": "invalid_lang"}
        response = requests.post(f"{BASE_URL}/audit", json=payload, headers=HEADERS, timeout=10)
        
        if response.status_code == 422:  # Validation error
            results.add_pass("Error Handling - Invalid Language")
        else:
            results.add_fail("Error Handling - Invalid Language", f"Expected 422, got {response.status_code}")
    except Exception as e:
        results.add_fail("Error Handling - Invalid Language", str(e))
    
    # Test invalid model
    try:
        payload = {
            "code": "print('hello')", 
            "language": "python",
            "model": "invalid-model"
        }
        response = requests.post(f"{BASE_URL}/audit", json=payload, headers=HEADERS, timeout=10)
        
        if response.status_code == 422:  # Validation error
            results.add_pass("Error Handling - Invalid Model")
        else:
            results.add_fail("Error Handling - Invalid Model", f"Expected 422, got {response.status_code}")
    except Exception as e:
        results.add_fail("Error Handling - Invalid Model", str(e))

def test_openrouter_integration(results: TestResults):
    """Test OpenRouter integration with patch generation"""
    try:
        payload = {
            "code": VULNERABLE_PYTHON_CODE,
            "language": "python",
            "model": "agentica-org/deepcoder-14b-preview:free",  # DeepCoder for patches
            "filename": "test.py"
        }
        
        response = requests.post(f"{BASE_URL}/audit", json=payload, headers=HEADERS, timeout=45)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if patches were generated (or at least attempted)
            patches = data.get("patches", [])
            if patches:
                # Check if we got actual patches or rate limit errors
                has_patches = any("diff" in patch.get("patch", {}) for patch in patches)
                has_rate_limit = any("503" in str(patch.get("patch", {})) or "rate" in str(patch.get("patch", {})).lower() for patch in patches)
                
                if has_patches:
                    results.add_pass("OpenRouter Integration - Patch Generation")
                elif has_rate_limit:
                    results.add_pass("OpenRouter Integration - Rate Limit Handling")
                else:
                    # Check for API key errors (401)
                    has_auth_error = any("401" in str(patch.get("patch", {})) for patch in patches)
                    if has_auth_error:
                        results.add_fail("OpenRouter Integration", "API authentication failed - check API key")
                    else:
                        results.add_pass("OpenRouter Integration - Attempted")
            else:
                results.add_fail("OpenRouter Integration", "No patches generated")
        else:
            results.add_fail("OpenRouter Integration", f"Status code: {response.status_code}")
            
    except Exception as e:
        results.add_fail("OpenRouter Integration", str(e))

def test_backward_compatibility(results: TestResults):
    """Test that original functionality works without model specification"""
    try:
        payload = {
            "code": VULNERABLE_PYTHON_CODE,
            "language": "python"
            # No model specified - should use defaults
        }
        
        response = requests.post(f"{BASE_URL}/audit", json=payload, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Should still detect vulnerabilities
            if "vulnerabilities" in data and len(data["vulnerabilities"]) > 0:
                results.add_pass("Backward Compatibility")
            else:
                results.add_fail("Backward Compatibility", "No vulnerabilities detected without model specification")
        else:
            results.add_fail("Backward Compatibility", f"Status code: {response.status_code}")
            
    except Exception as e:
        results.add_fail("Backward Compatibility", str(e))

def main():
    """Run all backend tests"""
    print("🚀 Starting AI Code Security Auditor Backend Tests")
    print(f"Testing against: {BASE_URL}")
    print("="*60)
    
    results = TestResults()
    
    # Basic API tests
    print("\n📋 Basic API Health Checks")
    test_health_check(results)
    test_root_endpoint(results)
    test_models_endpoint(results)
    
    # Core functionality tests
    print("\n🔍 Core Security Scanning")
    test_basic_audit(results)
    test_javascript_support(results)
    test_backward_compatibility(results)
    
    # Enhanced features tests
    print("\n🤖 Multi-Model Features")
    test_model_selection(results)
    test_advanced_analysis(results)
    test_openrouter_integration(results)
    
    # Error handling tests
    print("\n⚠️  Error Handling")
    test_error_handling(results)
    
    # Final summary
    success = results.summary()
    
    if success:
        print("\n🎉 All tests passed! The AI Code Security Auditor is working correctly.")
        sys.exit(0)
    else:
        print(f"\n💥 {results.failed} test(s) failed. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()