#!/usr/bin/env python3
"""
Robust Test Suite for AI Code Security Auditor
Fixed timeout issues, connection problems, and test reliability
"""
import requests
import json
import time
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Any

class RobustTestSuite:
    """Test suite with improved reliability and timeout handling"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = []
        self.project_root = Path(__file__).parent
        
        # Improved timeout settings
        self.short_timeout = 10
        self.medium_timeout = 30
        self.long_timeout = 60
        
    def log_test_result(self, test_name: str, success: bool, details: str = "", ai_hint: str = ""):
        """Log test results with AI debugging hints"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        
        if details:
            print(f"   📝 {details}")
        
        if ai_hint and not success:
            print(f"   🤖 AI Hint: {ai_hint}")
            
        self.test_results.append({
            "name": test_name,
            "success": success,
            "details": details,
            "ai_hint": ai_hint
        })
    
    def wait_for_server(self, timeout=30):
        """Wait for server to be available"""
        print("🔍 Waiting for server to be ready...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Server is ready for testing!")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(2)
        
        print("❌ Server not ready for testing")
        return False
    
    def test_server_health(self) -> bool:
        """Test server health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=self.short_timeout)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                expected_fields = ["status", "version", "features"]
                missing_fields = [f for f in expected_fields if f not in data]
                if missing_fields:
                    success = False
                    details = f"Missing fields: {missing_fields}"
                else:
                    details = f"Status: {data.get('status')}, Version: {data.get('version')}"
            else:
                details = f"HTTP {response.status_code}"
                
            self.log_test_result("Server Health Check", success, details)
            return success
            
        except requests.exceptions.Timeout:
            self.log_test_result(
                "Server Health Check", 
                False, 
                "Request timed out",
                "Server might be overloaded - try restarting it"
            )
            return False
        except Exception as e:
            self.log_test_result("Server Health Check", False, str(e))
            return False
    
    def test_models_endpoint(self) -> bool:
        """Test models endpoint"""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=self.short_timeout)
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
                
            self.log_test_result("Models Endpoint", success, details)
            return success
            
        except requests.exceptions.Timeout:
            self.log_test_result(
                "Models Endpoint", 
                False, 
                "Request timed out",
                "Models endpoint taking too long - check server performance"
            )
            return False
        except Exception as e:
            self.log_test_result("Models Endpoint", False, str(e))
            return False
    
    def test_simple_vulnerability_detection(self) -> bool:
        """Test vulnerability detection with simple code (faster test)"""
        simple_vulnerable_code = """
import subprocess
subprocess.call(user_input, shell=True)
password = "admin123"
"""
        
        try:
            payload = {
                "code": simple_vulnerable_code,
                "language": "python",
                "use_advanced_analysis": False  # Disable advanced analysis for speed
            }
            
            response = requests.post(
                f"{self.base_url}/audit",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.medium_timeout  # Medium timeout for simple test
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                vulnerabilities = data.get('vulnerabilities', [])
                vuln_count = len(vulnerabilities)
                
                # Should detect at least 2 vulnerabilities (shell=True, hardcoded password)
                if vuln_count >= 2:
                    details = f"Successfully detected {vuln_count} vulnerabilities"
                else:
                    success = False
                    details = f"Only detected {vuln_count} vulnerabilities (expected 2+)"
            else:
                details = f"HTTP {response.status_code}: {response.text[:200]}"
                
            self.log_test_result("Simple Vulnerability Detection", success, details)
            return success
            
        except requests.exceptions.Timeout:
            self.log_test_result(
                "Simple Vulnerability Detection", 
                False, 
                "Request timed out",
                "Even simple vulnerability detection is timing out - check server stability"
            )
            return False
        except Exception as e:
            self.log_test_result("Simple Vulnerability Detection", False, str(e))
            return False
    
    def test_cli_models_command(self) -> bool:
        """Test CLI models command with better error handling"""
        try:
            # Use the robust CLI wrapper
            result = subprocess.run(
                ["python", "cursor_robust_cli.py", "models"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=self.medium_timeout
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
                
            self.log_test_result("CLI Models Command", success, details)
            return success
            
        except subprocess.TimeoutExpired:
            self.log_test_result(
                "CLI Models Command", 
                False, 
                "Command timed out",
                "CLI command taking too long - try the robust CLI wrapper"
            )
            return False
        except Exception as e:
            self.log_test_result("CLI Models Command", False, str(e))
            return False
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all tests with proper server availability check"""
        print("🚀 Starting Robust Test Suite for AI Code Security Auditor")
        print("🔧 Fixed timeout issues and connection problems")
        print("🤖 Use Cursor AI chat (Ctrl+L) for help with any failures!")
        print("=" * 60)
        
        # First, wait for server to be ready
        if not self.wait_for_server():
            print("❌ Server not available - please start it first:")
            print("   python cursor_robust_server.py")
            return {
                "total_tests": 0,
                "passed_tests": 0,
                "success_rate": 0,
                "all_results": []
            }
        
        # Run tests in order of complexity (simple to complex)
        tests = [
            ("Basic Tests", [
                self.test_server_health,
                self.test_models_endpoint
            ]),
            ("Functionality Tests", [
                self.test_simple_vulnerability_detection,
                self.test_cli_models_command
            ])
        ]
        
        passed = 0
        total = 0
        
        for category, test_functions in tests:
            print(f"\n📋 {category}")
            print("-" * 30)
            
            for test in test_functions:
                total += 1
                if test():
                    passed += 1
                time.sleep(1)  # Brief pause between tests
        
        # Summary
        print("=" * 60)
        print(f"🎯 Test Summary: {passed}/{total} tests passed")
        success_rate = (passed / total * 100) if total > 0 else 0
        
        if passed == total:
            print("🎉 All tests passed! System is fully operational.")
            print("💡 Try running: python cursor_robust_cli.py scan --path test.py")
        elif passed > total // 2:
            print("⚠️  Some tests failed, but core functionality works.")
            print("💡 Ask Cursor AI: 'Help me optimize the failing tests'")
        else:
            print("❌ Multiple test failures detected.")
            print("💡 Ask Cursor AI: 'Help me fix the major issues with the server'")
        
        return {
            "total_tests": total,
            "passed_tests": passed,
            "success_rate": success_rate,
            "all_results": self.test_results
        }

def main():
    """Run the robust test suite"""
    tester = RobustTestSuite()
    results = tester.run_comprehensive_test()
    
    # Save results for analysis
    with open("robust_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Detailed results saved to robust_test_results.json")
    print("💡 Ask Cursor AI to analyze the test results!")
    
    return 0 if results["passed_tests"] == results["total_tests"] else 1

if __name__ == "__main__":
    exit(main())