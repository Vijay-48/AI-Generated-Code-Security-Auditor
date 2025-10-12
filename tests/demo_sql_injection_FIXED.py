#!/usr/bin/env python3
"""
Demo: SQL Injection Vulnerabilities - FIXED VERSION
All vulnerabilities have been remediated with secure coding practices
"""

import sqlite3

def secure_login(username, password):
    """✅ SECURE: Uses parameterized queries to prevent SQL injection"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # ✅ SECURE: Using parameterized queries with placeholders
    query = "SELECT * FROM users WHERE username=? AND password=?"
    cursor.execute(query, (username, password))
    
    user = cursor.fetchone()
    conn.close()
    return user

def secure_search(search_term):
    """✅ SECURE: Uses parameterized queries for search"""
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    
    # ✅ SECURE: Parameterized query with LIKE operator
    query = "SELECT * FROM products WHERE name LIKE ?"
    cursor.execute(query, (f'%{search_term}%',))
    
    results = cursor.fetchall()
    conn.close()
    return results

def secure_delete(user_id):
    """✅ SECURE: Uses parameterized queries for DELETE"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # ✅ SECURE: Parameterized DELETE statement
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    
    conn.commit()
    conn.close()

# Security improvements applied:
# 1. All SQL queries use parameterized placeholders (?)
# 2. User input is passed as tuple parameters
# 3. Database driver properly escapes special characters
# 4. Prevents SQL injection attacks completely
#
# Example: Even malicious input like "admin' OR '1'='1" 
# will be treated as a literal string, not SQL code
