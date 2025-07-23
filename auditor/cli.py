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

@cli.command()
@click.option('--scan-id', help='Specific scan ID (optional, uses latest if not provided)')
@click.option('--rule', help='Filter by specific rule name (partial match)')
@click.option('--severity', type=click.Choice(['critical', 'high', 'medium', 'low']), help='Filter by severity level')
@click.option('--output', default='table', type=click.Choice(['table', 'json', 'yaml']), help='Output format')
@click.option('--save', help='Save output to file')
@click.option('--no-colors', is_flag=True, help='Disable colored output')
@click.option('--visual', is_flag=True, help='🚀 Enable enhanced visuals with pie charts and severity bars')
@click.option('--color-scheme', default='security', type=click.Choice(['default', 'monochrome', 'dark', 'security']), help='Color scheme for visuals')
@click.pass_context 
def summary(ctx, scan_id, rule, severity, output, save, no_colors, visual, color_scheme):
    """Show comprehensive summary of a scan with filtering options"""
    try:
        # Import required modules
        import sys
        import asyncio
        sys.path.append('/app')
        from app.services.analytics_service import analytics_service
        from app.utils.formatters import ExportFormatter
        
        # NEW: Import visual components for enhanced summary
        if visual:
            from cli_visuals.formatters import create_visual_formatter
            visual_formatter = create_visual_formatter(color_scheme, no_colors)
        
        # Load configuration
        from app.utils.formatters import load_config
        config = load_config()
        
        # Override config with command line options
        if no_colors:
            config['output']['colors'] = False
        
        async def get_summary():
            await analytics_service.connect()
            
            # Build filters
            filters = {}
            if rule:
                filters['rule'] = rule
            if severity:
                filters['severity'] = severity
            
            summary_data = await analytics_service.get_scan_summary_filtered(scan_id, **filters)
            return summary_data
        
        summary_data = asyncio.run(get_summary())
        
        if not summary_data:
            click.echo("❌ No scan data found matching the criteria")
            sys.exit(1)
        
        # Format output
        formatter = ExportFormatter.get_formatter(output)
        
        # NEW: Use enhanced visual summary if --visual flag is enabled
        if visual and output == 'table':
            content = visual_formatter.format_summary_visual(summary_data)
        elif output == 'table':
            content = formatter.format_summary(summary_data, show_colors=config['output']['colors'])
        else:
            content = formatter.format_summary(summary_data)
        
        # Output or save
        if save:
            from app.utils.formatters import save_to_file
            if save_to_file(content, save, output):
                click.echo(f"✅ Summary saved to {save}")
            else:
                sys.exit(1)
        else:
            click.echo(content)
        
    except Exception as e:
        click.echo(f"❌ Error getting scan summary: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--days', default=30, help='Number of days to show trends for')
@click.option('--output', default='ascii', type=click.Choice(['ascii', 'table', 'csv', 'json']), help='Output format')
@click.option('--save', help='Save output to file')
@click.option('--no-colors', is_flag=True, help='Disable colored output')
@click.option('--width', default=40, help='Chart width for ASCII output')
@click.option('--visual', is_flag=True, help='🚀 Enable enhanced ASCII visualizations with sparklines and gradients')
@click.option('--color-scheme', default='default', type=click.Choice(['default', 'monochrome', 'dark', 'security']), help='Color scheme for visuals')
@click.pass_context
def trends(ctx, days, output, save, no_colors, width, visual, color_scheme):
    """Display vulnerability trends over time with export options"""
    try:
        import sys
        import asyncio
        sys.path.append('/app')
        from app.services.analytics_service import analytics_service
        from app.utils.formatters import ExportFormatter, load_config
        
        # NEW: Import visual components for enhanced display
        if visual:
            from cli_visuals.formatters import create_visual_formatter
            visual_formatter = create_visual_formatter(color_scheme, no_colors)
        
        # Load configuration
        config = load_config()
        
        # Override config with command line options
        if no_colors:
            config['output']['colors'] = False
        
        async def get_trends():
            await analytics_service.connect()
            trend_data = await analytics_service.get_trend_data(days)
            return trend_data
        
        trend_data = asyncio.run(get_trends())
        
        if not trend_data:
            click.echo("❌ No trend data found")
            sys.exit(1)
        
        # NEW: Use visual formatting if --visual flag is enabled
        if visual and output == 'ascii':
            content = visual_formatter.format_trends_visual(trend_data, width)
        elif output == 'table':
            lines = []
            lines.append(f"📈 Vulnerability Trends (Last {days} days)")
            lines.append("=" * 50)
            lines.append(f"{'Date':<12} {'Scans':<8} {'Vulns':<8} {'Critical':<10} {'High':<8} {'Medium':<8} {'Low':<8}")
            lines.append("-" * 70)
            for trend in trend_data[-14:]:  # Show last 14 days
                lines.append(f"{trend.date:<12} {trend.total_scans:<8} {trend.total_vulnerabilities:<8} "
                           f"{trend.critical:<10} {trend.high:<8} {trend.medium:<8} {trend.low:<8}")
            content = "\n".join(lines)
            
        elif output == 'ascii':
            lines = []
            lines.append(f"📈 Vulnerability Trends (Last {days} days)")
            lines.append("=" * 50)
            
            # ASCII chart
            max_vulns = max(trend.total_vulnerabilities for trend in trend_data) if trend_data else 1
            
            lines.append("Vulnerability Count Over Time:")
            lines.append(f"Max: {max_vulns} vulnerabilities")
            lines.append("")
            
            for trend in trend_data[-14:]:  # Show last 14 days
                bar_length = int((trend.total_vulnerabilities / max_vulns) * width) if max_vulns > 0 else 0
                bar = "█" * bar_length + "░" * (width - bar_length)
                lines.append(f"{trend.date} |{bar}| {trend.total_vulnerabilities}")
            
            content = "\n".join(lines)
            
        else:
            formatter = ExportFormatter.get_formatter(output)
            content = formatter.format_trends(trend_data)
        
        # Add summary for ascii and table formats
        if output in ['ascii', 'table']:
            total_scans = sum(t.total_scans for t in trend_data)
            total_vulns = sum(t.total_vulnerabilities for t in trend_data)
            avg_per_day = total_vulns / len(trend_data) if trend_data else 0
            
            content += f"\n\n📊 Summary"
            content += f"\nTotal Scans: {total_scans}"
            content += f"\nTotal Vulnerabilities: {total_vulns}"
            content += f"\nAverage per day: {avg_per_day:.1f}"
        
        # Output or save
        if save:
            from app.utils.formatters import save_to_file
            if save_to_file(content, save, output):
                click.echo(f"✅ Trends saved to {save}")
            else:
                sys.exit(1)
        else:
            click.echo(content)
        
    except Exception as e:
        click.echo(f"❌ Error getting trends: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--scan-id', help='Specific scan ID (optional, uses latest if not provided)')
@click.option('--width', default=50, help='Heatmap width in characters')
@click.option('--output', default='ascii', type=click.Choice(['ascii', 'csv', 'json']), help='Output format')
@click.option('--save', help='Save output to file')
@click.option('--visual', is_flag=True, help='🚀 Enable enhanced gradient heatmap with 256-color support')
@click.option('--color-scheme', default='default', type=click.Choice(['default', 'monochrome', 'dark', 'security']), help='Color scheme for heatmap')
@click.pass_context
def heatmap(ctx, scan_id, width, output, save, visual, color_scheme):
    """Show heatmap of rule hits per directory with export options"""
    try:
        import sys
        import asyncio
        sys.path.append('/app')
        from app.services.analytics_service import analytics_service
        from app.utils.formatters import ExportFormatter
        
        # NEW: Import visual components for enhanced heatmap
        if visual:
            from cli_visuals.formatters import create_visual_formatter
            visual_formatter = create_visual_formatter(color_scheme, False)
        
        async def get_heatmap():
            await analytics_service.connect()
            heatmap_data = await analytics_service.get_heatmap_data(scan_id)
            return heatmap_data
        
        heatmap_data = asyncio.run(get_heatmap())
        
        if not heatmap_data:
            click.echo("❌ No heatmap data found")
            sys.exit(1)
        
        # Format based on output type
        formatter = ExportFormatter.get_formatter(output)
        
        # NEW: Use enhanced visual heatmap if --visual flag is enabled
        if visual and output == 'ascii':
            content = visual_formatter.format_heatmap_visual(heatmap_data, width)
        elif output == 'ascii':
            lines = []
            lines.append("🗺️  Security Heatmap - Rule Hits by Directory")
            lines.append("=" * (width + 20))
            
            max_hits = max(entry.rule_hits for entry in heatmap_data) if heatmap_data else 1
            
            # Color mapping for heat intensity
            def get_heat_char(hits, max_hits):
                if max_hits == 0:
                    return "░"
                intensity = hits / max_hits
                if intensity >= 0.8:
                    return "█"  # Very hot
                elif intensity >= 0.6:
                    return "▓"  # Hot
                elif intensity >= 0.4:
                    return "▒"  # Medium
                elif intensity >= 0.2:
                    return "░"  # Cool
                else:
                    return "·"  # Cold
            
            lines.append(f"Legend: █ Very High  ▓ High  ▒ Medium  ░ Low  · Minimal")
            lines.append(f"Max hits: {max_hits}")
            lines.append("")
            
            for entry in heatmap_data[:15]:  # Show top 15 directories
                heat_char = get_heat_char(entry.rule_hits, max_hits)
                bar_length = int((entry.rule_hits / max_hits) * (width - 20)) if max_hits > 0 else 0
                bar = heat_char * bar_length + "·" * ((width - 20) - bar_length)
                
                # Truncate path for display
                path_display = entry.path if len(entry.path) <= 25 else "..." + entry.path[-22:]
                
                lines.append(f"{path_display:<25} |{bar}| {entry.rule_hits:>4} hits ({entry.files_count} files)")
            
            content = "\n".join(lines)
        else:
            content = formatter.format_heatmap(heatmap_data)
        
        # Output or save
        if save:
            from app.utils.formatters import save_to_file
            if save_to_file(content, save, output):
                click.echo(f"✅ Heatmap saved to {save}")
            else:
                sys.exit(1)
        else:
            click.echo(content)
        
    except Exception as e:
        click.echo(f"❌ Error getting heatmap: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--limit', default=20, help='Number of repositories to show')
@click.option('--min-score', type=float, help='Minimum security score filter')
@click.option('--language', type=click.Choice(['python', 'javascript', 'java', 'go']), help='Filter by language')
@click.option('--since', help='Show repositories scanned since date (YYYY-MM-DD)')
@click.option('--output', default='table', type=click.Choice(['table', 'csv', 'json']), help='Output format')
@click.option('--save', help='Save output to file')
@click.option('--no-colors', is_flag=True, help='Disable colored output')
@click.pass_context
def repos(ctx, limit, min_score, language, since, output, save, no_colors):
    """Show repository statistics with filtering and export options"""
    try:
        import sys
        import asyncio
        from datetime import datetime
        sys.path.append('/app')
        from app.services.analytics_service import analytics_service
        from app.utils.formatters import ExportFormatter, load_config
        
        # Load configuration
        config = load_config()
        
        # Override config with command line options
        if no_colors:
            config['output']['colors'] = False
        
        # Parse filters
        filters = {}
        if min_score is not None:
            filters['min_score'] = min_score
        if language:
            filters['language'] = language
        if since:
            try:
                filters['since'] = datetime.strptime(since, '%Y-%m-%d')
            except ValueError:
                click.echo("❌ Invalid since date format. Use YYYY-MM-DD", err=True)
                sys.exit(1)
        
        async def get_repos():
            await analytics_service.connect()
            repos_data = await analytics_service.get_repository_stats_filtered(limit, **filters)
            return repos_data
        
        repos_data = asyncio.run(get_repos())
        
        if not repos_data:
            click.echo("❌ No repository data found matching the criteria")
            sys.exit(1)
        
        # Format based on output type
        formatter = ExportFormatter.get_formatter(output)
        
        if output == 'table':
            lines = []
            lines.append(f"📁 Repository Security Statistics ({len(repos_data)} repositories)")
            lines.append("=" * 80)
            lines.append(f"{'Repository':<30} {'Score':<8} {'Vulns':<8} {'Scans':<8} {'Files':<8} {'Last Scan':<12}")
            lines.append("-" * 80)
            
            for repo in repos_data:
                repo_name = repo.repository_name[:28] if len(repo.repository_name) > 28 else repo.repository_name
                score_display = f"{repo.security_score:.1f}" if not config['output']['colors'] else \
                    formatter.colorize_score(repo.security_score)
                last_scan = repo.last_scan_date.strftime('%Y-%m-%d') if repo.last_scan_date else 'N/A'
                
                lines.append(f"{repo_name:<30} {score_display:<8} {repo.total_vulnerabilities:<8} "
                           f"{repo.total_scans:<8} {repo.total_files:<8} {last_scan:<12}")
            
            content = "\n".join(lines)
            
            # Add summary
            avg_score = sum(r.security_score for r in repos_data) / len(repos_data) if repos_data else 0
            total_vulns = sum(r.total_vulnerabilities for r in repos_data)
            content += f"\n\n📊 Summary"
            content += f"\nAverage Security Score: {avg_score:.1f}"
            content += f"\nTotal Vulnerabilities: {total_vulns}"
        else:
            content = formatter.format_repositories(repos_data)
        
        # Output or save
        if save:
            from app.utils.formatters import save_to_file
            if save_to_file(content, save, output):
                click.echo(f"✅ Repository statistics saved to {save}")
            else:
                sys.exit(1)
        else:
            click.echo(content)
        
    except Exception as e:
        click.echo(f"❌ Error getting repository statistics: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--format', default='yaml', type=click.Choice(['yaml', 'json']), help='Configuration format')
@click.option('--reset', is_flag=True, help='Reset configuration to defaults')
@click.pass_context
def config(ctx, format, reset):
    """Manage CLI configuration settings"""
    try:
        import sys
        sys.path.append('/app')
        from app.utils.formatters import load_config, save_config, get_config_dir
        
        config_dir = get_config_dir()
        
        if reset:
            # Reset to defaults
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
            
            if save_config(default_config):
                click.echo("✅ Configuration reset to defaults")
            else:
                click.echo("❌ Failed to reset configuration")
                sys.exit(1)
        else:
            # Show current configuration
            config_data = load_config()
            
            if format == 'json':
                import json
                click.echo(json.dumps(config_data, indent=2))
            else:
                import yaml
                click.echo(yaml.dump(config_data, default_flow_style=False, sort_keys=False))
            
            click.echo(f"\nConfiguration file location: {config_dir}/config.yml")
            click.echo("Edit this file to customize default settings.")
        
    except Exception as e:
        click.echo(f"❌ Error managing configuration: {str(e)}", err=True)
        sys.exit(1)

@cli.command() 
@click.option('--limit', default=20, help='Number of scans to show')
@click.option('--since', help='Show scans since date (YYYY-MM-DD)')
@click.option('--until', help='Show scans until date (YYYY-MM-DD)')
@click.option('--min-score', type=float, help='Minimum security score filter')
@click.option('--max-score', type=float, help='Maximum security score filter')
@click.option('--repo', help='Filter by repository URL (partial match)')
@click.option('--language', type=click.Choice(['python', 'javascript', 'java', 'go']), help='Filter by language')
@click.option('--scan-type', type=click.Choice(['single_file', 'repository', 'bulk']), help='Filter by scan type')
@click.option('--output', default='table', type=click.Choice(['table', 'detailed', 'csv', 'json', 'sarif']), help='Output format')
@click.option('--save', help='Save output to file')
@click.option('--no-colors', is_flag=True, help='Disable colored output')
@click.option('--progress', is_flag=True, help='Show progress bar for large datasets')
@click.pass_context
def history(ctx, limit, since, until, min_score, max_score, repo, language, scan_type, output, save, no_colors, progress):
    """Show scan history with advanced filtering and export options"""
    try:
        import sys
        import asyncio
        from datetime import datetime
        sys.path.append('/app')
        from app.services.analytics_service import analytics_service
        from app.utils.formatters import ExportFormatter, load_config
        
        # Load configuration
        config = load_config()
        
        # Override config with command line options
        if no_colors:
            config['output']['colors'] = False
        if not progress:
            config['output']['progress_bars'] = False
        
        # Parse date filters
        filters = {}
        if since:
            try:
                filters['since'] = datetime.strptime(since, '%Y-%m-%d')
            except ValueError:
                click.echo("❌ Invalid since date format. Use YYYY-MM-DD", err=True)
                sys.exit(1)
        
        if until:
            try:
                filters['until'] = datetime.strptime(until, '%Y-%m-%d')
            except ValueError:
                click.echo("❌ Invalid until date format. Use YYYY-MM-DD", err=True)
                sys.exit(1)
        
        # Add other filters
        if min_score is not None:
            filters['min_score'] = min_score
        if max_score is not None:
            filters['max_score'] = max_score
        if repo:
            filters['repo'] = repo
        if language:
            filters['language'] = language
        if scan_type:
            filters['scan_type'] = scan_type
        
        async def get_history():
            await analytics_service.connect()
            
            if config['output']['progress_bars'] and limit > 50:
                try:
                    from tqdm import tqdm
                    with tqdm(total=1, desc="Fetching scan history") as pbar:
                        history_data = await analytics_service.get_scan_history(limit, **filters)
                        pbar.update(1)
                    return history_data
                except ImportError:
                    pass
            
            history_data = await analytics_service.get_scan_history(limit, **filters)
            return history_data
        
        history_data = asyncio.run(get_history())
        
        if not history_data:
            click.echo("❌ No scan history found matching the criteria")
            sys.exit(1)
        
        # Format output
        formatter = ExportFormatter.get_formatter(output)
        
        if output == 'table':
            content = formatter.format_scan_history(history_data, show_colors=config['output']['colors'])
        elif output == 'detailed':
            # Detailed format with full information
            lines = []
            header = f"📋 Detailed Scan History (Last {len(history_data)} scans)"
            lines.append(header)
            lines.append("=" * max(80, len(header)))
            
            for i, entry in enumerate(history_data, 1):
                lines.append(f"\n{i}. Scan ID: {entry.scan_id}")
                lines.append(f"   Date: {entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                if entry.repository:
                    repo_name = entry.repository.split('/')[-1] if '/' in entry.repository else entry.repository
                    lines.append(f"   Repository: {repo_name}")
                lines.append(f"   Security Score: {entry.security_score:.1f}/100")
                lines.append(f"   Issues: {entry.total_issues}")
                lines.append(f"   Type: {entry.scan_type}")
                if entry.duration:
                    lines.append(f"   Duration: {entry.duration:.2f}s")
                if entry.top_issues:
                    lines.append(f"   Top Issues: {', '.join(entry.top_issues[:3])}")
            
            # Summary statistics
            total_issues = sum(h.total_issues for h in history_data)
            avg_score = sum(h.security_score for h in history_data) / len(history_data)
            
            lines.append(f"\n📊 Summary")
            lines.append(f"Total Issues Found: {total_issues}")
            lines.append(f"Average Security Score: {avg_score:.1f}")
            
            content = "\n".join(lines)
        else:
            content = formatter.format_scan_history(history_data)
        
        # Output or save
        if save:
            from app.utils.formatters import save_to_file
            if save_to_file(content, save, output):
                click.echo(f"✅ History saved to {save}")
            else:
                sys.exit(1)
        else:
            click.echo(content)
        
        # Show summary unless output is non-table format
        if output == 'table' or output == 'detailed':
            total_issues = sum(h.total_issues for h in history_data)
            avg_score = sum(h.security_score for h in history_data) / len(history_data) if history_data else 0
            
            if output == 'table':
                click.echo(f"\n📊 Summary")
                click.echo(f"Total Issues Found: {total_issues}")
                click.echo(f"Average Security Score: {avg_score:.1f}")
        
    except Exception as e:
        click.echo(f"❌ Error getting scan history: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--period', default=30, help='Number of days to analyze')
@click.option('--granularity', default='daily', type=click.Choice(['hourly', 'daily', 'weekly']), help='Time granularity')
@click.option('--include-forecast', is_flag=True, help='Include trend forecasting')
@click.option('--output', default='table', type=click.Choice(['table', 'json', 'csv']), help='Output format')
@click.option('--save', help='Save output to file')
@click.option('--visual', is_flag=True, help='🚀 Enable enhanced visualizations with sparklines')
@click.pass_context
def trends_detailed(ctx, period, granularity, include_forecast, output, save, visual):
    """🔥 PHASE 9: Advanced vulnerability trends analysis with forecasting"""
    try:
        import asyncio
        import json
        
        api_url = ctx.obj['api_url']
        
        # Make API request
        params = {
            'period': period,
            'granularity': granularity,
            'include_forecasting': include_forecast
        }
        
        response = requests.get(f"{api_url}/api/analytics/trends/detailed", params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if output == 'json':
            content = json.dumps(data, indent=2)
        elif output == 'csv':
            # Convert to CSV format
            lines = ['time_period,total_scans,total_issues,critical,high,medium,low,avg_security_score,growth_rate']
            for trend in data['trends']:
                lines.append(f"{trend['time_period']},{trend['total_scans']},{trend['total_issues']},"
                           f"{trend['severity_breakdown']['critical']},{trend['severity_breakdown']['high']},"
                           f"{trend['severity_breakdown']['medium']},{trend['severity_breakdown']['low']},"
                           f"{trend['avg_security_score']},{trend['growth_rate_percent']}")
            content = '\n'.join(lines)
        else:
            # Table format with enhanced visuals
            lines = []
            lines.append(f"📈 Advanced Trend Analysis ({data['period_days']} days, {data['granularity']} granularity)")
            lines.append("=" * 80)
            lines.append(f"Data Points: {data['data_points']}")
            lines.append("")
            
            # Table header
            lines.append(f"{'Period':<15} {'Scans':<7} {'Issues':<7} {'Critical':<8} {'High':<6} {'Score':<6} {'Growth%':<8}")
            lines.append("-" * 80)
            
            for trend in data['trends']:
                period_short = trend['time_period'][:10] if len(trend['time_period']) > 10 else trend['time_period']
                growth_indicator = "📈" if trend['growth_rate_percent'] > 10 else "📉" if trend['growth_rate_percent'] < -10 else "➡️"
                
                lines.append(f"{period_short:<15} {trend['total_scans']:<7} {trend['total_issues']:<7} "
                           f"{trend['severity_breakdown']['critical']:<8} {trend['severity_breakdown']['high']:<6} "
                           f"{trend['avg_security_score']:<6.1f} {growth_indicator}{trend['growth_rate_percent']:<7.1f}")
            
            # Add forecasting if available
            if 'forecasting' in data:
                forecast = data['forecasting']
                lines.append("")
                lines.append("🔮 Trend Forecasting")
                lines.append("-" * 30)
                lines.append(f"Average Growth Rate: {forecast['average_growth_rate']:.1f}%")
                lines.append(f"Trend Direction: {forecast['trend_direction']}")
                lines.append(f"Confidence: {forecast['confidence']}")
            
            # Enhanced visual mode
            if visual:
                try:
                    # Generate sparkline for issues trend
                    issue_counts = [t['total_issues'] for t in data['trends']]
                    if issue_counts:
                        # Simple ASCII sparkline
                        max_val = max(issue_counts) if max(issue_counts) > 0 else 1
                        normalized = [int((val / max_val) * 8) for val in issue_counts]
                        sparkline_chars = " ▁▂▃▄▅▆▇█"
                        sparkline = "".join(sparkline_chars[min(8, val)] for val in normalized)
                        
                        lines.append("")
                        lines.append("✨ Issues Trend Sparkline:")
                        lines.append(f"   {sparkline}")
                        lines.append(f"   {min(issue_counts)}-{max(issue_counts)} issues")
                except Exception as e:
                    lines.append(f"⚠️ Visual enhancement failed: {e}")
            
            content = "\n".join(lines)
        
        # Output or save
        if save:
            with open(save, 'w') as f:
                f.write(content)
            click.echo(f"✅ Trends analysis saved to {save}")
        else:
            click.echo(content)
        
    except Exception as e:
        click.echo(f"❌ Failed to get trends analysis: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--limit', default=10, help='Number of top rules to show')
@click.option('--time-range', default='30d', help='Time range for analysis')
@click.option('--severity', type=click.Choice(['critical', 'high', 'medium', 'low']), help='Filter by severity')
@click.option('--tool', type=click.Choice(['bandit', 'semgrep']), help='Filter by security tool')
@click.option('--output', default='table', type=click.Choice(['table', 'json', 'csv']), help='Output format')
@click.option('--save', help='Save output to file')
@click.pass_context
def top_rules(ctx, limit, time_range, severity, tool, output, save):
    """🔝 PHASE 9: Most frequently triggered vulnerability rules analysis"""
    try:
        import json
        
        api_url = ctx.obj['api_url']
        
        # Build query parameters
        params = {
            'limit': limit,
            'time_range': time_range
        }
        
        if severity:
            params['severity_filter'] = severity
        if tool:
            params['tool_filter'] = tool
        
        response = requests.get(f"{api_url}/api/analytics/top-rules", params=params, timeout=20)
        response.raise_for_status()
        
        data = response.json()
        
        if output == 'json':
            content = json.dumps(data, indent=2)
        elif output == 'csv':
            # Convert to CSV
            lines = ['rule_name,severity,tool,total_hits,affected_scans,affected_files,percentage,avg_hits_per_scan']
            for rule in data['top_rules']:
                lines.append(f"{rule['rule_name']},{rule['severity']},{rule['tool']},"
                           f"{rule['total_hits']},{rule['affected_scans']},{rule['affected_files']},"
                           f"{rule['percentage_of_total']:.1f},{rule['avg_hits_per_scan']:.1f}")
            content = '\n'.join(lines)
        else:
            # Table format  
            lines = []
            lines.append(f"🔝 Top Vulnerability Rules Analysis ({data['time_range']})")
            lines.append("=" * 90)
            
            # Show filters
            filters = data.get('filters', {})
            active_filters = []
            if filters.get('severity'):
                active_filters.append(f"severity={filters['severity']}")
            if filters.get('tool'):
                active_filters.append(f"tool={filters['tool']}")
            
            if active_filters:
                lines.append(f"Filters: {', '.join(active_filters)}")
                lines.append("")
            
            # Summary
            summary = data.get('summary', {})
            lines.append(f"📊 Summary:")
            lines.append(f"   Total Rules: {data['total_unique_rules']}")
            lines.append(f"   Total Hits: {summary.get('total_hits_analyzed', 0)}")
            if summary.get('most_common_severity'):
                lines.append(f"   Most Common Severity: {summary['most_common_severity'].upper()}")
            if summary.get('most_active_tool'):
                lines.append(f"   Most Active Tool: {summary['most_active_tool']}")
            lines.append("")
            
            # Table
            lines.append(f"{'Rank':<5} {'Rule':<25} {'Severity':<9} {'Tool':<8} {'Hits':<6} {'Files':<6} {'%':<6} {'Avg':<5}")
            lines.append("-" * 90)
            
            for i, rule in enumerate(data['top_rules'], 1):
                rule_short = rule['rule_name'][:23] if len(rule['rule_name']) > 23 else rule['rule_name']
                severity_emoji = {'critical': '⚫', 'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(rule['severity'], '🔍')
                
                lines.append(f"{i:<5} {rule_short:<25} {severity_emoji}{rule['severity']:<8} {rule['tool']:<8} "
                           f"{rule['total_hits']:<6} {rule['affected_files']:<6} "
                           f"{rule['percentage_of_total']:<6.1f} {rule['avg_hits_per_scan']:<5.1f}")
            
            content = "\n".join(lines)
        
        # Output or save
        if save:
            with open(save, 'w') as f:
                f.write(content)
            click.echo(f"✅ Top rules analysis saved to {save}")
        else:
            click.echo(content)
        
    except Exception as e:
        click.echo(f"❌ Failed to get top rules analysis: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--include-cache', is_flag=True, default=True, help='Include cache performance metrics')
@click.option('--include-models', is_flag=True, default=True, help='Include LLM model performance')
@click.option('--breakdown-language', is_flag=True, help='Break down by programming language')
@click.option('--output', default='table', type=click.Choice(['table', 'json', 'csv']), help='Output format')
@click.option('--save', help='Save output to file')
@click.pass_context
def performance(ctx, include_cache, include_models, breakdown_language, output, save):
    """⚡ PHASE 9: Detailed performance analysis and optimization insights"""
    try:
        import json
        
        api_url = ctx.obj['api_url']
        
        # Build query parameters
        params = {
            'include_caching': include_cache,
            'include_model_stats': include_models,
            'breakdown_by_language': breakdown_language
        }
        
        response = requests.get(f"{api_url}/api/analytics/performance/detailed", params=params, timeout=20)
        response.raise_for_status()
        
        data = response.json()
        
        if output == 'json':
            content = json.dumps(data, indent=2)
        elif output == 'csv':
            # Convert overall metrics to CSV
            lines = ['metric,value']
            overall = data['overall_metrics']
            for key, value in overall.items():
                lines.append(f"{key},{value}")
            content = '\n'.join(lines)
        else:
            # Enhanced table format
            lines = []
            lines.append("⚡ Performance Analysis Dashboard")
            lines.append("=" * 60)
            
            # Overall metrics
            overall = data['overall_metrics']
            lines.append("📊 Overall Performance Metrics")
            lines.append("-" * 35)
            lines.append(f"Total Scans: {overall['total_scans']:,}")
            lines.append(f"Average Duration: {overall['avg_scan_duration']:.2f}s")
            lines.append(f"Min Duration: {overall['min_scan_duration']:.2f}s")
            lines.append(f"Max Duration: {overall['max_scan_duration']:.2f}s")
            lines.append(f"Avg Files/Scan: {overall['avg_files_per_scan']:.1f}")
            lines.append(f"Avg Security Score: {overall['avg_security_score']:.1f}/100")
            lines.append("")
            
            # Performance by scan type
            if 'by_scan_type' in data:
                lines.append("🔍 Performance by Scan Type")
                lines.append("-" * 35)
                lines.append(f"{'Type':<15} {'Count':<8} {'Avg Duration':<12} {'Avg Files':<10}")
                lines.append("-" * 45)
                for perf in data['by_scan_type']:
                    lines.append(f"{perf['scan_type']:<15} {perf['total_scans']:<8} "
                               f"{perf['avg_duration']:<12.2f} {perf['avg_files']:<10.1f}")
                lines.append("")
            
            # Model performance
            if 'by_model' in data and data['by_model']:
                lines.append("🤖 LLM Model Performance")
                lines.append("-" * 35)
                lines.append(f"{'Model':<25} {'Usage':<8} {'Avg Duration':<12}")
                lines.append("-" * 45)
                for perf in data['by_model']:
                    model_short = perf['model'].split('/')[-1][:23] if '/' in perf['model'] else perf['model'][:23]
                    lines.append(f"{model_short:<25} {perf['usage_count']:<8} {perf['avg_duration']:<12.2f}")
                lines.append("")
            
            # Language breakdown
            if 'by_language' in data and data['by_language']:
                lines.append("💻 Performance by Language")
                lines.append("-" * 35)
                lines.append(f"{'Language':<12} {'Scans':<8} {'Duration':<10} {'Avg Issues':<11}")
                lines.append("-" * 41)
                for perf in data['by_language']:
                    lines.append(f"{perf['language']:<12} {perf['total_scans']:<8} "
                               f"{perf['avg_duration']:<10.2f} {perf['avg_issues_found']:<11.1f}")
                lines.append("")
            
            # Cache metrics
            if 'cache_metrics' in data:
                cache = data['cache_metrics']
                lines.append("🚀 Cache Performance")
                lines.append("-" * 25)
                lines.append(f"Cache Available: {'✅' if cache['cache_available'] else '❌'}")
                lines.append(f"Hit Rate: {cache['estimated_cache_hit_rate']:.1f}%")
                if cache.get('note'):
                    lines.append(f"Note: {cache['note']}")
            
            content = "\n".join(lines)
        
        # Output or save
        if save:
            with open(save, 'w') as f:
                f.write(content)
            click.echo(f"✅ Performance analysis saved to {save}")
        else:
            click.echo(content)
        
    except Exception as e:
        click.echo(f"❌ Failed to get performance analysis: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--report-type', default='security_summary', 
              type=click.Choice(['security_summary', 'vulnerability_trends', 'performance_analysis', 'top_rules_analysis']),
              help='Type of report to generate')
@click.option('--time-range', default='7d', help='Time range for report (1h, 24h, 7d, 30d)')
@click.option('--format', 'report_format', default='markdown', 
              type=click.Choice(['markdown', 'json', 'csv', 'text']),
              help='Output format')
@click.option('--save', help='Save report to file')
@click.option('--email', help='Email address to send report (future feature)')
@click.pass_context
def generate_report(ctx, report_type, time_range, report_format, save, email):
    """🔥 PHASE 9: Generate comprehensive security analytics reports"""
    try:
        import asyncio
        import sys
        sys.path.append('/app')
        
        from app.utils.report_generator import report_generator
        from app.models.analytics import TimeRange
        
        # Map time range string to enum
        time_range_map = {
            '1h': TimeRange.LAST_HOUR,
            '24h': TimeRange.LAST_DAY,
            '7d': TimeRange.LAST_WEEK,
            '30d': TimeRange.LAST_MONTH,
            '90d': TimeRange.LAST_QUARTER,
            '365d': TimeRange.LAST_YEAR
        }
        
        time_range_enum = time_range_map.get(time_range, TimeRange.LAST_WEEK)
        
        async def generate():
            return await report_generator.generate_scheduled_report(
                report_type=report_type,
                time_range=time_range_enum,
                format_type=report_format,
                save_path=save
            )
        
        # Generate the report
        click.echo(f"🚀 Generating {report_type.replace('_', ' ').title()} report...")
        click.echo(f"📅 Time Range: {time_range}")
        click.echo(f"📄 Format: {report_format}")
        
        content = asyncio.run(generate())
        
        if save:
            click.echo(f"✅ Report saved to {save}")
            
            # Show preview of saved report
            preview_lines = content.split('\n')[:10]
            click.echo("\n📋 Preview:")
            click.echo("-" * 50)
            for line in preview_lines:
                click.echo(line)
            if len(content.split('\n')) > 10:
                click.echo("... (truncated)")
        else:
            click.echo(content)
        
        # Future email feature
        if email:
            click.echo(f"📧 Email feature to {email} - Coming in Phase 9B!")
        
        click.echo(f"\n✨ Report generation completed successfully!")
        
    except Exception as e:
        click.echo(f"❌ Failed to generate report: {str(e)}", err=True)
        sys.exit(1)

def main():
    """Main entry point for the CLI"""
    cli()

if __name__ == '__main__':
    main()