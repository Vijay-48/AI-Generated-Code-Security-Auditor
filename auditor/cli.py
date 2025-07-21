#!/usr/bin/env python3
"""
AI Code Security Auditor CLI
Production-ready command-line interface for security scanning
"""

import click
import requests
import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
import fnmatch

# Configuration
DEFAULT_API_URL = "http://localhost:8001"
SUPPORTED_EXTENSIONS = {
    '.py': 'python',
    '.js': 'javascript', 
    '.jsx': 'javascript',
    '.ts': 'javascript',
    '.tsx': 'javascript',
    '.java': 'java',
    '.go': 'go'
}

@click.group()
@click.option('--api-url', default=DEFAULT_API_URL, help='API base URL')
@click.option('--api-key', help='API authentication key')
@click.pass_context
def cli(ctx, api_url, api_key):
    """AI Code Security Auditor CLI - Production Security Scanner"""
    ctx.ensure_object(dict)
    ctx.obj['api_url'] = api_url
    ctx.obj['api_key'] = api_key

@cli.command()
@click.option('--path', default='.', help='Directory or file to scan')
@click.option('--model', default='agentica-org/deepcoder-14b-preview:free', 
              help='LLM model to use for analysis')
@click.option('--output-format', default='table', 
              type=click.Choice(['json', 'table', 'github', 'markdown', 'sarif']),
              help='Output format')
@click.option('--output-file', help='Output file path')
@click.option('--severity-filter', default='all',
              type=click.Choice(['all', 'critical', 'high', 'medium', 'low']),
              help='Filter by minimum severity')
@click.option('--include', multiple=True, help='File patterns to include (glob)')
@click.option('--exclude', multiple=True, help='File patterns to exclude (glob). Repeat flag for multiple patterns: --exclude "*/tests/*" --exclude "*/node_modules/*"')
@click.option('--advanced/--no-advanced', default=False, help='Enable advanced multi-model analysis')
@click.option('--fail-on-high/--no-fail-on-high', default=False, help='Exit with error on high/critical findings')
@click.pass_context
def scan(ctx, path, model, output_format, output_file, severity_filter, 
         include, exclude, advanced, fail_on_high):
    """Scan files or directories for security vulnerabilities"""
    
    try:
        # Discover files to scan
        files_to_scan = discover_files(path, include, exclude)
        
        if not files_to_scan:
            click.echo("❌ No supported files found to scan")
            sys.exit(1)
            
        click.echo(f"🔍 Scanning {len(files_to_scan)} files with {model.split('/')[1].split(':')[0]}")
        
        # Scan files
        all_results = []
        high_severity_found = False
        
        with click.progressbar(files_to_scan, label='Scanning files') as files:
            for file_path in files:
                try:
                    result = scan_file(ctx, file_path, model, advanced)
                    if result:
                        result['file_path'] = str(file_path)
                        all_results.append(result)
                        
                        # Check for high severity vulnerabilities
                        for vuln in result.get('vulnerabilities', []):
                            if vuln.get('severity', '').upper() in ['HIGH', 'CRITICAL']:
                                high_severity_found = True
                                
                except Exception as e:
                    click.echo(f"\n⚠️  Error scanning {file_path}: {str(e)}", err=True)
        
        # Filter by severity
        if severity_filter != 'all':
            all_results = filter_by_severity(all_results, severity_filter)
        
        # Generate output
        output = generate_output(all_results, output_format)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(output)
            click.echo(f"📄 Report saved to {output_file}")
        else:
            click.echo(output)
        
        # Summary
        total_vulns = sum(len(r.get('vulnerabilities', [])) for r in all_results)
        click.echo(f"\n📊 Scan complete: {total_vulns} vulnerabilities found across {len(all_results)} files")
        
        # Exit with error if configured
        if fail_on_high and high_severity_found:
            click.echo("❌ High/Critical severity vulnerabilities found - failing build")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Scan failed: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--code', required=True, help='Code to analyze')
@click.option('--language', required=True, help='Programming language') 
@click.option('--model', default='agentica-org/deepcoder-14b-preview:free', help='LLM model to use')
@click.option('--advanced/--no-advanced', default=False, help='Enable advanced analysis')
@click.pass_context
def analyze(ctx, code, language, model, advanced):
    """Analyze a code snippet directly"""
    
    try:
        api_url = ctx.obj['api_url']
        
        payload = {
            "code": code,
            "language": language,
            "model": model,
            "use_advanced_analysis": advanced
        }
        
        headers = {"Content-Type": "application/json"}
        if ctx.obj.get('api_key'):
            headers['Authorization'] = f"Bearer {ctx.obj['api_key']}"
        
        response = requests.post(f"{api_url}/audit", json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        # Display results
        click.echo("🔍 Analysis Results:")
        click.echo("=" * 50)
        
        vulnerabilities = result.get('vulnerabilities', [])
        if vulnerabilities:
            for vuln in vulnerabilities:
                click.echo(f"📍 {vuln['title']} ({vuln['id']})")
                click.echo(f"   Severity: {vuln['severity']}")
                click.echo(f"   Line: {vuln['line_number']}")
                click.echo(f"   Description: {vuln['description']}")
                click.echo()
        else:
            click.echo("✅ No vulnerabilities detected")
        
        # Show AI-generated patches if available
        patches = result.get('patches', [])
        for patch in patches:
            if 'error' not in patch.get('patch', {}):
                click.echo("🤖 AI-Generated Fix:")
                click.echo(patch['patch'].get('diff', 'No diff available')[:500])
                click.echo()
        
    except Exception as e:
        click.echo(f"❌ Analysis failed: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.pass_context 
def models(ctx):
    """List available LLM models"""
    
    try:
        api_url = ctx.obj['api_url']
        response = requests.get(f"{api_url}/models", timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        click.echo("🤖 Available Models:")
        click.echo("=" * 50)
        
        for model in data['available_models']:
            model_name = model.split('/')[1].split(':')[0]
            click.echo(f"  • {model_name}: {model}")
        
        click.echo("\n💡 Recommendations:")
        for use_case, model in data['recommendations'].items():
            model_name = model.split('/')[1].split(':')[0] 
            click.echo(f"  • {use_case}: {model_name}")
        
    except Exception as e:
        click.echo(f"❌ Failed to fetch models: {str(e)}", err=True)
        sys.exit(1)

def discover_files(path: str, include: tuple, exclude: tuple) -> List[Path]:
    """Discover files to scan based on patterns"""
    path_obj = Path(path)
    files = []
    
    # Default exclude patterns to prevent scanning too many files
    default_excludes = [
        '*/__pycache__/*',
        '*/node_modules/*',
        '*/.git/*',
        '*/venv/*',
        '*/env/*',
        '*/myenv/*',
        '*/.venv/*',
        '*/build/*',
        '*/dist/*',
        '*/target/*',
        '*.log',
        '*.tmp',
        '*.temp',
        '*/.pytest_cache/*',
        '*/.coverage*',
        '*/htmlcov/*',
        '*/chroma_db/*'
    ]
    
    # Combine user excludes with defaults
    all_excludes = list(exclude) + default_excludes
    
    if path_obj.is_file():
        if path_obj.suffix in SUPPORTED_EXTENSIONS:
            files.append(path_obj)
    else:
        for ext in SUPPORTED_EXTENSIONS:
            for file_path in path_obj.rglob(f'*{ext}'):
                if file_path.is_file():
                    files.append(file_path)
    
    # Apply include patterns first
    if include:
        included_files = []
        for file_path in files:
            for pattern in include:
                if fnmatch.fnmatch(str(file_path), pattern):
                    included_files.append(file_path)
                    break
        files = included_files
    
    # Apply exclude patterns (including defaults)
    if all_excludes:
        filtered_files = []
        for file_path in files:
            excluded = False
            for pattern in all_excludes:
                if fnmatch.fnmatch(str(file_path), pattern):
                    excluded = True
                    break
            if not excluded:
                filtered_files.append(file_path)
        files = filtered_files
    
    return files

def scan_file(ctx: click.Context, file_path: Path, model: str, advanced: bool) -> Dict[str, Any]:
    """Scan a single file"""
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    
    if not code.strip():
        return None
    
    language = SUPPORTED_EXTENSIONS.get(file_path.suffix)
    if not language:
        return None
    
    api_url = ctx.obj['api_url']
    
    payload = {
        "code": code,
        "language": language,
        "filename": str(file_path.name),
        "model": model,
        "use_advanced_analysis": advanced
    }
    
    headers = {"Content-Type": "application/json"}
    if ctx.obj.get('api_key'):
        headers['Authorization'] = f"Bearer {ctx.obj['api_key']}"
    
    response = requests.post(f"{api_url}/audit", json=payload, headers=headers, timeout=120)
    response.raise_for_status()
    
    return response.json()

def filter_by_severity(results: List[Dict], min_severity: str) -> List[Dict]:
    """Filter results by minimum severity"""
    severity_order = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    min_index = severity_order.index(min_severity.upper())
    
    filtered_results = []
    for result in results:
        filtered_vulns = []
        for vuln in result.get('vulnerabilities', []):
            vuln_severity = vuln.get('severity', 'LOW').upper()
            if vuln_severity in severity_order and severity_order.index(vuln_severity) >= min_index:
                filtered_vulns.append(vuln)
        
        if filtered_vulns:
            result_copy = result.copy()
            result_copy['vulnerabilities'] = filtered_vulns
            filtered_results.append(result_copy)
    
    return filtered_results

def generate_output(results: List[Dict], format_type: str) -> str:
    """Generate output in specified format"""
    
    if format_type == 'json':
        return json.dumps(results, indent=2)
    
    elif format_type == 'table':
        return generate_table_output(results)
    
    elif format_type == 'github':
        return generate_github_output(results)
    
    elif format_type == 'markdown':
        return generate_markdown_output(results)
    
    elif format_type == 'sarif':
        return generate_sarif_output(results)
    
    else:
        return json.dumps(results, indent=2)

def generate_table_output(results: List[Dict]) -> str:
    """Generate table format output"""
    output = []
    output.append("🔍 Security Audit Results")
    output.append("=" * 80)
    
    for result in results:
        file_path = result.get('file_path', 'unknown')
        vulnerabilities = result.get('vulnerabilities', [])
        
        if vulnerabilities:
            output.append(f"\n📁 File: {file_path}")
            output.append("-" * 50)
            
            for vuln in vulnerabilities:
                output.append(f"  🚨 {vuln['title']} ({vuln['id']})")
                output.append(f"     Severity: {vuln['severity']}")
                output.append(f"     Line: {vuln['line_number']}")
                output.append(f"     Description: {vuln['description']}")
                
                # Show AI fix if available
                patches = result.get('patches', [])
                for patch in patches:
                    if patch.get('vuln', {}).get('id') == vuln['id']:
                        patch_info = patch.get('patch', {})
                        if 'error' not in patch_info and patch_info.get('diff'):
                            output.append(f"     🤖 AI Fix Available: {patch_info.get('confidence', 'MEDIUM')} confidence")
                output.append("")
    
    if not any(result.get('vulnerabilities') for result in results):
        output.append("✅ No vulnerabilities found!")
    
    return "\n".join(output)

def generate_github_output(results: List[Dict]) -> str:
    """Generate GitHub Actions format output"""
    output = []
    output.append("## 🛡️ AI Security Audit Results")
    output.append("")
    
    total_vulns = sum(len(r.get('vulnerabilities', [])) for r in results)
    
    if total_vulns == 0:
        output.append("✅ **No vulnerabilities detected!** Your code is secure.")
        return "\n".join(output)
    
    output.append(f"❌ **{total_vulns} vulnerabilities detected**")
    output.append("")
    output.append("| File | Issue | Severity | Line | AI Fix |")
    output.append("|------|-------|----------|------|--------|")
    
    for result in results:
        file_path = result.get('file_path', 'unknown')
        vulnerabilities = result.get('vulnerabilities', [])
        patches = {p.get('vuln', {}).get('id'): p for p in result.get('patches', [])}
        
        for vuln in vulnerabilities:
            file_short = file_path.split('/')[-1] if '/' in file_path else file_path
            severity_emoji = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢', 'CRITICAL': '⚫'}.get(vuln['severity'], '🔍')
            
            # Check if AI fix is available
            patch = patches.get(vuln['id'], {})
            ai_fix = "✅" if patch.get('patch', {}).get('diff') and 'error' not in patch.get('patch', {}) else "❌"
            
            output.append(f"| `{file_short}` | {vuln['title']} | {severity_emoji} {vuln['severity']} | {vuln['line_number']} | {ai_fix} |")
    
    output.append("")
    output.append("### 🤖 AI-Powered Features")
    output.append("- Code patch generation with DeepCoder")
    output.append("- Quality assessment with LLaMA 3.3")
    output.append("- Security explanations with Kimi")
    
    return "\n".join(output)

def generate_markdown_output(results: List[Dict]) -> str:
    """Generate Markdown format output"""
    output = generate_github_output(results)  # Reuse GitHub format for now
    return output

def generate_sarif_output(results: List[Dict]) -> str:
    """Generate SARIF format output for security tools integration"""
    sarif = {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "AI Code Security Auditor",
                    "version": "1.0.0",
                    "informationUri": "https://github.com/your-repo/ai-code-auditor"
                }
            },
            "results": []
        }]
    }
    
    for result in results:
        file_path = result.get('file_path', 'unknown')
        vulnerabilities = result.get('vulnerabilities', [])
        
        for vuln in vulnerabilities:
            sarif_result = {
                "ruleId": vuln['id'],
                "level": vuln['severity'].lower(),
                "message": {
                    "text": vuln['description']
                },
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": file_path
                        },
                        "region": {
                            "startLine": vuln['line_number']
                        }
                    }
                }]
            }
            sarif["runs"][0]["results"].append(sarif_result)
    
    return json.dumps(sarif, indent=2)

if __name__ == '__main__':
    cli()