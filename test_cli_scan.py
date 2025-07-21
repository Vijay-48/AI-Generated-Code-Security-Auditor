# Test file for CLI scanning
import os
import subprocess

# AWS Access Key
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"

# Database credentials
DATABASE_URL = "mongodb://admin:password123@localhost/db"

# API Key
api_key = "sk-1234567890abcdef"

def vulnerable_function(user_input):
    # Command injection
    os.system(f"echo {user_input}")
    
    # SQL injection
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    
    # Another command injection
    subprocess.call(f"ls {user_input}", shell=True)
    
    return query