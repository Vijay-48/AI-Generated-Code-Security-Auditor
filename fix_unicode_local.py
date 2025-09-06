#!/usr/bin/env python3
"""
Quick fix script to remove Unicode characters from local AI Code Security Auditor files
Run this in your local directory: A:\Project\AI-Generated-Code-Security-Auditor
"""
import os
import sys
import re
from pathlib import Path

def fix_file_unicode(file_path, replacements):
    """Fix Unicode characters in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all replacements
        for old, new in replacements:
            content = content.replace(old, new)
        
        if content != original_content:
            # Backup original file
            backup_path = f"{file_path}.backup"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Write fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ Fixed {file_path} (backup saved as {backup_path})")
            return True
        else:
            print(f"- No changes needed in {file_path}")
            return False
            
    except Exception as e:
        print(f"✗ Error fixing {file_path}: {e}")
        return False

def add_windows_encoding_fix(file_path):
    """Add Windows UTF-8 encoding fix to Python files"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if fix already exists
        if 'sys.platform.startswith(' in content:
            print(f"- Windows encoding fix already exists in {file_path}")
            return False
        
        # Find import section
        lines = content.split('\n')
        insert_pos = -1
        
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                insert_pos = i
        
        if insert_pos == -1:
            print(f"- Could not find import section in {file_path}")
            return False
        
        # Find end of imports
        for i in range(insert_pos, len(lines)):
            if not (lines[i].startswith('import ') or lines[i].startswith('from ') or lines[i].strip() == ''):
                insert_pos = i
                break
        
        # Add Windows encoding fix
        encoding_fix = [
            "",
            "# Windows-compatible output encoding",
            "if sys.platform.startswith('win'):",
            "    if hasattr(sys.stdout, 'reconfigure'):",
            "        sys.stdout.reconfigure(encoding='utf-8')",
            "    elif hasattr(sys.stdout, 'buffer'):",
            "        import codecs",
            "        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')",
            ""
        ]
        
        # Insert the fix
        for i, fix_line in enumerate(encoding_fix):
            lines.insert(insert_pos + i, fix_line)
        
        # Backup and write
        backup_path = f"{file_path}.backup"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"✓ Added Windows encoding fix to {file_path}")
        return True
        
    except Exception as e:
        print(f"✗ Error adding encoding fix to {file_path}: {e}")
        return False

def main():
    """Main fix function"""
    print("AI Code Security Auditor - Unicode Fix Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('cursor_robust_server.py'):
        print("✗ Error: cursor_robust_server.py not found in current directory")
        print("Please run this script from your AI Code Security Auditor directory")
        return 1
    
    # Define replacements for common Unicode characters
    server_replacements = [
        ('🚀 Starting AI Code Security Auditor FastAPI Server...', 'STARTING AI Code Security Auditor FastAPI Server...'),
        ('🔧 Cursor AI Development Mode - Robust Configuration', 'CURSOR AI Development Mode - Robust Configuration'),
        ('🎯 AI Code Security Auditor - READY', 'AI Code Security Auditor - READY'),
        ('📚 API Documentation:', 'API Documentation:'),
        ('🔍 Health Check:', 'Health Check:'),
        ('🤖 Models Endpoint:', 'Models Endpoint:'),
        ('🔥 Interactive API:', 'Interactive API:'),
        ('💡 Server is stable and ready for CLI commands!', 'Server is stable and ready for CLI commands!'),
        ('🛑 Press Ctrl+C to stop the server', 'Press Ctrl+C to stop the server'),
    ]
    
    cli_replacements = [
        ('🔍 Checking server availability...', 'Checking server availability...'),
        ('✅ Server is ready!', 'Server is ready!'),
        ('⏳ Waiting for server...', 'Waiting for server...'),
        ('❌ Server not responding', 'Server not responding'),
        ('🤖 Running CLI command', 'Running CLI command'),
        ('📝 Command:', 'Command:'),
        ('✅ Command completed successfully!', 'Command completed successfully!'),
        ('⏰ Command timed out', 'Command timed out'),
        ('🔄 Retrying in', 'Retrying in'),
        ('❌ Command failed', 'Command failed'),
        ('❌ Unexpected error', 'Unexpected error'),
        ('🛡️ AI Code Security Auditor', 'AI Code Security Auditor'),
        ('💡 Make sure the server', 'Make sure the server'),
        ('💡 Use Cursor AI chat', 'Use the application for help'),
    ]
    
    app_main_replacements = [
        ('🚀 Starting AI Code Security Auditor...', 'STARTING AI Code Security Auditor...'),
        ('✅ Application startup complete', 'Application startup complete'),
        ('🔄 Shutting down AI Code Security Auditor...', 'Shutting down AI Code Security Auditor...'),
        ('✅ Application shutdown complete', 'Application shutdown complete'),
    ]
    
    cli_auditor_replacements = [
        ('🔍 Scanning', 'Scanning'),
        ('⚠️  Error scanning', 'Error scanning'),
        ('❌ No supported files', 'No supported files'),
        ('📄 Report saved to', 'Report saved to'),
        ('📊 Scan complete:', 'Scan complete:'),
        ('❌ High/Critical severity', 'High/Critical severity'),
        ('❌ Scan failed:', 'Scan failed:'),
        ('🔍 Analysis Results:', 'Analysis Results:'),
        ('📍 ', '[!] '),
        ('✅ No vulnerabilities detected', 'No vulnerabilities detected'),
        ('🤖 AI-Generated Fix:', 'AI-Generated Fix:'),
        ('❌ Analysis failed:', 'Analysis failed:'),
        ('🤖 Available Models:', 'Available Models:'),
        ('💡 Recommendations:', 'Recommendations:'),
        ('❌ Failed to fetch models:', 'Failed to fetch models:'),
        ('🔍 Security Audit Results', 'Security Audit Results'),
        ('📁 File:', 'File:'),
        ('🚨 ', '[!] '),
        ('🤖 AI Fix Available:', 'AI Fix Available:'),
        ('✅ No vulnerabilities found!', 'No vulnerabilities found!'),
        ('## 🛡️ AI Security Audit Results', '## AI Security Audit Results'),
        ('✅ **No vulnerabilities detected!**', '**No vulnerabilities detected!**'),
        ('❌ **', '**'),
        ('🔴', 'HIGH'),
        ('🟡', 'MEDIUM'),
        ('🟢', 'LOW'),
        ('⚫', 'CRITICAL'),
        ('🔍', 'UNKNOWN'),
        ('✅', 'Available'),
        ('❌', 'No'),
        ('### 🤖 AI-Powered Features', '### AI-Powered Features'),
    ]
    
    files_to_fix = [
        ('cursor_robust_server.py', server_replacements),
        ('cursor_robust_cli.py', cli_replacements),
        ('app/main.py', app_main_replacements),
        ('auditor/cli.py', cli_auditor_replacements),
    ]
    
    fixed_count = 0
    
    # Fix Unicode characters in files
    for file_path, replacements in files_to_fix:
        if os.path.exists(file_path):
            if fix_file_unicode(file_path, replacements):
                fixed_count += 1
        else:
            print(f"- Skipping {file_path} (not found)")
    
    # Add Windows encoding fixes
    encoding_files = ['cursor_robust_server.py', 'cursor_robust_cli.py']
    for file_path in encoding_files:
        if os.path.exists(file_path):
            add_windows_encoding_fix(file_path)
    
    print("\n" + "=" * 50)
    print(f"Fixed {fixed_count} files")
    print("✓ Unicode characters replaced with plain text")
    print("✓ Windows encoding fixes added")
    print("\nYou can now run your server without Unicode errors:")
    print("  python cursor_robust_server.py")
    print("\nBackup files (.backup) have been created for safety.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())