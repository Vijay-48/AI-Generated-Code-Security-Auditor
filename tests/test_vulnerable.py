"""
Test file with intentional security vulnerabilities
"""
import os
import subprocess

# Vulnerability 1: Command Injection
def execute_user_command(user_input):
    os.system(user_input)  # Dangerous! Command injection

# Vulnerability 2: SQL Injection
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return query

# Vulnerability 3: Hardcoded Credentials
API_KEY = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
AWS_SECRET = "AKIAIOSFODNN7EXAMPLE1234567890"
DATABASE_PASSWORD = "SuperSecret123!"

# Vulnerability 4: Using eval with user input
def calculate(expression):
    result = eval(expression)  # Dangerous!
    return result

# Vulnerability 5: Insecure deserialization
import pickle

def load_data(data):
    return pickle.loads(data)  # Dangerous!
