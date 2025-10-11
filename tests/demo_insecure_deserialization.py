#!/usr/bin/env python3
"""
Demo: Insecure Deserialization & Code Injection
For hackathon demonstration
"""

import pickle
import yaml
import json

def vulnerable_pickle_load(data):
    """CRITICAL: Unsafe pickle deserialization"""
    # Pickle can execute arbitrary code during deserialization
    obj = pickle.loads(data)
    return obj

def vulnerable_eval(user_input):
    """CRITICAL: Using eval() on user input"""
    # Attacker can execute arbitrary Python code
    result = eval(user_input)
    return result

def vulnerable_exec(code_string):
    """CRITICAL: Using exec() on user input"""
    # Allows execution of arbitrary Python code
    exec(code_string)

def vulnerable_yaml_load(yaml_data):
    """CRITICAL: Unsafe YAML loading"""
    # yaml.load() can execute arbitrary Python code
    config = yaml.load(yaml_data, Loader=yaml.Loader)
    return config

def vulnerable_compile(source_code):
    """CRITICAL: Compiling and executing user code"""
    # Compiling user input is dangerous
    code_obj = compile(source_code, '<string>', 'exec')
    exec(code_obj)

def vulnerable_import(module_name):
    """CRITICAL: Dynamic import of user-specified modules"""
    # Attacker can import malicious modules
    module = __import__(module_name)
    return module

class VulnerableSession:
    """CRITICAL: Insecure session handling"""
    
    def save_session(self, session_data):
        """Save session using pickle"""
        with open('session.pkl', 'wb') as f:
            pickle.dump(session_data, f)
    
    def load_session(self):
        """CRITICAL: Load session from pickle"""
        with open('session.pkl', 'rb') as f:
            # Vulnerable to deserialization attacks
            return pickle.load(f)

def vulnerable_calculator(expression):
    """CRITICAL: Calculator using eval"""
    # Attacker can inject: __import__('os').system('rm -rf /')
    result = eval(expression)
    return result

# Example exploits:
# vulnerable_eval("__import__('os').system('whoami')")
# vulnerable_exec("import os; os.system('cat /etc/passwd')")
