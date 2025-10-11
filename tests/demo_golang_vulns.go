// Demo: Go Security Vulnerabilities
// For hackathon demonstration

package main

import (
	"crypto/md5"
	"database/sql"
	"fmt"
	"io/ioutil"
	"math/rand"
	"net/http"
	"os"
	"os/exec"
)

// CRITICAL: Hardcoded Credentials
const (
	DBPassword     = "admin123"
	APIKey         = "sk-1234567890abcdefghijklmnop"
	JWTSecret      = "my-secret-key"
	AWSAccessKey   = "AKIAIOSFODNN7EXAMPLE"
	AWSSecretKey   = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
)

// CRITICAL: SQL Injection
func vulnerableLogin(db *sql.DB, username, password string) (*User, error) {
	// CRITICAL: SQL injection via string concatenation
	query := fmt.Sprintf("SELECT * FROM users WHERE username='%s' AND password='%s'", username, password)
	
	row := db.QueryRow(query)
	var user User
	err := row.Scan(&user.ID, &user.Username, &user.Email)
	return &user, err
}

// CRITICAL: Command Injection
func vulnerableExec(filename string) error {
	// CRITICAL: User input in command execution
	cmd := exec.Command("sh", "-c", "cat "+filename)
	return cmd.Run()
}

// CRITICAL: Path Traversal
func vulnerableFileRead(filename string) (string, error) {
	// Attacker can use: ../../../../etc/passwd
	path := "/var/www/uploads/" + filename
	content, err := ioutil.ReadFile(path)
	return string(content), err
}

// CRITICAL: Weak Cryptography
func weakPasswordHash(password string) string {
	// MD5 is broken!
	hash := md5.Sum([]byte(password))
	return fmt.Sprintf("%x", hash)
}

// CRITICAL: XSS Vulnerability
func vulnerableHandler(w http.ResponseWriter, r *http.Request) {
	username := r.URL.Query().Get("username")
	
	// CRITICAL: Unescaped output
	fmt.Fprintf(w, "<h1>Welcome %s</h1>", username)
}

// CRITICAL: Insecure Random
func generateSessionID() string {
	// rand.Int() is NOT cryptographically secure!
	return fmt.Sprintf("%d", rand.Int())
}

// CRITICAL: SSRF Vulnerability
func vulnerableFetch(url string) (string, error) {
	// CRITICAL: No URL validation
	resp, err := http.Get(url)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	
	body, err := ioutil.ReadAll(resp.Body)
	return string(body), err
}

// CRITICAL: Environment Variable Exposure
func vulnerableEnvExpose() map[string]string {
	// CRITICAL: Exposing all environment variables
	envVars := make(map[string]string)
	for _, env := range os.Environ() {
		envVars[env] = os.Getenv(env)
	}
	return envVars
}

// CRITICAL: Hardcoded Database Connection
func connectToDatabase() (*sql.DB, error) {
	// CRITICAL: Hardcoded credentials
	connStr := "user=admin password=admin123 dbname=production host=prod-db.company.com"
	return sql.Open("postgres", connStr)
}

// User struct
type User struct {
	ID       int
	Username string
	Email    string
}

func main() {
	fmt.Println("Vulnerable Go Application - For Security Testing Only")
}
