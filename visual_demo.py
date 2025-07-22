#!/usr/bin/env python3
"""
CLI Visuals Demo - Showcase Phase 7C enhancements
"""

import sys
import os
sys.path.append('/app')

from cli_visuals.formatters import create_visual_formatter
from cli_visuals.terminal import terminal, ColorScheme


def demo_sparklines():
    """Demo sparkline charts"""
    print("🚀 Phase 7C Demo: Sparklines & Enhanced Charts")
    print("=" * 60)
    
    # Test different color schemes
    for scheme_name in ['default', 'security', 'monochrome', 'dark']:
        print(f"\n📊 {scheme_name.upper()} Color Scheme:")
        
        formatter = create_visual_formatter(scheme_name)
        
        # Sample vulnerability data over time
        vulnerability_counts = [2, 5, 8, 12, 15, 10, 7, 4, 6, 9, 11, 8, 5, 2]
        
        sparkline = formatter.sparkline.generate_sparkline(vulnerability_counts, 20)
        print(f"   Vulnerability Trend: {sparkline} (14 days)")
        
        # Critical vulnerabilities only
        critical_counts = [0, 1, 2, 3, 2, 1, 0, 0, 1, 2, 1, 0, 0, 0]
        critical_sparkline = formatter.sparkline.generate_sparkline(critical_counts, 20)
        print(f"   Critical Only:       {critical_sparkline} (14 days)")


def demo_enhanced_bars():
    """Demo enhanced bar charts"""
    print("\n🎯 Enhanced Bar Charts:")
    print("-" * 30)
    
    formatter = create_visual_formatter('security')
    
    # Severity distribution
    severity_data = {
        'CRITICAL': 8,
        'HIGH': 23, 
        'MEDIUM': 45,
        'LOW': 12,
        'INFO': 3
    }
    
    print("Vulnerability Severity Distribution:")
    bars = formatter.bar_chart.generate_severity_bars(severity_data, 35)
    for bar in bars:
        print(f"  {bar}")


def demo_pie_charts():
    """Demo pie chart representations"""
    print("\n🥧 ASCII Pie Charts:")
    print("-" * 25)
    
    formatter = create_visual_formatter('default')
    
    # File type distribution
    file_type_data = {
        'Python': 45,
        'JavaScript': 28,
        'Java': 15,
        'Go': 8,
        'Other': 4
    }
    
    print("Vulnerabilities by File Type:")
    pie_lines = formatter.pie_chart.generate_mini_pie(file_type_data)
    for line in pie_lines:
        print(f"  {line}")


def demo_gradient_heatmaps():
    """Demo gradient heatmaps"""
    print("\n🔥 Gradient Heatmaps:")
    print("-" * 25)
    
    formatter = create_visual_formatter('default')
    
    # Mock directory data
    class MockDir:
        def __init__(self, path, rule_hits, files_count):
            self.path = path
            self.rule_hits = rule_hits
            self.files_count = files_count
    
    mock_data = [
        MockDir("/app/src/core", 45, 20),
        MockDir("/app/src/api", 38, 15),
        MockDir("/app/src/utils", 25, 8),
        MockDir("/app/tests/unit", 18, 12),
        MockDir("/app/src/models", 15, 6),
        MockDir("/app/config", 8, 3),
        MockDir("/app/scripts", 5, 2)
    ]
    
    print("Directory Vulnerability Heatmap:")
    heatmap_lines = formatter.heatmap.generate_directory_heatmap(mock_data, 40)
    for line in heatmap_lines[:15]:  # Show first 15 lines
        print(f"  {line}")


def demo_interactive_features():
    """Demo interactive and navigation features"""
    print("\n🧭 Interactive Features:")
    print("-" * 30)
    
    formatter = create_visual_formatter('default')
    
    # Navigation hints
    nav_hints = formatter.interactive.generate_navigation_help()
    for hint in nav_hints:
        print(f"  {hint}")
    
    print()
    # Drill-down hints
    drill_hints = [
        formatter.interactive.generate_drill_down_hint('trend', '2024-01-15'),
        formatter.interactive.generate_drill_down_hint('heatmap', '/app/src'),
        formatter.interactive.generate_drill_down_hint('severity')
    ]
    
    for hint in drill_hints:
        print(f"  {hint}")


def demo_terminal_detection():
    """Demo terminal capability detection"""
    print("\n🖥️  Terminal Capabilities:")
    print("-" * 35)
    
    capabilities = terminal.test_capabilities()
    for key, value in capabilities.items():
        status = "✅" if value and value != "not set" else "❌"
        print(f"  {status} {key}: {value}")
    
    print(f"\n  Color Support: {'✅ 256-color' if terminal.supports_256_colors else '❌ Fallback mode'}")
    print(f"  Terminal Width: {terminal.terminal_width} characters")


def main():
    """Run all demos"""
    print("🎨 AI Code Security Auditor - Phase 7C Visual Demo")
    print("=" * 70)
    print("Enhanced CLI ASCII Charts & Heatmaps with Rich library integration")
    print()
    
    demo_terminal_detection()
    demo_sparklines()
    demo_enhanced_bars()
    demo_pie_charts()
    demo_gradient_heatmaps()
    demo_interactive_features()
    
    print("\n" + "=" * 70)
    print("🚀 Phase 7C Implementation Complete!")
    print("✨ Use --visual flag with CLI commands: trends, heatmap, summary")
    print("📚 Available color schemes: default, security, dark, monochrome")
    print("💡 Try: python auditor/cli.py visual-test --test-charts --test-colors")


if __name__ == '__main__':
    main()