#!/usr/bin/env python3
"""
Demo: Command Injection Vulnerabilities
For hackathon demonstration
"""

import os
import subprocess

def vulnerable_ping(ip_address):
    """CRITICAL: Command injection via os.system"""
    # Attacker can inject: 8.8.8.8; rm -rf /
    os.system(f"ping -c 4 {ip_address}")

def vulnerable_file_viewer(filename):
    """CRITICAL: Command injection via subprocess.call"""
    # Attacker can inject: file.txt && cat /etc/passwd
    subprocess.call(f"cat {filename}", shell=True)

def vulnerable_backup(directory):
    """CRITICAL: Command injection in backup script"""
    backup_cmd = "tar -czf backup.tar.gz " + directory
    os.system(backup_cmd)

def vulnerable_convert(input_file, output_file):
    """CRITICAL: Command injection via exec"""
    command = f"convert {input_file} {output_file}"
    exec(command)  # Double vulnerability: exec + command injection

def vulnerable_network_test(host):
    """CRITICAL: Command injection via subprocess"""
    result = subprocess.check_output(f"nslookup {host}", shell=True)
    return result.decode()

# Example exploits:
# vulnerable_ping("8.8.8.8; cat /etc/passwd")
# vulnerable_file_viewer("file.txt && whoami")
