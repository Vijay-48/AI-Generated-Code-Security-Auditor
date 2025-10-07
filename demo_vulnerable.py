import os
def vulnerable_function(user_input):
    os.system(user_input)  # Command injection vulnerability
    
def sql_query(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection
    return query

API_KEY = "sk-1234567890abcdef"  # Hardcoded secret
