import subprocess
import json
import tempfile
import os
import re
from typing import Dict, Any, List
from pathlib import Path

class SecurityScanner:
    def __init__(self):
        self.supported_languages = ['python', 'javascript', 'java', 'go']
        
        # Secret detection patterns
        self.secret_patterns = {
            'AWS_ACCESS_KEY': {
                'pattern': r'AKIA[0-9A-Z]{16}',
                'description': 'AWS Access Key ID detected',
                'severity': 'CRITICAL'
            },
            'AWS_SECRET_KEY': {
                'pattern': r'aws_secret_access_key\s*=\s*["\'][^"\']{20,}["\']',
                'description': 'AWS Secret Access Key detected',
                'severity': 'CRITICAL'
            },
            'PRIVATE_KEY': {
                'pattern': r'-----BEGIN\s+(RSA\s+)?PRIVATE KEY-----',
                'description': 'Private key detected in code',
                'severity': 'HIGH'
            },
            'HARDCODED_PASSWORD': {
                'pattern': r'(?i)(password|pwd|passwd)\s*[=:]\s*["\'][^"\']{8,}["\']',
                'description': 'Hardcoded password detected',
                'severity': 'HIGH'
            },
            'JWT_TOKEN': {
                'pattern': r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*',
                'description': 'JWT token detected in code',
                'severity': 'MEDIUM'
            },
            'API_KEY_GENERIC': {
                'pattern': r'(?i)(api[_-]?key|apikey|secret[_-]?key)\s*[=:]\s*["\'][^"\']{16,}["\']',
                'description': 'Generic API key pattern detected',
                'severity': 'HIGH'
            },
            'DATABASE_URL': {
                'pattern': r'(?i)(mongodb|mysql|postgres|redis)://[^/\s]+:[^/\s]+@[^\s]+',
                'description': 'Database connection string with credentials',
                'severity': 'HIGH'
            },
            'GITHUB_TOKEN': {
                'pattern': r'gh[pousr]_[A-Za-z0-9_]{36,255}',
                'description': 'GitHub token detected',
                'severity': 'HIGH'
            },
            'SLACK_TOKEN': {
                'pattern': r'xox[baprs]-([0-9a-zA-Z]{10,48})',
                'description': 'Slack token detected',
                'severity': 'MEDIUM'
            },
            'GOOGLE_API_KEY': {
                'pattern': r'AIza[0-9A-Za-z\\-_]{35}',
                'description': 'Google API key detected',
                'severity': 'HIGH'
            }
        }

    async def scan_code(self, code: str, language: str, filename: str = None) -> Dict[str, Any]:
        if language not in self.supported_languages:
            raise ValueError(f"Language {language} not supported")

        with tempfile.NamedTemporaryFile(mode='w', suffix=self._ext(language), delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        try:
            results = {}
            
            # Static analysis tools
            if language == 'python':
                results['bandit'] = await self._run_bandit(tmp_path)
                results['semgrep'] = await self._run_semgrep(tmp_path)
            else:
                results['semgrep'] = await self._run_semgrep(tmp_path)
            
            # Secret detection (for all languages)
            results['secrets'] = self._detect_secrets(code, filename or tmp_path)

            return self._normalize(results)
        finally:
            os.unlink(tmp_path)

    async def _run_bandit(self, file_path: str) -> Dict[str, Any]:
        try:
            cmd = ['/root/.venv/bin/bandit', '-f', 'json', file_path]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return json.loads(res.stdout) if res.stdout else {}
        except Exception as e:
            print(f"DEBUG: Bandit exception: {e}")
            return {"error": str(e)}

    async def _run_semgrep(self, file_path: str) -> Dict[str, Any]:
        try:
            cmd = ['/root/.venv/bin/semgrep', '--config=auto', '--json', '--timeout=30', file_path]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
            return json.loads(res.stdout) if res.stdout else {}
        except Exception as e:
            print(f"DEBUG: Semgrep exception: {e}")
            return {"error": str(e)}

    def _normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        norm = {
            "vulnerabilities": [],
            "summary": {"total": 0, "high": 0, "medium": 0, "low": 0, "critical": 0}
        }
        
        # Bandit results
        bandit = raw.get('bandit', {}).get('results', [])
        for issue in bandit:
            sev = issue.get('issue_severity', 'LOW').upper()
            norm["vulnerabilities"].append({
                "id": issue.get('test_id', ''),
                "title": issue.get('test_name', ''),
                "description": issue.get('issue_text', ''),
                "severity": sev,
                "confidence": issue.get('issue_confidence', ''),
                "line_number": issue.get('line_number', 0),
                "cwe_id": self._cwe_bandit(issue.get('test_id', '')),
                "tool": "bandit",
                "code_snippet": issue.get('code', '')
            })
            
        # Semgrep results
        sem = raw.get('semgrep', {}).get('results', [])
        for issue in sem:
            sev = issue.get('extra', {}).get('severity', 'INFO').upper()
            sev_map = {"ERROR": "HIGH","WARNING":"MEDIUM","INFO":"LOW"}.get(sev, "LOW")
            norm["vulnerabilities"].append({
                "id": issue.get('check_id', ''),
                "title": issue.get('message', ''),
                "description": issue.get('message', ''),
                "severity": sev_map,
                "line_number": issue.get('start', {}).get('line', 0),
                "cwe_id": self._cwe_semgrep(issue),
                "tool": "semgrep",
                "code_snippet": issue.get('extra', {}).get('lines', '')
            })
            
        # Secret detection results
        secrets = raw.get('secrets', [])
        for secret in secrets:
            norm["vulnerabilities"].append({
                "id": f"SECRET_{secret['type']}",
                "title": f"Secret Detected: {secret['type'].replace('_', ' ').title()}",
                "description": secret['description'],
                "severity": secret['severity'],
                "line_number": secret['line_number'],
                "cwe_id": "CWE-798",  # Use of Hard-coded Credentials
                "tool": "secrets",
                "code_snippet": secret['context']
            })
        
        # Calculate summary
        for v in norm["vulnerabilities"]:
            severity = v["severity"].lower()
            norm["summary"]["total"] += 1
            if severity in norm["summary"]:
                norm["summary"][severity] += 1
        
        return norm

    def _detect_secrets(self, code: str, filename: str) -> List[Dict[str, Any]]:
        """Detect secrets and sensitive information in code"""
        secrets = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for secret_type, config in self.secret_patterns.items():
                pattern = config['pattern']
                matches = re.finditer(pattern, line, re.IGNORECASE)
                
                for match in matches:
                    # Get context around the match
                    start_line = max(0, line_num - 2)
                    end_line = min(len(lines), line_num + 1)
                    context_lines = lines[start_line:end_line]
                    
                    secrets.append({
                        'type': secret_type,
                        'description': config['description'],
                        'severity': config['severity'],
                        'line_number': line_num,
                        'context': '\n'.join(f"{start_line + i + 1}: {line}" for i, line in enumerate(context_lines)),
                        'match': match.group(0)[:50] + "..." if len(match.group(0)) > 50 else match.group(0),
                        'filename': filename
                    })
        
        return secrets

    def _ext(self, lang: str) -> str:
        return { 'python':'.py','javascript':'.js','java':'.java','go':'.go' }.get(lang, '.txt')

    def _cwe_bandit(self, test_id: str) -> str:
        mapping = {
            'B101':'CWE-78','B108':'CWE-377','B110':'CWE-703','B608':'CWE-89'
        }
        return mapping.get(test_id, 'CWE-Unknown')

    def _cwe_semgrep(self, issue: Dict[str, Any]) -> str:
        cid = issue.get('check_id','').lower()
        if 'sql' in cid: return 'CWE-89'
        if 'xss' in cid: return 'CWE-79'
        return 'CWE-Unknown'
