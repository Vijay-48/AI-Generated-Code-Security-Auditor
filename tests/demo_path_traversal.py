#!/usr/bin/env python3
"""
Demo: Path Traversal Vulnerabilities
For hackathon demonstration
"""

import os

def vulnerable_file_read(filename):
    """CRITICAL: Path traversal vulnerability"""
    # Attacker can use: ../../../../etc/passwd
    with open(f"/var/www/uploads/{filename}", 'r') as f:
        return f.read()

def vulnerable_file_download(file_path):
    """CRITICAL: Arbitrary file read"""
    # No validation of file path
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            return f.read()
    return None

def vulnerable_image_serve(image_name):
    """CRITICAL: Directory traversal in file serving"""
    base_dir = "/var/www/images/"
    # CRITICAL: No sanitization of image_name
    full_path = base_dir + image_name
    
    with open(full_path, 'rb') as f:
        return f.read()

def vulnerable_log_viewer(log_file):
    """CRITICAL: Path traversal in log viewing"""
    log_dir = "/var/log/app/"
    # Attacker can use: ../../../etc/shadow
    log_path = os.path.join(log_dir, log_file)
    
    with open(log_path, 'r') as f:
        return f.readlines()

def vulnerable_backup_restore(backup_name):
    """CRITICAL: Arbitrary file write"""
    backup_dir = "/backups/"
    restore_path = backup_dir + backup_name
    
    # CRITICAL: Can overwrite system files
    with open(restore_path, 'w') as f:
        f.write("restored content")

def vulnerable_template_load(template_name):
    """CRITICAL: Template injection via path traversal"""
    template_dir = "./templates/"
    # Attacker can load arbitrary files
    template_path = template_dir + template_name
    
    with open(template_path, 'r') as f:
        return f.read()

# Example exploits:
# vulnerable_file_read("../../../etc/passwd")
# vulnerable_file_download("/etc/shadow")
# vulnerable_image_serve("../../config/database.yml")
