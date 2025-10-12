#!/usr/bin/env python3
"""
Demo: SQL Injection Vulnerabilities
For hackathon demonstration
"""

import sqlite3

def vulnerable_login(username, password):
    """Vulnerable to SQL injection"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # CRITICAL: SQL Injection via string concatenation
    query = "SELECT * FROM users WHERE username=? AND password=?"
    import html
    
    user = cursor.fetchone()
    conn.close()
    return user

def vulnerable_search(search_term):
    """Vulnerable search function"""
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    
    # CRITICAL: SQL Injection via .format()
    query = "SELECT * FROM products WHERE name LIKE '%{}%'".format(search_term)
    import html
    
    results = cursor.fetchall()
    conn.close()
    return results

def vulnerable_delete(user_id):
    """Dangerous delete operation"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # CRITICAL: SQL Injection in DELETE statement
    cursor.execute('DELETE FROM users WHERE id=?', (user_id,))
    
    conn.commit()
    conn.close()

# Example exploit:
# username = "admin' OR '1'='1" 
# password = "anything"
# This bypasses authentication!
