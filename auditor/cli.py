#!/usr/bin/env python3
"""
AI Code Security Auditor CLI - Hackathon Version
Simplified command-line interface for security scanning with AI
"""

import click
import requests
import json
import sys
import os
import time
import asyncio
from pathlib import Path
from typing import List, Dict, Any
import fnmatch

# Import configuration to validate API keys
try:
    from app.config import settings, validate_api_keys
    from app.services.scanner import SecurityScanner
    from app.agents.security_agent import SecurityAgent
except ImportError:
    print("❌ Error: Could not import required modules. Run from project root directory.")
    print("💡 Usage: python -m auditor.cli --help")
    sys.exit(1)

# Configuration
DEFAULT_API_URL = "http://localhost:8000"
SUPPORTED_EXTENSIONS = {
    '.py': 'python',
    '.js': 'javascript', 
    '.jsx': 'javascript',
    '.ts': 'javascript',
    '.tsx': 'javascript',
    '.java': 'java',
    '.go': 'go'
}

def check_api_keys():
    """Check if API keys are configured"""
    if not settings.OPENROUTER_API_KEY and not settings.OPENAI_API_KEY:
        print("❌ No API keys found!")
        print("\n📖 Quick Setup:")
        print("1. Copy: cp .env.example .env")
        print("2. Edit .env and add your API key:")
        print("   • OPENROUTER_API_KEY=your_key (from https://openrouter.ai/)")
        print("   • OPENAI_API_KEY=sk-your_key (from https://platform.openai.com/)")
        print("3. Run: python -m auditor.cli --help")
        return False
    return True

@click.group()
@click.option('--api-url', default=DEFAULT_API_URL, help='API base URL (for server mode)')
def cli(api_url):
    """🛡️ AI Code Security Auditor - Hackathon Edition
    
    Detect security vulnerabilities in your code with AI-powered analysis.
    
    Examples:
      python -m auditor.cli scan --path myfile.py
      python -m auditor.cli analyze --code "os.system(user_input)" --language python
      python -m auditor.cli models
    """
    pass

@cli.command()
@click.option('--path', required=True, help='File or directory to scan')
@click.option('--model', default='openai/gpt-4', help='AI model to use')
@click.option('--output-format', default='table', 
              type=click.Choice(['json', 'table', 'github', 'markdown', 'sarif']),
              help='Output format')
@click.option('--output-file', help='Save output to file')
@click.option('--severity-filter', default='all',
              type=click.Choice(['all', 'critical', 'high', 'medium', 'low']),
              help='Filter by minimum severity')
@click.option('--include', multiple=True, help='Include file patterns (glob)')
@click.option('--exclude', multiple=True, help='Exclude file patterns (glob)')
@click.option('--advanced/--no-advanced', default=False, help='Enable advanced AI analysis')
@click.option('--fail-on-high/--no-fail-on-high', default=False, help='Exit with error on high/critical findings')
def scan(path, model, output_format, output_file, severity_filter, include, exclude, advanced, fail_on_high):
    """🔍 Scan files or directories for security vulnerabilities
    
    Examples:
      python -m auditor.cli scan --path app.py
      python -m auditor.cli scan --path ./src --model openai/gpt-4 --advanced
      python -m auditor.cli scan --path . --output-format json --output-file results.json
    """
    
    # Check API keys first
    if not check_api_keys():
        sys.exit(1)
    
    try:
        # Discover files to scan
        files_to_scan = discover_files(path, include, exclude)
        
        if not files_to_scan:
            click.echo("❌ No supported files found to scan")
            click.echo("💡 Supported extensions: " + ", ".join(SUPPORTED_EXTENSIONS.keys()))
            sys.exit(1)
            
        click.echo(f"🔍 Scanning {len(files_to_scan)} files with {model}")
        
        # Scan files
        all_results = []
        high_severity_found = False
        
        with click.progressbar(files_to_scan, label='Scanning files') as files:
            for file_path in files:
                try:
                    result = scan_file_direct(file_path, model, advanced)
                    if result:
                        result['file_path'] = str(file_path)
                        all_results.append(result)
                        
                        # Check for high severity vulnerabilities
                        for vuln in result.get('vulnerabilities', []):
                            if vuln.get('severity', '').upper() in ['HIGH', 'CRITICAL']:
                                high_severity_found = True
                                
                except Exception as e:
                    click.echo(f"\n❌ Error scanning {file_path}: {str(e)}")
        
        # Filter by severity
        if severity_filter != 'all':
            all_results = filter_by_severity(all_results, severity_filter)
        
        # Generate output
        output = generate_output(all_results, output_format)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(output)
            click.echo(f"💾 Report saved to {output_file}")
        else:
            click.echo(output)
        
        # Summary
        total_vulns = sum(len(r.get('vulnerabilities', [])) for r in all_results)
        click.echo(f"\n📊 Scan complete: {total_vulns} vulnerabilities found across {len(all_results)} files")
        
        # Exit with error if configured
        if fail_on_high and high_severity_found:
            click.echo("🚨 High/Critical severity vulnerabilities found - failing build")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Scan failed: {str(e)}")
        sys.exit(1)

@cli.command()
@click.option('--code', required=True, help='Code snippet to analyze')
@click.option('--language', required=True, 
              type=click.Choice(['python', 'javascript', 'java', 'go']),
              help='Programming language') 
@click.option('--model', default='openai/gpt-4', help='AI model to use')
@click.option('--advanced/--no-advanced', default=False, help='Enable advanced analysis')
def analyze(code, language, model, advanced):
    """🤖 Analyze a code snippet directly with AI
    
    Examples:
      python -m auditor.cli analyze --code "os.system(user_input)" --language python
      python -m auditor.cli analyze --code "exec(data)" --language python --model openai/gpt-4
    """
    
    # Check API keys first
    if not check_api_keys():
        sys.exit(1)
    
    try:
        click.echo(f"🤖 Analyzing code with {model}...")
        
        # Create agent and analyze
        agent = SecurityAgent()
        
        result = agent.run(
            code=code,
            language=language,
            filename="<direct_input>",
            preferred_model=model,
            use_advanced_analysis=advanced
        )
        
        # Display results
        click.echo("\n🔍 Analysis Results:")
        click.echo("=" * 60)
        
        vulnerabilities = result.get('vulnerabilities', [])
        if vulnerabilities:
            for i, vuln in enumerate(vulnerabilities, 1):
                severity_emoji = {
                    'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'
                }.get(vuln.get('severity', 'LOW'), '🔵')
                
                click.echo(f"{severity_emoji} {i}. {vuln.get('title', 'Unknown Issue')}")
                click.echo(f"   Severity: {vuln.get('severity', 'Unknown')}")
                click.echo(f"   Line: {vuln.get('line_number', 'N/A')}")
                click.echo(f"   Description: {vuln.get('description', 'No description')}")
                click.echo()
        else:
            click.echo("✅ No vulnerabilities detected!")
        
        # Show AI-generated patches if available
        patches = result.get('patches', [])
        for patch in patches:
            patch_data = patch.get('patch', {})
            if 'error' not in patch_data and patch_data.get('diff'):
                click.echo("🛠️ AI-Generated Fix:")
                diff_preview = patch_data.get('diff', 'No diff available')
                click.echo(diff_preview[:500] + "..." if len(diff_preview) > 500 else diff_preview)
                click.echo()
        
        # Show advanced analysis if requested
        if advanced:
            explanations = result.get('explanations', [])
            if explanations:
                click.echo("📚 AI Security Explanations:")
                for exp in explanations[:2]:  # Limit to first 2
                    explanation_text = exp.get('explanation', 'No explanation available')
                    preview = explanation_text[:300] + "..." if len(explanation_text) > 300 else explanation_text
                    click.echo(f"   {preview}")
                    click.echo()
        
    except Exception as e:
        click.echo(f"❌ Analysis failed: {str(e)}")
        click.echo("💡 Try: python -m auditor.cli models")
        sys.exit(1)

@cli.command()
def models():
    """📋 List available AI models and their capabilities
    
    Shows all available models with recommendations for different use cases.
    """
    
    click.echo("🤖 Available AI Models:")
    click.echo("=" * 50)
    
    models_info = {
        "openai/gpt-4": {
            "name": "OpenAI GPT-4",
            "quality": "★★★★★",
            "speed": "★★★☆☆", 
            "cost": "High",
            "best_for": "Production, highest quality analysis"
        },
        "openai/gpt-3.5-turbo": {
            "name": "OpenAI GPT-3.5 Turbo",
            "quality": "★★★★☆",
            "speed": "★★★★☆",
            "cost": "Medium",
            "best_for": "Development, fast analysis"
        },
        "agentica-org/deepcoder-14b-preview:free": {
            "name": "DeepCoder 14B",
            "quality": "★★★★☆",
            "speed": "★★★☆☆",
            "cost": "Free",
            "best_for": "Code patches and fixes"
        },
        "meta-llama/llama-3.3-70b-instruct:free": {
            "name": "LLaMA 3.3 70B", 
            "quality": "★★★★☆",
            "speed": "★★☆☆☆",
            "cost": "Free",
            "best_for": "Balanced analysis"
        },
        "qwen/qwen-2.5-coder-32b-instruct:free": {
            "name": "Qwen Coder 32B",
            "quality": "★★★☆☆",
            "speed": "★★★★★",
            "cost": "Free", 
            "best_for": "Fast classification"
        }
    }
    
    for model_id, info in models_info.items():
        click.echo(f"\n🔸 {info['name']}")
        click.echo(f"   Model ID: {model_id}")
        click.echo(f"   Quality: {info['quality']}")
        click.echo(f"   Speed: {info['speed']}")
        click.echo(f"   Cost: {info['cost']}")
        click.echo(f"   Best for: {info['best_for']}")
    
    click.echo(f"\n💡 Recommendations:")
    click.echo(f"   • For best results: --model openai/gpt-4")
    click.echo(f"   • For fast analysis: --model openai/gpt-3.5-turbo") 
    click.echo(f"   • For free usage: --model qwen/qwen-2.5-coder-32b-instruct:free")
    
    click.echo(f"\n🔑 API Key Status:")
    click.echo(f"   • OpenAI: {'✅ Configured' if settings.OPENAI_API_KEY else '❌ Not set'}")
    click.echo(f"   • OpenRouter: {'✅ Configured' if settings.OPENROUTER_API_KEY else '❌ Not set'}")

@cli.command()
def test():
    """🧪 Test the installation with a sample vulnerable code
    
    Runs a quick test to verify everything is working correctly.
    """
    
    # Check API keys first
    if not check_api_keys():
        sys.exit(1)
    
    test_code = """
import os
import subprocess

# Vulnerable code for testing
def run_command(user_input):
    os.system(user_input)  # Command injection vulnerability

def db_query(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection
    return query

API_KEY = "sk-1234567890abcdef"  # Hardcoded secret
"""
    
    click.echo("🧪 Running installation test...")
    click.echo("📝 Testing with sample vulnerable code...")
    
    try:
        # Create agent and test
        agent = SecurityAgent()
        
        result = agent.run(
            code=test_code,
            language="python", 
            filename="test.py",
            preferred_model="openai/gpt-4",
            use_advanced_analysis=False
        )
        
        vulnerabilities = result.get('vulnerabilities', [])
        
        if vulnerabilities:
            click.echo(f"✅ Test PASSED! Found {len(vulnerabilities)} vulnerabilities:")
            for i, vuln in enumerate(vulnerabilities[:3], 1):
                click.echo(f"   {i}. {vuln.get('title', 'Unknown')} ({vuln.get('severity', 'Unknown')})")
            
            if len(vulnerabilities) > 3:
                click.echo(f"   ... and {len(vulnerabilities) - 3} more")
        else:
            click.echo("⚠️ Test completed but no vulnerabilities detected.")
            click.echo("This might indicate an issue with the scanners.")
        
        click.echo("\n🎉 Installation test completed successfully!")
        click.echo("💡 Try: python -m auditor.cli scan --path your_file.py")
        
    except Exception as e:
        click.echo(f"❌ Test failed: {str(e)}")
        click.echo("💡 Check your API keys and try again")
        sys.exit(1)

def scan_file_direct(file_path: Path, model: str, advanced: bool) -> Dict[str, Any]:
    """Scan a single file directly using the security agent"""
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        
        if not code.strip():
            return None
        
        language = SUPPORTED_EXTENSIONS.get(file_path.suffix)
        if not language:
            return None
        
        # Create agent and scan
        agent = SecurityAgent()
        
        result = agent.run(
            code=code,
            language=language,
            filename=str(file_path.name),
            preferred_model=model,
            use_advanced_analysis=advanced
        )
        
        return result
        
    except Exception as e:
        return {"error": str(e), "vulnerabilities": []}

def discover_files(path: str, include: tuple, exclude: tuple) -> List[Path]:
    """Discover files to scan based on patterns"""
    path_obj = Path(path)
    files = []
    
    # Default exclude patterns
    default_excludes = [
        '*/__pycache__/*', '*/node_modules/*', '*/.git/*', '*/venv/*',
        '*/env/*', '*/myenv/*', '*/.venv/*', '*/build/*', '*/dist/*',
        '*/target/*', '*.log', '*.tmp', '*.temp', '*/.pytest_cache/*',
        '*/.coverage*', '*/htmlcov/*', '*/chroma_db/*', '*/temp_files/*'
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
    
    # Apply include patterns
    if include:
        included_files = []
        for file_path in files:
            for pattern in include:
                if fnmatch.fnmatch(str(file_path), pattern):
                    included_files.append(file_path)
                    break
        files = included_files
    
    # Apply exclude patterns
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
        return generate_github_output(results)  # Reuse GitHub format
    elif format_type == 'sarif':
        return generate_sarif_output(results)
    else:
        return json.dumps(results, indent=2)

def generate_table_output(results: List[Dict]) -> str:
    """Generate table format output"""
    output = []
    output.append("🛡️ AI Code Security Audit Results")
    output.append("=" * 80)
    
    if not results:
        output.append("✅ No vulnerabilities found! Your code looks secure.")
        return "\n".join(output)
    
    for result in results:
        file_path = result.get('file_path', 'unknown')
        vulnerabilities = result.get('vulnerabilities', [])
        
        if vulnerabilities:
            output.append(f"\n📁 File: {file_path}")
            output.append("-" * 60)
            
            for vuln in vulnerabilities:
                severity_emoji = {
                    'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'
                }.get(vuln.get('severity', 'LOW'), '🔵')
                
                output.append(f"  {severity_emoji} {vuln.get('title', 'Unknown Issue')} ({vuln.get('id', 'Unknown')})")
                output.append(f"     Severity: {vuln.get('severity', 'Unknown')}")
                output.append(f"     Line: {vuln.get('line_number', 'N/A')}")
                output.append(f"     Description: {vuln.get('description', 'No description')}")
                
                # Show AI fix if available
                patches = result.get('patches', [])
                for patch in patches:
                    if patch.get('vuln', {}).get('id') == vuln.get('id'):
                        patch_info = patch.get('patch', {})
                        if 'error' not in patch_info and patch_info.get('diff'):
                            output.append(f"     🤖 AI Fix Available: {patch_info.get('confidence', 'MEDIUM')} confidence")
                output.append("")
    
    return "\n".join(output)

def generate_github_output(results: List[Dict]) -> str:
    """Generate GitHub Actions format output"""
    output = []
    output.append("# 🛡️ AI Security Audit Results")
    output.append("")
    
    total_vulns = sum(len(r.get('vulnerabilities', [])) for r in results)
    
    if total_vulns == 0:
        output.append("## ✅ No vulnerabilities detected!")
        output.append("Your code passed the AI security audit.")
        return "\n".join(output)
    
    output.append(f"## 🚨 {total_vulns} vulnerabilities detected")
    output.append("")
    output.append("| File | Issue | Severity | Line | AI Fix |")
    output.append("|------|-------|----------|------|--------|")
    
    for result in results:
        file_path = result.get('file_path', 'unknown')
        vulnerabilities = result.get('vulnerabilities', [])
        patches = {p.get('vuln', {}).get('id'): p for p in result.get('patches', [])}
        
        for vuln in vulnerabilities:
            file_short = file_path.split('/')[-1] if '/' in file_path else file_path
            severity = vuln.get('severity', 'UNKNOWN')
            
            # Check if AI fix is available
            patch = patches.get(vuln.get('id'), {})
            ai_fix = "✅" if patch.get('patch', {}).get('diff') and 'error' not in patch.get('patch', {}) else "❌"
            
            output.append(f"| `{file_short}` | {vuln.get('title', 'Unknown')} | {severity} | {vuln.get('line_number', 'N/A')} | {ai_fix} |")
    
    output.append("")
    output.append("### 🤖 AI-Powered Features")
    output.append("- Intelligent vulnerability detection")
    output.append("- Automated fix suggestions") 
    output.append("- Security explanations and guidance")
    
    return "\n".join(output)

def generate_sarif_output(results: List[Dict]) -> str:
    """Generate SARIF format output for security tools integration"""
    sarif = {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "AI Code Security Auditor",
                    "version": "2.0.0",
                    "informationUri": "https://github.com/Vijay-48/AI-Generated-Code-Security-Auditor"
                }
            },
            "results": []
        }]
    }
    
    for result in results:
        file_path = result.get('file_path', 'unknown')
        vulnerabilities = result.get('vulnerabilities', [])
        
        for vuln in vulnerabilities:
            severity_map = {
                'CRITICAL': 'error',
                'HIGH': 'error', 
                'MEDIUM': 'warning',
                'LOW': 'note'
            }
            
            sarif_result = {
                "ruleId": vuln.get('id', 'unknown'),
                "level": severity_map.get(vuln.get('severity', 'LOW'), 'note'),
                "message": {
                    "text": vuln.get('description', 'No description available')
                },
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": file_path
                        },
                        "region": {
                            "startLine": vuln.get('line_number', 1)
                        }
                    }
                }]
            }
            sarif["runs"][0]["results"].append(sarif_result)
    
    return json.dumps(sarif, indent=2)

def main():
    """Main entry point for the CLI"""
    cli()

if __name__ == '__main__':
    main()