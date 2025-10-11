/**
 * Demo: Java Security Vulnerabilities
 * For hackathon demonstration
 */

import java.sql.*;
import java.io.*;
import java.security.MessageDigest;
import javax.servlet.http.*;

public class VulnerableJavaApp {
    
    // CRITICAL: SQL Injection
    public User vulnerableLogin(String username, String password) throws SQLException {
        Connection conn = DriverManager.getConnection("jdbc:mysql://localhost/mydb", "root", "password");
        Statement stmt = conn.createStatement();
        
        // CRITICAL: SQL Injection via string concatenation
        String query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'";
        ResultSet rs = stmt.executeQuery(query);
        
        if (rs.next()) {
            return new User(rs.getString("username"), rs.getString("email"));
        }
        return null;
    }
    
    // CRITICAL: Command Injection
    public void vulnerableExec(String filename) throws IOException {
        // CRITICAL: User input in Runtime.exec()
        Runtime.getRuntime().exec("cat " + filename);
    }
    
    // CRITICAL: Path Traversal
    public String vulnerableFileRead(String filename) throws IOException {
        // Attacker can use: ../../../../etc/passwd
        File file = new File("/var/www/uploads/" + filename);
        BufferedReader reader = new BufferedReader(new FileReader(file));
        
        StringBuilder content = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            content.append(line);
        }
        reader.close();
        return content.toString();
    }
    
    // CRITICAL: Hardcoded Credentials
    private static final String DB_PASSWORD = "admin123";
    private static final String API_KEY = "sk-1234567890abcdefghijklmnop";
    private static final String ENCRYPTION_KEY = "secretkey123";
    
    // CRITICAL: Weak Cryptography
    public String weakPasswordHash(String password) throws Exception {
        // MD5 is broken!
        MessageDigest md = MessageDigest.getInstance("MD5");
        byte[] hash = md.digest(password.getBytes());
        StringBuilder hexString = new StringBuilder();
        for (byte b : hash) {
            hexString.append(String.format("%02x", b));
        }
        return hexString.toString();
    }
    
    // CRITICAL: XSS Vulnerability
    public void vulnerableServlet(HttpServletRequest request, HttpServletResponse response) throws IOException {
        String username = request.getParameter("username");
        
        // CRITICAL: Unescaped output
        response.getWriter().write("<h1>Welcome " + username + "</h1>");
    }
    
    // CRITICAL: Insecure Deserialization
    public Object vulnerableDeserialize(InputStream input) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(input);
        // CRITICAL: Deserializing untrusted data
        return ois.readObject();
    }
    
    // CRITICAL: XXE Vulnerability
    public void vulnerableXMLParse(String xmlData) throws Exception {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        // CRITICAL: XXE not disabled
        DocumentBuilder builder = factory.newDocumentBuilder();
        Document doc = builder.parse(new ByteArrayInputStream(xmlData.getBytes()));
    }
    
    // CRITICAL: LDAP Injection
    public void vulnerableLDAPSearch(String username) throws Exception {
        DirContext ctx = new InitialDirContext();
        
        // CRITICAL: Unvalidated user input in LDAP filter
        String filter = "(uid=" + username + ")";
        ctx.search("ou=users,dc=example,dc=com", filter, new SearchControls());
    }
    
    // CRITICAL: Insecure Random
    public String generateSessionId() {
        // java.util.Random is NOT cryptographically secure!
        java.util.Random random = new java.util.Random();
        return String.valueOf(random.nextLong());
    }
    
    // Inner class for demonstration
    static class User {
        String username;
        String email;
        
        User(String username, String email) {
            this.username = username;
            this.email = email;
        }
    }
}
