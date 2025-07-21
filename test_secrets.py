import os
import boto3

# AWS credentials hardcoded (bad practice!)
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# Database connection with credentials
DATABASE_URL = "mongodb://admin:password123@localhost:27017/myapp"

# API key in code
api_key = "sk-1234567890abcdef1234567890abcdef12345678"

def connect_db():
    # Hardcoded password
    password = "super_secret_password123"
    return f"Connected with {password}"

# Private key (part of one)
private_key = '''-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA4f5wg5l2hKsTeNem/V41fGnJm6gOdrj8ym3rFkEjWT2btNjp
...
-----END RSA PRIVATE KEY-----'''