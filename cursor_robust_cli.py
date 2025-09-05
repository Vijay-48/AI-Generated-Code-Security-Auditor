#!/usr/bin/env python3
"""
Robust CLI Wrapper for AI Code Security Auditor
Includes retry logic, connection stability, and better error handling
"""
import os
import sys
import time
import requests
import subprocess
from pathlib import Path

# Set environment variables
os.environ.setdefault('OPENROUTER_API_KEY', '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')

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class RobustCLI:
    """Robust CLI with connection retry and health checking"""
    
    def __init__(self, max_retries=3, retry_delay=2):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.server_url = "http://localhost:8000"
    
    def wait_for_server(self, timeout=30):
        """Wait for server to be ready with health checks"""
        print("🔍 Checking server availability...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.server_url}/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Server is ready!")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            print("⏳ Waiting for server... (will retry)")
            time.sleep(2)
        
        print("❌ Server not responding after 30 seconds")
        return False
    
    def run_cli_with_retry(self, args):
        """Run CLI command with retry logic"""
        
        # First, check if server is available
        if not self.wait_for_server():
            print("💡 Try starting the server first: python cursor_robust_server.py")
            return 1
        
        # Run the CLI command with retries
        for attempt in range(self.max_retries):
            try:
                print(f"🤖 Running CLI command (attempt {attempt + 1}/{self.max_retries})")
                print(f"📝 Command: python -m auditor.cli {' '.join(args)}")
                
                cmd = [sys.executable, "-m", "auditor.cli"] + args
                
                result = subprocess.run(
                    cmd, 
                    cwd=project_root, 
                    check=True,
                    timeout=120,  # 2 minute timeout
                    env={**os.environ, "OPENROUTER_API_KEY": os.environ['OPENROUTER_API_KEY']}
                )
                
                print("✅ Command completed successfully!")
                return result.returncode
                
            except subprocess.TimeoutExpired:
                print(f"⏰ Command timed out (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    print(f"🔄 Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print("❌ Command timed out after all retries")
                    print("💡 Try with a simpler command or restart the server")
                    return 1
                    
            except subprocess.CalledProcessError as e:
                print(f"❌ Command failed with exit code {e.returncode} (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    print(f"🔄 Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print("❌ Command failed after all retries")
                    print("💡 Ask Cursor AI: 'Help me debug this CLI error'")
                    return e.returncode
                    
            except Exception as e:
                print(f"❌ Unexpected error: {e} (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    print(f"🔄 Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print("❌ Unexpected error after all retries")
                    return 1
        
        return 1

def show_help():
    """Show help information"""
    print("🛡️ AI Code Security Auditor - Robust CLI Wrapper")
    print("=" * 50)
    print("Usage examples:")
    print("  python cursor_robust_cli.py models")
    print("  python cursor_robust_cli.py scan --path test.py")
    print("  python cursor_robust_cli.py scan --path . --output-format github")
    print("  python cursor_robust_cli.py analyze --code 'import os; os.system(input())' --language python")
    print("")
    print("Output formats: table, json, github, sarif, csv")
    print("")
    print("💡 Make sure the server is running first:")
    print("   python cursor_robust_server.py")
    print("")
    print("💡 Use Cursor AI chat (Ctrl+L) for help with commands!")

def main():
    """Main CLI function"""
    if len(sys.argv) < 2:
        show_help()
        return 0
    
    # Special help command
    if sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
        return 0
    
    # Initialize robust CLI
    cli = RobustCLI()
    
    # Run the command
    cli_args = sys.argv[1:]
    return cli.run_cli_with_retry(cli_args)

if __name__ == "__main__":
    sys.exit(main())