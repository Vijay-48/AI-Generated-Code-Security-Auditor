"""
Visual Formatter - Integrates all visual components with CLI output
"""

from typing import List, Dict, Any, Optional
from rich.console import Console, Group
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich import box

from .charts import SparklineChart, BarChart, PieChart, InteractiveChart
from .heatmap import GradientHeatmap
from .terminal import terminal, ColorScheme


class VisualFormatter:
    """Main formatter that combines all visual elements"""
    
    def __init__(self, color_scheme: ColorScheme = ColorScheme.DEFAULT, no_colors: bool = False):
        self.console = Console()
        self.color_scheme = terminal.get_color_scheme(color_scheme, no_colors)
        
        # Initialize visual components
        self.sparkline = SparklineChart(self.color_scheme)
        self.bar_chart = BarChart(self.color_scheme)
        self.pie_chart = PieChart(self.color_scheme)
        self.heatmap = GradientHeatmap(self.color_scheme)
        self.interactive = InteractiveChart()
    
    def format_trends_visual(self, trend_data: List[Any], width: int = 40) -> str:
        """Enhanced trends visualization with sparklines and bars"""
        if not trend_data:
            return "No trend data available for visualization"
        
        lines = []
        
        # Header with sparkline summary
        sparkline = self.sparkline.generate_trend_sparkline(trend_data)
        lines.append(f"📈 Vulnerability Trends {sparkline}")
        lines.append("=" * 80)
        
        # Show recent trend with bars
        trend_bars = self.bar_chart.generate_trend_bars(trend_data, width)
        lines.extend(trend_bars)
        
        # Summary statistics with mini sparklines
        lines.append("")
        lines.append("📊 Trend Analysis:")
        
        # Critical vulnerabilities sparkline
        critical_values = [getattr(t, 'critical', 0) for t in trend_data[-14:]]
        critical_sparkline = self.sparkline.generate_sparkline(critical_values, 20)
        lines.append(f"   Critical:  {critical_sparkline} (last 14 days)")
        
        # High vulnerabilities sparkline
        high_values = [getattr(t, 'high', 0) for t in trend_data[-14:]]
        high_sparkline = self.sparkline.generate_sparkline(high_values, 20)
        lines.append(f"   High:      {high_sparkline} (last 14 days)")
        
        # Add interactive hint
        lines.append("")
        lines.append(self.interactive.generate_drill_down_hint('trend'))
        
        return "\n".join(lines)
    
    def format_heatmap_visual(self, heatmap_data: List[Any], width: int = 50) -> str:
        """Enhanced heatmap visualization with gradient colors"""
        if not heatmap_data:
            return "No heatmap data available for visualization"
        
        lines = []
        
        # Generate main directory heatmap
        heatmap_lines = self.heatmap.generate_directory_heatmap(heatmap_data, width)
        lines.extend(heatmap_lines)
        
        # Add navigation help
        lines.append("")
        nav_help = self.interactive.generate_navigation_help()
        lines.extend(nav_help)
        
        return "\n".join(lines)
    
    def format_summary_visual(self, summary_data: Dict[str, Any]) -> str:
        """Enhanced summary with pie charts and severity bars"""
        if not summary_data:
            return "No summary data available for visualization"
        
        lines = []
        lines.append("🛡️  Security Audit Summary - Visual Dashboard")
        lines.append("=" * 80)
        
        # Extract severity distribution
        severity_counts = summary_data.get('severity_distribution', {})
        
        if severity_counts:
            # Generate severity bars
            lines.append("\n📊 Vulnerability Severity Distribution:")
            severity_bars = self.bar_chart.generate_severity_bars(severity_counts, 40)
            for bar in severity_bars:
                lines.append(f"   {bar}")
            
            # Generate mini pie chart
            lines.append("\n🥧 Severity Distribution (Pie Chart):")
            pie_lines = self.pie_chart.generate_severity_pie(severity_counts)
            for pie_line in pie_lines:
                lines.append(f"   {pie_line}")
        
        # Add scan statistics with sparklines if available
        scan_stats = summary_data.get('scan_statistics', {})
        if scan_stats:
            lines.append("\n📈 Scan Activity:")
            total_scans = scan_stats.get('total_scans', 0)
            lines.append(f"   Total Scans: {total_scans}")
            
            # If we have historical data, show sparkline
            if 'recent_activity' in scan_stats:
                recent_activity = scan_stats['recent_activity']
                activity_sparkline = self.sparkline.generate_sparkline(recent_activity, 15)
                lines.append(f"   Recent Activity: {activity_sparkline}")
        
        # File type distribution heatmap if available
        file_types = summary_data.get('file_type_distribution', {})
        if file_types:
            lines.append("\n📁 File Type Vulnerability Heatmap:")
            file_heatmap = self.heatmap.generate_file_type_heatmap(file_types, 30)
            for hm_line in file_heatmap:
                lines.append(f"   {hm_line}")
        
        # Add interactive hints
        lines.append("")
        lines.append(self.interactive.generate_drill_down_hint('severity'))
        
        return "\n".join(lines)
    
    def format_terminal_info(self) -> str:
        """Display terminal capabilities for debugging"""
        lines = []
        lines.append("🖥️  Terminal Capabilities Report")
        lines.append("=" * 50)
        
        capabilities = terminal.test_capabilities()
        for key, value in capabilities.items():
            lines.append(f"   {key}: {value}")
        
        lines.append(f"\n   Selected color scheme: {self.color_scheme.value}")
        lines.append(f"   Visual enhancements: {'✅ Enabled' if terminal.supports_256_colors else '❌ Disabled (fallback mode)'}")
        
        return "\n".join(lines)
    
    def create_visual_panel(self, title: str, content: str, 
                           style: str = "blue") -> Panel:
        """Create a Rich panel for visual content"""
        return Panel(
            content,
            title=f"[bold {style}]{title}[/bold {style}]",
            border_style=style,
            box=box.ROUNDED
        )
    
    def create_dashboard_layout(self, components: List[str]) -> str:
        """Create a dashboard-style layout with multiple visual components"""
        # This could be expanded to create multi-column layouts
        return "\n\n".join(components)


def create_visual_formatter(color_scheme: str = "default", no_colors: bool = False) -> VisualFormatter:
    """Factory function to create visual formatter with proper color scheme"""
    scheme_map = {
        'default': ColorScheme.DEFAULT,
        'monochrome': ColorScheme.MONOCHROME,
        'dark': ColorScheme.DARK,
        'security': ColorScheme.SECURITY
    }
    
    scheme = scheme_map.get(color_scheme.lower(), ColorScheme.DEFAULT)
    return VisualFormatter(scheme, no_colors)