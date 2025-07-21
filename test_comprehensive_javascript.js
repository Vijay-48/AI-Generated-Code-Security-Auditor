/**
 * Comprehensive JavaScript vulnerability test cases
 */

// 1. XSS VULNERABILITIES
function renderUserContent(userInput) {
    document.getElementById('content').innerHTML = userInput; // XSS
    document.write(userInput); // XSS
}

function unsafeJqueryHtml(data) {
    $('#content').html(data); // XSS via jQuery
}

// 2. CODE INJECTION
function evaluateUserCode(code) {
    eval(code); // Code injection
}

function functionConstructor(userCode) {
    var fn = new Function(userCode); // Code injection
    return fn();
}

function setTimeoutInjection(userCode) {
    setTimeout(userCode, 1000); // Code injection
}

// 3. PROTOTYPE POLLUTION
function mergeObjects(target, source) {
    for (let key in source) {
        target[key] = source[key]; // Prototype pollution vulnerability
    }
}

// 4. INSECURE RANDOMNESS
function generateToken() {
    return Math.random().toString(36); // Weak random generation
}

function generateSessionId() {
    return Math.floor(Math.random() * 1000000); // Weak session ID
}

// 5. HARDCODED SECRETS
const JWT_SECRET = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"; // JWT token
const STRIPE_SECRET_KEY = "sk_live_51234567890abcdef"; // Stripe key
const GITHUB_TOKEN = "ghp_1234567890abcdef1234567890abcdef12"; // GitHub token
const SLACK_WEBHOOK = "https://hooks.slack.com/services/T00/B00/XXXX"; // Webhook URL

// 6. REGEX DOS (ReDoS)
function vulnerableRegex(input) {
    const pattern = /^(a+)+$/; // Catastrophic backtracking
    return pattern.test(input);
}

// 7. INSECURE STORAGE
function storeCredentials(username, password) {
    localStorage.setItem('user', username);
    localStorage.setItem('pass', password); // Insecure storage
    sessionStorage.setItem('token', getAuthToken());
}

// 8. OPEN REDIRECT
function redirectUser(url) {
    window.location = url; // Open redirect
    window.location.href = url; // Open redirect
}

// 9. INSECURE COMMUNICATION
function makeInsecureRequest(data) {
    fetch('http://api.example.com/data', { // HTTP instead of HTTPS
        method: 'POST',
        body: JSON.stringify(data)
    });
}

// 10. TEMPLATE INJECTION (Client-side)
function renderTemplate(template, data) {
    return template.replace(/{{(\w+)}}/g, (match, key) => {
        return data[key]; // Potential template injection
    });
}

// 11. INSECURE DESERIALIZATION
function parseUntrustedJSON(jsonString) {
    return JSON.parse(jsonString); // If from untrusted source
}

// 12. CLICKJACKING VULNERABILITY  
function createFrame(url) {
    const frame = document.createElement('iframe');
    frame.src = url; // Potential clickjacking if X-Frame-Options not set
    document.body.appendChild(frame);
}