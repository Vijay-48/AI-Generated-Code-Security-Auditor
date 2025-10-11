import pickle
import subprocess
import sys
import sqlite3
from flask import Flask, request

app = Flask(__name__)

# Hardcoded credentials (Security vulnerability)
DB_PASSWORD = "admin123"
API_KEY = "secret_key_123"

# Command injection vulnerability
def run_command(cmd):
    return subprocess.check_output(cmd, shell=True)  # Shell injection risk

# SQL injection vulnerability
def query_user(username):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE name = '{username}'"  # SQL injection
    cursor.execute(query)
    return cursor.fetchall()

# Insecure deserialization
def deserialize_data(data):
    return pickle.loads(data)  # Insecure deserialization

# Path traversal vulnerability
def read_file(path):
    with open(path, 'r') as f:  # Path traversal risk
        return f.read()

# Weak cryptographic function (MD5)
import hashlib
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()  # Weak hash

# XSS vulnerability (in web context)
@app.route('/search')
def search():
    query = request.args.get('q')
    return f"<p>Results for: {query}</p>"  # XSS vulnerability

# Buffer overflow simulation (Python is memory-safe, but this mimics the pattern)
def buffer_overflow():
    buffer = bytearray(10)
    data = bytearray(100)
    for i in range(len(data)):
        buffer[i] = data[i]  # Buffer overflow simulation
    return buffer

if __name__ == '__main__':
    # Test command injection
    run_command('ls')  # This is just for demonstration

    # Test SQL injection
    query_user("admin' OR 1=1 --")

    # Test deserialization (use a pickled object from a trusted source ONLY in tests)
    deserialize_data(b"cos\nsystem\n(S'echo hello'\ntR.")

    # Test path traversal
    read_file('../../etc/passwd')

    # Test weak hashing
    hash_password('password123')

    # Run Flask app (comment out if not testing web vulnerabilities)
    app.run(debug=True)  # Debug mode exposes sensitive data