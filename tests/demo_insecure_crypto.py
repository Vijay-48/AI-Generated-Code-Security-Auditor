#!/usr/bin/env python3
"""
Demo: Insecure Cryptography
For hackathon demonstration
"""

import hashlib
import random

def vulnerable_password_hash(password):
    """CRITICAL: Using MD5 for password hashing"""
    # MD5 is broken and should never be used for passwords
    return hashlib.md5(password.encode()).hexdigest()

def vulnerable_password_hash_sha1(password):
    """CRITICAL: Using SHA1 without salt"""
    # SHA1 is deprecated and no salt makes it vulnerable to rainbow tables
    return hashlib.sha1(password.encode()).hexdigest()

def weak_random_token():
    """CRITICAL: Using weak random number generator"""
    # random module is NOT cryptographically secure
    token = ''.join([str(random.randint(0, 9)) for _ in range(32)])
    return token

def insecure_session_id():
    """CRITICAL: Predictable session ID"""
    import time
    # Using timestamp makes session IDs predictable
    session_id = hashlib.md5(str(time.time()).encode()).hexdigest()
    return session_id

def weak_encryption_key():
    """CRITICAL: Hardcoded encryption key"""
    # Never hardcode encryption keys!
    ENCRYPTION_KEY = b'1234567890123456'  # 16 bytes, but predictable
    return ENCRYPTION_KEY

def vulnerable_random_password():
    """CRITICAL: Weak password generation"""
    # Using random instead of secrets module
    password = ''.join([chr(random.randint(65, 90)) for _ in range(8)])
    return password

class InsecureAuth:
    """CRITICAL: Multiple cryptographic failures"""
    
    def __init__(self):
        # CRITICAL: Weak secret key
        self.secret_key = "secret123"
    
    def create_token(self, user_id):
        """CRITICAL: Weak token generation"""
        # Predictable token based on user_id only
        return hashlib.md5(f"{user_id}{self.secret_key}".encode()).hexdigest()
    
    def verify_password(self, password, stored_hash):
        """CRITICAL: Timing attack vulnerability"""
        # Direct comparison allows timing attacks
        return hashlib.md5(password.encode()).hexdigest() == stored_hash

# Secure alternatives (commented out for demo):
# import secrets
# import bcrypt
# secure_token = secrets.token_urlsafe(32)
# hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
