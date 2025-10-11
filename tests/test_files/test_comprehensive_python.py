"""
Comprehensive Python vulnerability test cases for regression testing
"""
import os
import subprocess
import sqlite3
import pickle
import yaml
import xml.etree.ElementTree as ET
import hashlib
import random
import tempfile

# 1. COMMAND INJECTION VARIATIONS
def command_injection_os_system(user_input):
    os.system(f"ls {user_input}")  # B605 - High

def command_injection_subprocess_shell(filename):
    subprocess.call(f"cat {filename}", shell=True)  # B602 - High
    
def command_injection_subprocess_list(cmd_parts):
    subprocess.Popen(["/bin/sh", "-c", cmd_parts])  # B604 - Medium

# 2. SQL INJECTION VARIATIONS  
def sql_injection_format_string(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"  # B608 - Medium
    return query

def sql_injection_percent_format(table_name):
    query = "SELECT * FROM %s WHERE active = 1" % table_name  # B608 - Medium
    return query

# 3. DESERIALIZATION VULNERABILITIES
def unsafe_pickle_load(data):
    return pickle.loads(data)  # B301 - High

def unsafe_yaml_load(yaml_string):
    return yaml.load(yaml_string)  # B506 - High

# 4. XML VULNERABILITIES
def xml_external_entity(xml_data):
    parser = ET.XMLParser()  # B314 - Medium
    return ET.fromstring(xml_data, parser)

# 5. CRYPTOGRAPHIC ISSUES
def weak_random_generator():
    return random.random()  # B311 - Low

def weak_hash_md5(password):
    return hashlib.md5(password.encode()).hexdigest()  # B303 - Medium

def weak_hash_sha1(data):
    return hashlib.sha1(data.encode()).hexdigest()  # B303 - Medium

# 6. FILE HANDLING VULNERABILITIES
def insecure_temp_file():
    return tempfile.mktemp()  # B306 - Medium

def path_traversal_vulnerability(filename):
    with open(f"/var/log/{filename}", 'r') as f:  # Potential path traversal
        return f.read()

# 7. HARDCODED SECRETS (Multiple patterns)
DATABASE_PASSWORD = "super_secret_password_123"  # Secret detection
API_TOKEN = "token_abcd1234567890efgh"  # Secret detection
PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7VJTUt9Us8cKB
-----END PRIVATE KEY-----"""  # Secret detection

# 8. ASSERT STATEMENTS IN PRODUCTION
def production_assert(user_role):
    assert user_role == "admin", "Access denied"  # B101 - Low

# 9. TRY-EXCEPT PASS (Silent failure)  
def silent_exception_handling():
    try:
        risky_operation()
    except:
        pass  # B110 - Low

def risky_operation():
    raise ValueError("Something went wrong")

# 10. EVAL AND EXEC USAGE
def dangerous_eval(user_code):
    return eval(user_code)  # B307 - High

def dangerous_exec(user_script):
    exec(user_script)  # B102 - Medium