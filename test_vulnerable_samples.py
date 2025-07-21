#!/usr/bin/env python3
"""
Test file with multiple security vulnerabilities for GitHub Actions testing
"""
import os
import subprocess
import sqlite3
import hashlib

# 1. CRITICAL: Command Injection
def dangerous_system_call(user_input):
    os.system(f"rm -rf {user_input}")  # This should trigger B605 - Critical

# 2. CRITICAL: Hardcoded API Key 
API_KEY = "sk-live-abcd1234567890abcdef1234567890ab"  # Secret detection - Critical

# 3. HIGH: SQL Injection vulnerability
def unsafe_database_query(user_id):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = {user_id}"  # B608 - High
    cursor.execute(query)
    return cursor.fetchall()

# 4. HIGH: Shell injection via subprocess
def unsafe_subprocess(filename):
    subprocess.call(f"cat {filename}", shell=True)  # B602 - High

# 5. MEDIUM: Weak cryptographic hash
def weak_password_hash(password):
    return hashlib.md5(password.encode()).hexdigest()  # B303 - Medium

# 6. LOW: Use of assert statement
def debug_check(condition):
    assert condition == True, "Debug assertion"  # B101 - Low

# 7. CRITICAL: AWS Access Key (should be detected by secret scanner)
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"  # Secret pattern - Critical

# 8. HIGH: Database connection string with credentials
DATABASE_URL = "postgresql://admin:password123@localhost:5432/prod_db"  # Secret - High