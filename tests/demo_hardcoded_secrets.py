#!/usr/bin/env python3
"""
Demo: Hardcoded Secrets & Credentials
For hackathon demonstration
"""

import requests

# CRITICAL: Hardcoded API keys
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# CRITICAL: Hardcoded database credentials
DB_HOST = "prod-db.company.com"
DB_USER = "admin"
DB_PASSWORD = "P@ssw0rd123!"  # Never hardcode passwords!
DB_NAME = "production_db"

# CRITICAL: Hardcoded API tokens
GITHUB_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
STRIPE_SECRET_KEY = "sk_live_1234567890abcdefghijklmnopqrstuv"
OPENAI_API_KEY = "sk-proj-abcdefghijklmnopqrstuvwxyz1234567890"

def connect_to_database():
    """Vulnerable database connection"""
    import psycopg2
    
    # CRITICAL: Credentials in code
    conn = psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    return conn

def upload_to_s3(file_path):
    """Vulnerable S3 upload"""
    import boto3
    
    # CRITICAL: AWS keys in code
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )
    s3_client.upload_file(file_path, 'my-bucket', 'file.txt')

def make_payment(amount):
    """Vulnerable payment processing"""
    # CRITICAL: Stripe key exposed
    response = requests.post(
        'https://api.stripe.com/v1/charges',
        headers={'Authorization': f'Bearer {STRIPE_SECRET_KEY}'},
        data={'amount': amount, 'currency': 'usd'}
    )
    return response.json()

# CRITICAL: Private key in code
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA1234567890abcdefghijklmnopqrstuvwxyz...
-----END RSA PRIVATE KEY-----"""

# CRITICAL: JWT secret
JWT_SECRET = "super-secret-key-12345"
