#!/usr/bin/env python3
"""
Test file with multiple security vulnerabilities and secrets
"""
import os
import subprocess

# Secret detection test cases
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"  
DATABASE_URL = "mongodb://admin:password123@localhost/db"
api_key = "sk-1234567890abcdef"
password = "hardcoded_password"

def insecure_function(user_input):
    # Command injection vulnerability
    os.system(f"rm -rf {user_input}")  # Command injection
    
    # SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    
    # Another command injection
    subprocess.call(f"ls {user_input}", shell=True)
    
    return query

def another_vuln():
    # Hardcoded password
    db_password = "super_secret_password_123"
    
    # More command injection
    os.system("echo 'vulnerable'")
    
    return db_password