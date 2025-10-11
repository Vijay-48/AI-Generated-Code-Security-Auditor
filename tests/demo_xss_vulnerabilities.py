#!/usr/bin/env python3
"""
Demo: Cross-Site Scripting (XSS) Vulnerabilities
For hackathon demonstration
"""

from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route('/search')
def vulnerable_search():
    """CRITICAL: Reflected XSS vulnerability"""
    search_query = request.args.get('q', '')
    
    # CRITICAL: User input rendered without escaping
    html = f"""
    <html>
        <body>
            <h1>Search Results for: {search_query}</h1>
        </body>
    </html>
    """
    return html

@app.route('/comment', methods=['POST'])
def vulnerable_comment():
    """CRITICAL: Stored XSS vulnerability"""
    comment = request.form.get('comment', '')
    
    # CRITICAL: Storing unsanitized user input
    with open('comments.txt', 'a') as f:
        f.write(comment + '\n')
    
    return f"Comment saved: {comment}"

@app.route('/profile')
def vulnerable_profile():
    """CRITICAL: DOM-based XSS"""
    username = request.args.get('name', 'Guest')
    
    # CRITICAL: User input in JavaScript
    html = f"""
    <html>
        <script>
            var username = "{username}";
            document.write("Welcome " + username);
        </script>
    </html>
    """
    return html

def generate_unsafe_html(user_bio):
    """CRITICAL: HTML injection"""
    # CRITICAL: No sanitization of user input
    html_template = f"""
    <div class="user-bio">
        <p>{user_bio}</p>
    </div>
    """
    return html_template

# Example exploits:
# /search?q=<script>alert('XSS')</script>
# /profile?name=<img src=x onerror=alert('XSS')>
