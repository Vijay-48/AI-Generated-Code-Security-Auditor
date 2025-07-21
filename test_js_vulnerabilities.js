/* JavaScript test file with XSS and other vulnerabilities */

// 1. XSS Vulnerability 
function renderUserContent(userInput) {
    document.getElementById('content').innerHTML = userInput; // XSS vulnerability
}

// 2. Dangerous eval usage
function executeUserCode(code) {
    eval(code); // Code injection vulnerability
}

// 3. Hardcoded JWT token
const JWT_SECRET = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U";

// 4. localStorage with sensitive data
function storeCredentials(username, password) {
    localStorage.setItem('credentials', JSON.stringify({
        user: username,
        pass: password  // Storing password in localStorage
    }));
}

// 5. Unsafe redirect
function redirectUser(url) {
    window.location = url; // Open redirect vulnerability
}