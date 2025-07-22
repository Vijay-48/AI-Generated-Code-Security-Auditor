"""
Export formatters for CLI output
Supports CSV, JSON, SARIF, and other export formats for analytics data
"""
import csv
import json
import yaml
from datetime import datetime
from io import StringIO
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.models.analytics import (
    ScanHistoryEntry, ScanSummary, TrendDataPoint, 
    HeatmapEntry, RepositoryStats
)


class ExportFormatter:
    """Base class for export formatters"""
    
    @staticmethod
    def get_formatter(format_type: str):
        """Factory method to get appropriate formatter"""
        formatters = {
            'csv': CSVFormatter(),
            'json': JSONFormatter(),
            'yaml': YAMLFormatter(),
            'sarif': SARIFFormatter(),
            'table': TableFormatter()
        }
        return formatters.get(format_type.lower(), TableFormatter())


class CSVFormatter(ExportFormatter):
    """CSV export formatter"""
    
    def format_scan_history(self, history: List[ScanHistoryEntry]) -> str:
        """Format scan history as CSV"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow([
            'scan_id', 'timestamp', 'repository', 'total_issues', 
            'security_score', 'scan_type', 'duration', 'top_issues'
        ])
        
        # Data rows
        for entry in history:
            writer.writerow([
                entry.scan_id,
                entry.timestamp.isoformat(),
                entry.repository or '',
                entry.total_issues,
                entry.security_score,
                entry.scan_type,
                entry.duration or 0,
                '; '.join(entry.top_issues)
            ])
        
        return output.getvalue()
    
    def format_trends(self, trends: List[TrendDataPoint]) -> str:
        """Format trend data as CSV"""
        output = StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            'date', 'total_scans', 'total_vulnerabilities', 
            'critical', 'high', 'medium', 'low'
        ])
        
        for trend in trends:
            writer.writerow([
                trend.date,
                trend.total_scans,
                trend.total_vulnerabilities,
                trend.critical,
                trend.high,
                trend.medium,
                trend.low
            ])
        
        return output.getvalue()
    
    def format_heatmap(self, heatmap: List[HeatmapEntry]) -> str:
        """Format heatmap data as CSV"""
        output = StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['path', 'rule_hits', 'severity_score', 'files_count'])
        
        for entry in heatmap:
            writer.writerow([
                entry.path,
                entry.rule_hits,
                entry.severity_score,
                entry.files_count
            ])
        
        return output.getvalue()
    
    def format_repositories(self, repos: List[RepositoryStats]) -> str:
        """Format repository stats as CSV"""
        output = StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            'repository_url', 'repository_name', 'security_score',
            'total_vulnerabilities', 'total_scans', 'total_files',
            'last_scan_date', 'avg_scan_duration', 'branch'
        ])
        
        for repo in repos:
            writer.writerow([
                repo.repository_url,
                repo.repository_name,
                repo.security_score,
                repo.total_vulnerabilities,
                repo.total_scans,
                repo.total_files,
                repo.last_scan_date.isoformat() if repo.last_scan_date else '',
                repo.avg_scan_duration,
                repo.branch
            ])
        
        return output.getvalue()


class JSONFormatter(ExportFormatter):
    """JSON export formatter"""
    
    def format_scan_history(self, history: List[ScanHistoryEntry]) -> str:
        """Format scan history as JSON"""
        return json.dumps([entry.model_dump() for entry in history], indent=2, default=str)
    
    def format_trends(self, trends: List[TrendDataPoint]) -> str:
        """Format trend data as JSON"""
        return json.dumps([trend.model_dump() for trend in trends], indent=2, default=str)
    
    def format_heatmap(self, heatmap: List[HeatmapEntry]) -> str:
        """Format heatmap data as JSON"""
        return json.dumps([entry.model_dump() for entry in heatmap], indent=2, default=str)
    
    def format_repositories(self, repos: List[RepositoryStats]) -> str:
        """Format repository stats as JSON"""
        return json.dumps([repo.model_dump() for repo in repos], indent=2, default=str)
    
    def format_summary(self, summary: ScanSummary) -> str:
        """Format scan summary as JSON"""
        return json.dumps(summary.model_dump(), indent=2, default=str)


class YAMLFormatter(ExportFormatter):
    """YAML export formatter"""
    
    def format_scan_history(self, history: List[ScanHistoryEntry]) -> str:
        """Format scan history as YAML"""
        data = [entry.model_dump() for entry in history]
        return yaml.dump(data, default_flow_style=False, sort_keys=False)
    
    def format_summary(self, summary: ScanSummary) -> str:
        """Format scan summary as YAML"""
        return yaml.dump(summary.model_dump(), default_flow_style=False, sort_keys=False)


class SARIFFormatter(ExportFormatter):
    """SARIF (Static Analysis Results Interchange Format) formatter"""
    
    def format_scan_history(self, history: List[ScanHistoryEntry]) -> str:
        """Format scan history as SARIF"""
        sarif = {
            "version": "2.1.0",
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "runs": []
        }
        
        for entry in history:
            run = {
                "tool": {
                    "driver": {
                        "name": "AI Code Security Auditor",
                        "version": "2.0.0",
                        "informationUri": "https://github.com/your-repo/ai-code-auditor"
                    }
                },
                "invocations": [{
                    "startTimeUtc": entry.timestamp.isoformat(),
                    "executionSuccessful": True
                }],
                "properties": {
                    "scan_id": entry.scan_id,
                    "security_score": entry.security_score,
                    "scan_type": entry.scan_type,
                    "repository": entry.repository
                },
                "results": []
            }
            
            # Add placeholder results based on top issues
            for i, issue in enumerate(entry.top_issues[:3]):
                result = {
                    "ruleId": issue,
                    "level": "warning",
                    "message": {
                        "text": f"Security issue detected: {issue}"
                    },
                    "locations": [{
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": entry.repository or "unknown"
                            },
                            "region": {
                                "startLine": 1
                            }
                        }
                    }]
                }
                run["results"].append(result)
            
            sarif["runs"].append(run)
        
        return json.dumps(sarif, indent=2)


class TableFormatter(ExportFormatter):
    """Enhanced table formatter with colors"""
    
    def __init__(self):
        try:
            from colorama import Fore, Style, init
            init()
            self.colors = {
                'critical': Fore.RED,
                'high': Fore.MAGENTA,
                'medium': Fore.YELLOW,
                'low': Fore.GREEN,
                'info': Fore.BLUE,
                'reset': Style.RESET_ALL,
                'bold': Style.BRIGHT,
                'dim': Style.DIM
            }
            self.colorize = True
        except ImportError:
            self.colors = {key: '' for key in ['critical', 'high', 'medium', 'low', 'info', 'reset', 'bold', 'dim']}
            self.colorize = False
    
    def colorize_severity(self, text: str, severity: str) -> str:
        """Colorize text based on severity"""
        if not self.colorize:
            return text
        
        color = self.colors.get(severity.lower(), '')
        return f"{color}{text}{self.colors['reset']}"
    
    def colorize_score(self, score: float) -> str:
        """Colorize security score"""
        if not self.colorize:
            return f"{score:.1f}"
        
        if score >= 90:
            color = self.colors['low']  # Green
        elif score >= 70:
            color = self.colors['medium']  # Yellow
        elif score >= 50:
            color = self.colors['high']  # Magenta
        else:
            color = self.colors['critical']  # Red
        
        return f"{color}{score:.1f}{self.colors['reset']}"
    
    def format_scan_history(self, history: List[ScanHistoryEntry], show_colors: bool = True) -> str:
        """Format scan history as colorized table"""
        if not history:
            return "No scan history found."
        
        lines = []
        header = f"📋 Scan History (Last {len(history)} scans)"
        lines.append(header)
        lines.append("=" * max(80, len(header)))
        
        # Table header
        header_row = f"{'Date':<12} {'Score':<8} {'Issues':<7} {'Type':<12} {'Top Issues':<30}"
        lines.append(header_row)
        lines.append("-" * len(header_row))
        
        # Table rows
        for entry in history:
            date_str = entry.timestamp.strftime('%Y-%m-%d')
            score_str = self.colorize_score(entry.security_score) if show_colors else f"{entry.security_score:.1f}"
            issues_str = str(entry.total_issues)
            type_str = entry.scan_type
            top_issues_str = ", ".join(entry.top_issues[:3])[:30]
            
            lines.append(f"{date_str:<12} {score_str:<8} {issues_str:<7} {type_str:<12} {top_issues_str:<30}")
        
        return "\n".join(lines)
    
    def format_summary(self, summary: ScanSummary, show_colors: bool = True) -> str:
        """Format scan summary with colors"""
        lines = []
        lines.append("🔍 Scan Summary")
        lines.append("=" * 50)
        lines.append(f"Scan ID: {summary.scan_id}")
        lines.append(f"Timestamp: {summary.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if summary.repository:
            lines.append(f"Repository: {summary.repository}")
            
        lines.append(f"Files Scanned: {summary.files_scanned}")
        
        if summary.scan_duration:
            lines.append(f"Duration: {summary.scan_duration:.2f}s")
        
        lines.append(f"\n📊 Security Overview")
        score_display = self.colorize_score(summary.security_score) if show_colors else f"{summary.security_score:.1f}"
        lines.append(f"Overall Score: {score_display}/100")
        lines.append(f"Total Issues: {summary.total_issues}")
        
        if show_colors:
            lines.append(f"  {self.colorize_severity('🔴 Critical', 'critical')}: {summary.critical_count}")
            lines.append(f"  {self.colorize_severity('🟠 High', 'high')}: {summary.high_count}")
            lines.append(f"  {self.colorize_severity('🟡 Medium', 'medium')}: {summary.medium_count}")
            lines.append(f"  {self.colorize_severity('🟢 Low', 'low')}: {summary.low_count}")
        else:
            lines.append(f"  🔴 Critical: {summary.critical_count}")
            lines.append(f"  🟠 High: {summary.high_count}")
            lines.append(f"  🟡 Medium: {summary.medium_count}")
            lines.append(f"  🟢 Low: {summary.low_count}")
        
        if summary.languages:
            lines.append(f"Languages: {', '.join(summary.languages)}")
        
        if summary.top_rules:
            lines.append(f"\n🎯 Top Security Issues")
            for i, rule in enumerate(summary.top_rules[:5], 1):
                severity_display = self.colorize_severity(rule['severity'], rule['severity']) if show_colors else rule['severity']
                lines.append(f"  {i}. {rule['rule_name']} ({severity_display}) - {rule['hits']} hits")
        
        return "\n".join(lines)


def save_to_file(content: str, filename: str, format_type: str) -> bool:
    """Save formatted content to file"""
    try:
        file_path = Path(filename)
        
        # Ensure the file has the correct extension
        if not file_path.suffix:
            extensions = {
                'csv': '.csv',
                'json': '.json',
                'yaml': '.yml',
                'sarif': '.sarif'
            }
            file_path = file_path.with_suffix(extensions.get(format_type, '.txt'))
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"❌ Error saving to file: {e}")
        return False


def get_config_dir() -> Path:
    """Get the configuration directory for AI Auditor"""
    config_dir = Path.home() / '.ai_auditor'
    config_dir.mkdir(exist_ok=True)
    return config_dir


def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file"""
    config_file = get_config_dir() / 'config.yml'
    
    default_config = {
        'output': {
            'format': 'table',
            'colors': True,
            'progress_bars': True
        },
        'limits': {
            'history': 20,
            'trends_days': 30,
            'heatmap_width': 50
        },
        'filters': {
            'min_score': None,
            'severity': None
        }
    }
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                user_config = yaml.safe_load(f)
                # Merge with defaults
                default_config.update(user_config or {})
        except Exception as e:
            print(f"⚠️ Error loading config: {e}")
    
    return default_config


def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to YAML file"""
    config_file = get_config_dir() / 'config.yml'
    
    try:
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        return True
    except Exception as e:
        print(f"❌ Error saving config: {e}")
        return False