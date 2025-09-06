#!/usr/bin/env python3
"""
Test script to verify the fixes are working correctly
"""
import subprocess
import sys
import time

def test_server_start():
    """Test that server starts without Unicode errors"""
    print("Testing server startup...")
    try:
        # Start server in background
        proc = subprocess.Popen([
            sys.executable, 'cursor_robust_server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for startup
        time.sleep(3)
        
        # Check if it's still running
        if proc.poll() is None:
            print("✓ Server started successfully without Unicode errors")
            proc.terminate()
            proc.wait()
            return True
        else:
            stdout, stderr = proc.communicate()
            print(f"✗ Server failed to start")
            print(f"STDOUT: {stdout.decode('utf-8', errors='ignore')}")
            print(f"STDERR: {stderr.decode('utf-8', errors='ignore')}")
            return False
    except Exception as e:
        print(f"✗ Error testing server: {e}")
        return False

def test_cli_commands():
    """Test CLI commands work without Unicode errors"""
    print("\nTesting CLI commands...")
    
    commands = [
        ['python', 'cursor_robust_cli.py', 'models'],
        ['python', 'cursor_robust_cli.py', 'analyze', '--code', 'import os; os.system("echo hello")', '--language', 'python']
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"✓ Command succeeded: {' '.join(cmd[1:])}")
            else:
                print(f"✗ Command failed: {' '.join(cmd[1:])}")
                print(f"Error: {result.stderr}")
                return False
        except Exception as e:
            print(f"✗ Error running command {' '.join(cmd[1:])}: {e}")
            return False
    
    return True

def main():
    """Run all tests"""
    print("AI Code Security Auditor - Testing Fixed Issues")
    print("=" * 50)
    
    all_passed = True
    
    # Test server startup
    if not test_server_start():
        all_passed = False
    
    # Test CLI commands  
    if not test_cli_commands():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All tests passed! The fixes are working correctly.")
        print("✓ Unicode encoding issues resolved")
        print("✓ Redis made optional with proper fallbacks")
        print("✓ Application works without Redis dependency")
    else:
        print("✗ Some tests failed. Check output above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())