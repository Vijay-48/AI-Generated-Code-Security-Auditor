<<<<<<< HEAD
import subprocess
import json
import tempfile
import os
from typing import Dict, Any

class SecurityScanner:
    def __init__(self):
        self.supported_languages = ['python', 'javascript', 'java', 'go']

    async def scan_code(self, code: str, language: str) -> Dict[str, Any]:
        if language not in self.supported_languages:
            raise ValueError(f"Language {language} not supported")

        with tempfile.NamedTemporaryFile(mode='w', suffix=self._get_file_extension(language), delete=False) as tmp_file:
            tmp_file.write(code)
            tmp_file_path = tmp_file.name

        try:
            results = {}
            if language == 'python':
                results['bandit'] = await self._run_bandit(tmp_file_path)
            results['semgrep'] = await self._run_semgrep(tmp_file_path, language)
            return self._normalize_results(results)
        finally:
            os.unlink(tmp_file_path)

    async def _run_bandit(self, file_path: str) -> Dict[str, Any]:
        try:
            cmd = ['bandit', '-f', 'json', file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode in [0, 1]:
                return json.loads(result.stdout) if result.stdout else {}
            return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}

    async def _run_semgrep(self, file_path: str, language: str) -> Dict[str, Any]:
        try:
            cmd = ['semgrep', '--config=auto', '--json', file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
            if result.returncode in [0, 1]:
                return json.loads(result.stdout) if result.stdout else {}
            return {"error": result.stderr}
        except Exception as e:
            return {"error": str(e)}

    def _normalize_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        normalized = {
            "vulnerabilities": [],
            "summary": {
                "total_issues": 0,
                "high_severity": 0,
                "medium_severity": 0,
                "low_severity": 0
            }
        }

        # Process Bandit results
        if 'bandit' in raw_results and 'results' in raw_results['bandit']:
            for issue in raw_results['bandit']['results']:
                vuln = {
                    "id": issue.get('test_id', ''),
                    "title": issue.get('test_name', ''),
                    "description": issue.get('issue_text', ''),
                    "severity": issue.get('issue_severity', 'LOW').upper(),
                    "line_number": issue.get('line_number', 0),
                    "cwe_id": self._extract_cwe(issue),
                    "tool": "bandit",
                    "code_snippet": issue.get('code', '')
                }
                normalized["vulnerabilities"].append(vuln)

        # Process Semgrep results
        if 'semgrep' in raw_results and 'results' in raw_results['semgrep']:
            for issue in raw_results['semgrep']['results']:
                severity = issue.get('extra', {}).get('severity', 'INFO').upper()
                severity_map = {"ERROR": "HIGH", "WARNING": "MEDIUM", "INFO": "LOW"}
                
                vuln = {
                    "id": issue.get('check_id', ''),
                    "title": issue.get('message', ''),
                    "description": issue.get('message', ''),
                    "severity": severity_map.get(severity, "LOW"),
                    "line_number": issue.get('start', {}).get('line', 0),
                    "cwe_id": self._extract_cwe(issue),
                    "tool": "semgrep",
                    "code_snippet": issue.get('extra', {}).get('lines', '')
                }
                normalized["vulnerabilities"].append(vuln)

        # Update summary
        for vuln in normalized["vulnerabilities"]:
            normalized["summary"]["total_issues"] += 1
            if vuln["severity"] == "HIGH":
                normalized["summary"]["high_severity"] += 1
            elif vuln["severity"] == "MEDIUM":
                normalized["summary"]["medium_severity"] += 1
            else:
                normalized["summary"]["low_severity"] += 1

        return normalized

    def _get_file_extension(self, language: str) -> str:
        return {
            'python': '.py',
            'javascript': '.js',
            'java': '.java',
            'go': '.go'
        }.get(language, '.txt')

    def _extract_cwe(self, issue: Dict) -> str:
        # Simplified CWE extraction
        if 'metadata' in issue.get('extra', {}):
            if 'cwe' in issue['extra']['metadata']:
                return f"CWE-{issue['extra']['metadata']['cwe']}"
        
        # Fallback based on ID
        issue_id = issue.get('test_id') or issue.get('check_id', '').lower()
        if 'sql' in issue_id or 'sqli' in issue_id:
            return 'CWE-89'
        elif 'xss' in issue_id:
            return 'CWE-79'
        elif 'command' in issue_id or 'injection' in issue_id:
            return 'CWE-78'
        return 'CWE-Unknown'
=======
import subprocess
import json
import tempfile
import os
from typing import Dict, Any
from pathlib import Path

class SecurityScanner:
    def __init__(self):
        self.supported_languages = ['python', 'javascript', 'java', 'go']

    async def scan_code(self, code: str, language: str, filename: str = None) -> Dict[str, Any]:
        if language not in self.supported_languages:
            raise ValueError(f"Language {language} not supported")

        with tempfile.NamedTemporaryFile(mode='w', suffix=self._ext(language), delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        try:
            results = {}
            if language == 'python':
                results['bandit'] = await self._run_bandit(tmp_path)
                results['semgrep'] = await self._run_semgrep(tmp_path)
            else:
                results['semgrep'] = await self._run_semgrep(tmp_path)

            return self._normalize(results)
        finally:
            os.unlink(tmp_path)

    async def _run_bandit(self, file_path: str) -> Dict[str, Any]:
        try:
            cmd = ['bandit', '-f', 'json', file_path]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return json.loads(res.stdout) if res.stdout else {}
        except Exception as e:
            return {"error": str(e)}

    async def _run_semgrep(self, file_path: str) -> Dict[str, Any]:
        try:
            cmd = ['semgrep', '--config=auto', '--json', '--timeout=30', file_path]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
            return json.loads(res.stdout) if res.stdout else {}
        except Exception as e:
            return {"error": str(e)}

    def _normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        norm = {
            "vulnerabilities": [],
            "summary": {"total": 0, "high": 0, "medium": 0, "low": 0}
        }
        # Bandit
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
        # Semgrep
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
        # summary
        for v in norm["vulnerabilities"]:
            norm["summary"]["total"] += 1
            norm["summary"][v["severity"].lower()] += 1
        return norm

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
>>>>>>> 6beaaa9d992e786be91fc4cc04bf2dff00a41321
