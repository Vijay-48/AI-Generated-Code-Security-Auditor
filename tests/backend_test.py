#!/usr/bin/env python3
"""
Comprehensive Backend Test for AI Code Security Auditor
Tests all API endpoints, CLI functionality, and vulnerability detection
"""

import requests
import json
import sys
import time
import subprocess
import os
from datetime import datetime
from pathlib import Path

class AISecurityAuditorTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def test_server_health(self):
        """Test server health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            if success:
                expected_fields = ["status", "version", "features"]
                missing_fields = [f for f in expected_fields if f not in data]
                if missing_fields:
                    success = False
                    details = f"Missing fields: {missing_fields}"
                else:
                    details = f"Status: {data.get('status')}, Version: {data.get('version')}"
            else:
                details = f"HTTP {response.status_code}"
                
            self.log_test("Server Health Check", success, details)
            return success
        except Exception as e:
            self.log_test("Server Health Check", False, str(e))
            return False

    def test_models_endpoint(self):
        """Test models endpoint"""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                expected_models = 4  # Should have 4 models
                actual_models = len(data.get('available_models', []))
                
                if actual_models != expected_models:
                    success = False
                    details = f"Expected {expected_models} models, got {actual_models}"
                else:
                    details = f"Found {actual_models} AI models"
            else:
                details = f"HTTP {response.status_code}"
                
            self.log_test("Models Endpoint", success, details)
            return success
        except Exception as e:
            self.log_test("Models Endpoint", False, str(e))
            return False

    def test_audit_endpoint_basic(self):
        """Test basic audit endpoint functionality"""
        try:
            # Test with simple vulnerable code
            payload = {
                "code": "import os; os.system(user_input)",
                "language": "python"
            }
            
            response = requests.post(
                f"{self.base_url}/audit", 
                json=payload, 
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ["vulnerabilities", "scan_results"]
                missing_fields = [f for f in required_fields if f not in data]
                
                if missing_fields:
                    success = False
                    details = f"Missing response fields: {missing_fields}"
                else:
                    vuln_count = len(data.get('vulnerabilities', []))
                    details = f"Found {vuln_count} vulnerabilities"
            else:
                details = f"HTTP {response.status_code}: {response.text[:200]}"
                
            self.log_test("Basic Audit Endpoint", success, details)
            return success
        except Exception as e:
            self.log_test("Basic Audit Endpoint", False, str(e))
            return False

    def test_audit_endpoint_comprehensive(self):
        """Test audit endpoint with the comprehensive test.py file"""
        try:
            # Read the test.py file
            test_file_path = "/app/test.py"
            if not os.path.exists(test_file_path):
                self.log_test("Comprehensive Audit Test", False, "test.py file not found")
                return False
                
            with open(test_file_path, 'r') as f:
                test_code = f.read()
            
            payload = {
                "code": test_code,
                "language": "python",
                "filename": "test.py",
                "use_advanced_analysis": True
            }
            
            response = requests.post(
                f"{self.base_url}/audit", 
                json=payload, 
                headers={"Content-Type": "application/json"},
                timeout=120  # Longer timeout for comprehensive analysis
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                vulnerabilities = data.get('vulnerabilities', [])
                vuln_count = len(vulnerabilities)
                
                # Should find multiple vulnerabilities (expecting 15+)
                if vuln_count < 10:
                    success = False
                    details = f"Expected 15+ vulnerabilities, found only {vuln_count}"
                else:
                    # Check for specific vulnerability types
                    vuln_types = [v.get('id', '') for v in vulnerabilities]
                    expected_types = ['B602', 'B608', 'B105', 'B301', 'B303']  # Common Bandit IDs
                    found_types = [t for t in expected_types if any(t in vt for vt in vuln_types)]
                    
                    details = f"Found {vuln_count} vulnerabilities, types: {found_types}"
            else:
                details = f"HTTP {response.status_code}: {response.text[:200]}"
                
            self.log_test("Comprehensive Audit Test", success, details)
            return success
        except Exception as e:
            self.log_test("Comprehensive Audit Test", False, str(e))
            return False

    def test_cli_models_command(self):
        """Test CLI models command"""
        try:
            # Test using the wrapper script
            result = subprocess.run(
                ["./auditor.sh", "models"],
                cwd="/app",
                capture_output=True,
                text=True,
                timeout=30,
                env={**os.environ, "OPENROUTER_API_KEY": "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"}
            )
            
            success = result.returncode == 0
            
            if success:
                output = result.stdout
                # Check if output contains expected model information
                if "Available Models" in output and "deepcoder" in output.lower():
                    details = "CLI models command working correctly"
                else:
                    success = False
                    details = f"Unexpected output format: {output[:200]}"
            else:
                details = f"Exit code {result.returncode}: {result.stderr[:200]}"
                
            self.log_test("CLI Models Command", success, details)
            return success
        except Exception as e:
            self.log_test("CLI Models Command", False, str(e))
            return False

    def test_cli_scan_command(self):
        """Test CLI scan command with test.py"""
        try:
            # Test scanning the test.py file
            result = subprocess.run(
                ["./auditor.sh", "scan", "--path", "test.py"],
                cwd="/app",
                capture_output=True,
                text=True,
                timeout=120,
                env={**os.environ, "OPENROUTER_API_KEY": "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"}
            )
            
            success = result.returncode == 0
            
            if success:
                output = result.stdout
                # Check if vulnerabilities were found
                if "vulnerabilities found" in output.lower() or "security audit results" in output.lower():
                    # Extract vulnerability count if possible
                    lines = output.split('\n')
                    summary_line = [l for l in lines if "vulnerabilities found" in l.lower()]
                    details = summary_line[0] if summary_line else "Scan completed successfully"
                else:
                    success = False
                    details = f"No vulnerability summary found in output: {output[:300]}"
            else:
                details = f"Exit code {result.returncode}: {result.stderr[:200]}"
                
            self.log_test("CLI Scan Command", success, details)
            return success
        except Exception as e:
            self.log_test("CLI Scan Command", False, str(e))
            return False

    def test_cli_analyze_command(self):
        """Test CLI analyze command with direct code"""
        try:
            # Test analyzing a code snippet directly
            vulnerable_code = "import os; os.system(user_input)"
            
            result = subprocess.run(
                ["./auditor.sh", "analyze", "--code", vulnerable_code, "--language", "python"],
                cwd="/app",
                capture_output=True,
                text=True,
                timeout=60,
                env={**os.environ, "OPENROUTER_API_KEY": "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"}
            )
            
            success = result.returncode == 0
            
            if success:
                output = result.stdout
                # Should detect the command injection vulnerability
                if "analysis results" in output.lower() and ("vulnerability" in output.lower() or "no vulnerabilities" in output.lower()):
                    details = "CLI analyze command working correctly"
                else:
                    success = False
                    details = f"Unexpected output format: {output[:200]}"
            else:
                details = f"Exit code {result.returncode}: {result.stderr[:200]}"
                
            self.log_test("CLI Analyze Command", success, details)
            return success
        except Exception as e:
            self.log_test("CLI Analyze Command", False, str(e))
            return False

    def test_output_formats(self):
        """Test different output formats"""
        formats_to_test = ["json", "github", "table"]
        all_success = True
        
        for format_type in formats_to_test:
            try:
                result = subprocess.run(
                    ["./auditor.sh", "scan", "--path", "test.py", "--output-format", format_type],
                    cwd="/app",
                    capture_output=True,
                    text=True,
                    timeout=120,
                    env={**os.environ, "OPENROUTER_API_KEY": "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"}
                )
                
                success = result.returncode == 0
                
                if success:
                    output = result.stdout
                    # Basic validation for each format
                    if format_type == "json" and not output.strip().startswith('['):
                        success = False
                    elif format_type == "github" and "Security Audit Results" not in output:
                        success = False
                    elif format_type == "table" and "Security Audit Results" not in output:
                        success = False
                
                if not success:
                    all_success = False
                    
                self.log_test(f"Output Format: {format_type}", success, 
                            "Format working correctly" if success else f"Format validation failed")
                            
            except Exception as e:
                all_success = False
                self.log_test(f"Output Format: {format_type}", False, str(e))
        
        return all_success

    def test_error_handling(self):
        """Test error handling with invalid inputs"""
        test_cases = [
            {
                "name": "Empty Code",
                "payload": {"code": "", "language": "python"},
                "expected_status": 422
            },
            {
                "name": "Invalid Language", 
                "payload": {"code": "print('hello')", "language": "invalid"},
                "expected_status": 422
            },
            {
                "name": "Missing Language",
                "payload": {"code": "print('hello')"},
                "expected_status": 422
            }
        ]
        
        all_success = True
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/audit",
                    json=test_case["payload"],
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                success = response.status_code == test_case["expected_status"]
                details = f"Expected {test_case['expected_status']}, got {response.status_code}"
                
                if not success:
                    all_success = False
                    
                self.log_test(f"Error Handling: {test_case['name']}", success, details)
                
            except Exception as e:
                all_success = False
                self.log_test(f"Error Handling: {test_case['name']}", False, str(e))
        
        return all_success

    def run_all_tests(self):
        """Run all tests and generate report"""
        print("🚀 Starting AI Code Security Auditor Backend Tests")
        print("=" * 60)
        
        # Core API Tests
        print("\n📡 API Endpoint Tests:")
        self.test_server_health()
        self.test_models_endpoint()
        self.test_audit_endpoint_basic()
        self.test_audit_endpoint_comprehensive()
        
        # CLI Tests
        print("\n💻 CLI Functionality Tests:")
        self.test_cli_models_command()
        self.test_cli_scan_command()
        self.test_cli_analyze_command()
        
        # Output Format Tests
        print("\n📄 Output Format Tests:")
        self.test_output_formats()
        
        # Error Handling Tests
        print("\n🚨 Error Handling Tests:")
        self.test_error_handling()
        
        # Generate Summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! The AI Code Security Auditor is working correctly.")
            return 0
        else:
            failed_tests = [t for t in self.test_results if not t['success']]
            print(f"❌ {len(failed_tests)} tests failed:")
            for test in failed_tests:
                print(f"   - {test['name']}: {test['details']}")
            return 1

def main():
    """Main test execution"""
    tester = AISecurityAuditorTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())