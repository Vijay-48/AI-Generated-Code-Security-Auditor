#!/usr/bin/env python3
"""
🚀 PHASE 9 DEMONSTRATION: Advanced Monitoring & Analytics

This demo showcases the new advanced analytics capabilities
added to the AI Code Security Auditor in Phase 9.
"""

import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:8001"

def demo_header():
    print("=" * 80)
    print("🚀 PHASE 9: ADVANCED MONITORING & ANALYTICS DEMONSTRATION")
    print("=" * 80)
    print("AI Code Security Auditor v2.0 - Enhanced Analytics Features")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def demo_new_api_endpoints():
    print("📈 TESTING NEW ANALYTICS API ENDPOINTS")
    print("-" * 50)
    
    # Test detailed trends
    print("1. Testing /api/analytics/trends/detailed")
    try:
        response = requests.get(f"{API_BASE}/api/analytics/trends/detailed", 
                              params={"period": 7, "granularity": "daily", "include_forecasting": True})
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS: {data['data_points']} data points over {data['period_days']} days")
            if 'forecasting' in data:
                print(f"   📊 Forecast: {data['forecasting']['trend_direction']} trend")
        else:
            print(f"   ❌ FAILED: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  ERROR: {e}")
    
    # Test top rules
    print("2. Testing /api/analytics/top-rules")
    try:
        response = requests.get(f"{API_BASE}/api/analytics/top-rules",
                              params={"limit": 5, "time_range": "30d"})
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS: {len(data['top_rules'])} rules analyzed")
            print(f"   🔝 Most active tool: {data['summary']['most_active_tool']}")
        else:
            print(f"   ❌ FAILED: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  ERROR: {e}")
    
    # Test detailed performance
    print("3. Testing /api/analytics/performance/detailed")
    try:
        response = requests.get(f"{API_BASE}/api/analytics/performance/detailed",
                              params={"include_model_stats": True, "breakdown_by_language": True})
        if response.status_code == 200:
            data = response.json()
            total_scans = data['overall_metrics']['total_scans']
            avg_duration = data['overall_metrics']['avg_scan_duration']
            print(f"   ✅ SUCCESS: {total_scans} scans analyzed (avg: {avg_duration:.2f}s)")
        else:
            print(f"   ❌ FAILED: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  ERROR: {e}")
    
    print()

def demo_cli_commands():
    print("🖥️  TESTING NEW CLI COMMANDS")
    print("-" * 40)
    
    import subprocess
    import os
    
    os.chdir('/app')
    
    # Test trends-detailed command
    print("1. Testing CLI: trends-detailed")
    try:
        result = subprocess.run(['python', 'auditor/cli.py', 'trends-detailed', 
                               '--period', '7', '--granularity', 'daily'],
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            print(f"   ✅ SUCCESS: Generated {len(lines)} lines of output")
            print(f"   📈 Sample: {lines[0] if lines else 'No output'}")
        else:
            print(f"   ❌ FAILED: {result.stderr}")
    except Exception as e:
        print(f"   ⚠️  ERROR: {e}")
    
    # Test top-rules command
    print("2. Testing CLI: top-rules")
    try:
        result = subprocess.run(['python', 'auditor/cli.py', 'top-rules', '--limit', '5'],
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            print(f"   ✅ SUCCESS: Generated {len(lines)} lines of output")
        else:
            print(f"   ❌ FAILED: {result.stderr}")
    except Exception as e:
        print(f"   ⚠️  ERROR: {e}")
    
    # Test performance command
    print("3. Testing CLI: performance")
    try:
        result = subprocess.run(['python', 'auditor/cli.py', 'performance', '--include-models'],
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            print(f"   ✅ SUCCESS: Generated {len(lines)} lines of output")
        else:
            print(f"   ❌ FAILED: {result.stderr}")
    except Exception as e:
        print(f"   ⚠️  ERROR: {e}")
    
    print()

def demo_report_generation():
    print("📄 TESTING REPORT GENERATION")
    print("-" * 35)
    
    import subprocess
    import os
    
    os.chdir('/app')
    
    # Test security summary report
    print("1. Generating Security Summary Report")
    try:
        result = subprocess.run([
            'python', 'auditor/cli.py', 'generate-report',
            '--report-type', 'security_summary',
            '--time-range', '7d',
            '--format', 'markdown',
            '--save', '/tmp/phase9_security_report.md'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("   ✅ SUCCESS: Security summary report generated")
            
            # Check file exists
            if os.path.exists('/tmp/phase9_security_report.md'):
                with open('/tmp/phase9_security_report.md', 'r') as f:
                    content = f.read()
                    lines = len(content.split('\n'))
                    print(f"   📄 Report saved: {lines} lines, {len(content)} characters")
            else:
                print("   ⚠️  Report file not found")
        else:
            print(f"   ❌ FAILED: {result.stderr}")
    except Exception as e:
        print(f"   ⚠️  ERROR: {e}")
    
    # Test trends report
    print("2. Generating Vulnerability Trends Report")
    try:
        result = subprocess.run([
            'python', 'auditor/cli.py', 'generate-report',
            '--report-type', 'vulnerability_trends',
            '--time-range', '7d',
            '--format', 'json',
            '--save', '/tmp/phase9_trends_report.json'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("   ✅ SUCCESS: Trends report generated")
            
            if os.path.exists('/tmp/phase9_trends_report.json'):
                with open('/tmp/phase9_trends_report.json', 'r') as f:
                    data = json.load(f)
                    print(f"   📊 Data points: {len(data.get('trends_by_severity', {}))}")
            else:
                print("   ⚠️  Report file not found")
        else:
            print(f"   ❌ FAILED: {result.stderr}")
    except Exception as e:
        print(f"   ⚠️  ERROR: {e}")
    
    print()

def demo_export_functionality():
    print("📤 TESTING EXPORT FUNCTIONALITY")
    print("-" * 35)
    
    try:
        export_request = {
            "time_range": "7d",
            "format": "json",
            "include_trends": True,
            "include_repositories": True,
            "include_performance": True
        }
        
        response = requests.post(f"{API_BASE}/api/analytics/export", 
                               json=export_request)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS: Export initiated")
            print(f"   🆔 Export ID: {data['export_id']}")
            print(f"   📊 Status: {data['status']}")
        else:
            print(f"   ❌ FAILED: {response.status_code}")
            
    except Exception as e:
        print(f"   ⚠️  ERROR: {e}")
    
    print()

def demo_summary():
    print("🎯 PHASE 9 IMPLEMENTATION SUMMARY")
    print("-" * 40)
    print("✅ NEW API ENDPOINTS:")
    print("   • /api/analytics/trends/detailed - Advanced trend analysis")
    print("   • /api/analytics/top-rules - Most triggered vulnerability rules")
    print("   • /api/analytics/performance/detailed - Comprehensive performance metrics")
    print("   • /api/analytics/export - Enhanced data export")
    print("   • /api/analytics/alerts/configure - Alert configuration")
    print()
    print("✅ NEW CLI COMMANDS:")
    print("   • trends-detailed - Advanced trends with forecasting")
    print("   • top-rules - Vulnerability rule analysis")
    print("   • performance - Detailed performance insights")
    print("   • generate-report - Automated report generation")
    print()
    print("✅ ENHANCED FEATURES:")
    print("   • Report generation with multiple formats (Markdown, JSON, CSV)")
    print("   • Growth rate calculations and trend forecasting")
    print("   • Performance optimization recommendations")
    print("   • Enhanced data filtering and analysis")
    print("   • Export functionality with metadata")
    print()
    print("🚀 PHASE 9 SUCCESSFULLY IMPLEMENTED!")

def main():
    demo_header()
    demo_new_api_endpoints()
    demo_cli_commands()
    demo_report_generation()
    demo_export_functionality()
    demo_summary()
    
    print()
    print("=" * 80)
    print("🎉 PHASE 9 DEMONSTRATION COMPLETE!")
    print("The AI Code Security Auditor now includes advanced monitoring")
    print("and analytics capabilities for comprehensive security insights.")
    print("=" * 80)

if __name__ == "__main__":
    main()