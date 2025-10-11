#!/usr/bin/env node
/**
 * Demo: JavaScript Security Vulnerabilities
 * For hackathon demonstration
 */

// CRITICAL: SQL Injection in Node.js
function vulnerableLogin(username, password) {
    const mysql = require('mysql');
    const connection = mysql.createConnection({
        host: 'localhost',
        user: 'root',
        password: 'password',
        database: 'users'
    });
    
    // CRITICAL: SQL Injection via string concatenation
    const query = `SELECT * FROM users WHERE username='${username}' AND password='${password}'`;
    connection.query(query, (err, results) => {
        console.log(results);
    });
}

// CRITICAL: Command Injection
function vulnerableExec(userInput) {
    const { exec } = require('child_process');
    
    // CRITICAL: User input directly in command
    exec(`ping -c 4 ${userInput}`, (error, stdout, stderr) => {
        console.log(stdout);
    });
}

// CRITICAL: XSS Vulnerability
function vulnerableRender(username) {
    const express = require('express');
    const app = express();
    
    app.get('/profile', (req, res) => {
        // CRITICAL: Unescaped user input in HTML
        res.send(`<h1>Welcome ${username}</h1>`);
    });
}

// CRITICAL: Hardcoded Credentials
const DB_PASSWORD = 'admin123';
const API_KEY = 'sk-1234567890abcdefghijklmnop';
const JWT_SECRET = 'my-secret-key';

// CRITICAL: Insecure Crypto
function weakPasswordHash(password) {
    const crypto = require('crypto');
    // MD5 is broken!
    return crypto.createHash('md5').update(password).digest('hex');
}

// CRITICAL: Path Traversal
function vulnerableFileRead(filename) {
    const fs = require('fs');
    // Attacker can use: ../../../../etc/passwd
    const content = fs.readFileSync(`/var/www/uploads/${filename}`, 'utf8');
    return content;
}

// CRITICAL: Prototype Pollution
function vulnerableMerge(target, source) {
    for (let key in source) {
        // CRITICAL: No check for __proto__ or constructor
        target[key] = source[key];
    }
    return target;
}

// CRITICAL: NoSQL Injection
function vulnerableMongoQuery(userId) {
    const MongoClient = require('mongodb').MongoClient;
    
    MongoClient.connect('mongodb://localhost:27017', (err, client) => {
        const db = client.db('myapp');
        // CRITICAL: Direct user input in query
        db.collection('users').find({ userId: userId }).toArray();
    });
}

// CRITICAL: Insecure Random
function generateSessionId() {
    // Math.random() is NOT cryptographically secure!
    return Math.random().toString(36).substring(2);
}

// CRITICAL: eval() usage
function vulnerableCalculator(expression) {
    // CRITICAL: eval with user input
    return eval(expression);
}

// CRITICAL: SSRF Vulnerability
function vulnerableFetch(url) {
    const fetch = require('node-fetch');
    // CRITICAL: No URL validation
    fetch(url).then(res => res.text()).then(body => console.log(body));
}

module.exports = {
    vulnerableLogin,
    vulnerableExec,
    vulnerableRender,
    weakPasswordHash,
    vulnerableFileRead
};
