"""
Advanced ASCII Visualizations and Charts for CLI
Beautiful terminal graphics using Rich and custom ASCII art
"""
import math
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timedelta

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.bar import Bar
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    from rich.text import Text
    from rich.layout import Layout
    from rich.align import Align
    from rich.rule import Rule
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from app.models.analytics import (
    ScanHistoryEntry, ScanSummary, TrendDataPoint, 
    HeatmapEntry, RepositoryStats, VulnerabilityDistribution
)


class VisualComponents:
    """Advanced visualization components for CLI output"""
    
    def __init__(self, use_rich: bool = None):
        self.use_rich = RICH_AVAILABLE if use_rich is None else (use_rich and RICH_AVAILABLE)
        if self.use_rich:
            self.console = Console()
        
        # Define severity colors for different terminals
        self.colors = {
            'critical': '#FF0000',  # Bright red
            'high': '#FF6600',      # Orange  
            'medium': '#FFAA00',    # Yellow
            'low': '#00AA00',       # Green
            'info': '#0066FF',      # Blue
            'neutral': '#888888'    # Gray
        }
        
        # ASCII fallback colors
        self.ascii_colors = {
            'critical': '🔴',
            'high': '🟠', 
            'medium': '🟡',
            'low': '🟢',
            'info': '🔵',
            'neutral': '⚪'
        }
    
    def create_sparkline(self, data: List[float], width: int = 20, height: int = 8) -> str:
        """Create a sparkline chart from data points"""
        if not data:
            return "No data"
        
        if self.use_rich:
            return self._create_rich_sparkline(data, width, height)
        else:
            return self._create_ascii_sparkline(data, width)
    
    def _create_rich_sparkline(self, data: List[float], width: int, height: int) -> str:
        """Create sparkline using Rich"""
        if not data:
            return ""
        
        min_val = min(data)
        max_val = max(data)
        
        if min_val == max_val:
            return "▄" * min(len(data), width)
        
        # Normalize data to height levels
        normalized = []
        for val in data:
            level = int(((val - min_val) / (max_val - min_val)) * (height - 1))
            normalized.append(level)
        
        # Use block characters for different heights
        chars = [" ", "▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        
        result = ""
        for level in normalized[-width:]:  # Take last 'width' points
            char_idx = min(level, len(chars) - 1)
            result += chars[char_idx]
        
        return result
    
    def _create_ascii_sparkline(self, data: List[float], width: int) -> str:
        """Create simple ASCII sparkline"""
        if not data:
            return ""
        
        min_val = min(data)
        max_val = max(data)
        
        if min_val == max_val:
            return "─" * min(len(data), width)
        
        chars = ["_", "▁", "▃", "▅", "▇", "█"]
        result = ""
        
        for val in data[-width:]:
            level = int(((val - min_val) / (max_val - min_val)) * (len(chars) - 1))
            result += chars[level]
        
        return result
    
    def create_horizontal_bar_chart(self, data: Dict[str, int], width: int = 40, show_values: bool = True) -> str:
        """Create horizontal bar chart"""
        if not data:
            return "No data"
        
        if self.use_rich:
            return self._create_rich_bar_chart(data, width, show_values)
        else:
            return self._create_ascii_bar_chart(data, width, show_values)
    
    def _create_rich_bar_chart(self, data: Dict[str, int], width: int, show_values: bool) -> str:
        """Create bar chart using Rich"""
        if not data:
            return ""
        
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Label", style="bold", min_width=12)
        table.add_column("Bar", min_width=width)
        table.add_column("Value", justify="right", min_width=6)
        
        max_val = max(data.values()) if data else 1
        
        for label, value in data.items():
            # Calculate bar length
            bar_length = int((value / max_val) * width) if max_val > 0 else 0
            
            # Create colored bar based on severity
            color = self._get_severity_color(label.lower())
            bar = Text("█" * bar_length, style=color)
            
            # Add empty space
            if bar_length < width:
                bar.append(" " * (width - bar_length), style="dim")
            
            value_text = str(value) if show_values else ""
            table.add_row(label.title(), bar, value_text)
        
        return table
    
    def _create_ascii_bar_chart(self, data: Dict[str, int], width: int, show_values: bool) -> str:
        """Create ASCII bar chart"""
        lines = []
        max_val = max(data.values()) if data else 1
        
        for label, value in data.items():
            bar_length = int((value / max_val) * width) if max_val > 0 else 0
            bar = "█" * bar_length + "░" * (width - bar_length)
            
            emoji = self.ascii_colors.get(label.lower(), '⚪')
            value_str = f" {value}" if show_values else ""
            
            lines.append(f"{emoji} {label.title():<10} |{bar}|{value_str}")
        
        return "\n".join(lines)
    
    def create_gradient_heatmap(self, heatmap_data: List[HeatmapEntry], width: int = 50, max_entries: int = 15) -> str:
        """Create gradient heatmap with color intensity"""
        if not heatmap_data:
            return "No heatmap data"
        
        if self.use_rich:
            return self._create_rich_heatmap(heatmap_data, width, max_entries)
        else:
            return self._create_ascii_heatmap(heatmap_data, width, max_entries)
    
    def _create_rich_heatmap(self, heatmap_data: List[HeatmapEntry], width: int, max_entries: int) -> str:
        """Create heatmap using Rich with gradient colors"""
        table = Table(title="🗺️  Security Heatmap - Rule Hits by Directory", box=box.ROUNDED)
        table.add_column("Directory", style="bold cyan", min_width=25)
        table.add_column("Heat Map", min_width=width - 10)
        table.add_column("Hits", justify="right", style="bold")
        table.add_column("Files", justify="center", style="dim")
        
        max_hits = max(entry.rule_hits for entry in heatmap_data) if heatmap_data else 1
        
        for entry in heatmap_data[:max_entries]:
            # Calculate intensity (0-1)
            intensity = entry.rule_hits / max_hits if max_hits > 0 else 0
            
            # Create gradient bar
            bar_length = int((entry.rule_hits / max_hits) * (width - 20)) if max_hits > 0 else 0
            
            # Use different colors based on intensity
            if intensity >= 0.8:
                color = "red"
                char = "█"
            elif intensity >= 0.6:
                color = "red3" 
                char = "▓"
            elif intensity >= 0.4:
                color = "orange1"
                char = "▒"
            elif intensity >= 0.2:
                color = "yellow"
                char = "░"
            else:
                color = "green"
                char = "·"
            
            heat_bar = Text(char * bar_length, style=color)
            heat_bar.append("·" * (width - 20 - bar_length), style="dim")
            
            # Truncate path for display
            path_display = entry.path if len(entry.path) <= 23 else "..." + entry.path[-20:]
            
            table.add_row(
                path_display,
                heat_bar,
                str(entry.rule_hits),
                f"({entry.files_count})"
            )
        
        return table
    
    def _create_ascii_heatmap(self, heatmap_data: List[HeatmapEntry], width: int, max_entries: int) -> str:
        """Create ASCII heatmap"""
        lines = []
        lines.append("🗺️  Security Heatmap - Rule Hits by Directory")
        lines.append("=" * (width + 20))
        
        max_hits = max(entry.rule_hits for entry in heatmap_data) if heatmap_data else 1
        
        lines.append("Legend: 🔥 Very High  🟠 High  🟡 Medium  🟢 Low  ⚪ Minimal")
        lines.append(f"Max hits: {max_hits}")
        lines.append("")
        
        for entry in heatmap_data[:max_entries]:
            intensity = entry.rule_hits / max_hits if max_hits > 0 else 0
            
            # Choose emoji based on intensity
            if intensity >= 0.8:
                emoji = "🔥"
            elif intensity >= 0.6:
                emoji = "🟠"
            elif intensity >= 0.4:
                emoji = "🟡"
            elif intensity >= 0.2:
                emoji = "🟢"
            else:
                emoji = "⚪"
            
            bar_length = int((entry.rule_hits / max_hits) * (width - 25)) if max_hits > 0 else 0
            bar = "█" * bar_length + "·" * (width - 25 - bar_length)
            
            path_display = entry.path if len(entry.path) <= 22 else "..." + entry.path[-19:]
            lines.append(f"{emoji} {path_display:<22} |{bar}| {entry.rule_hits:>4} ({entry.files_count})")
        
        return "\n".join(lines)
    
    def create_pie_chart_text(self, data: Dict[str, int], total: Optional[int] = None) -> str:
        """Create text-based pie chart representation"""
        if not data:
            return "No data"
        
        if total is None:
            total = sum(data.values())
        
        if total == 0:
            return "No data to display"
        
        lines = []
        
        if self.use_rich:
            # Create a more visual representation with Rich
            table = Table(title="📊 Vulnerability Distribution", box=box.ROUNDED)
            table.add_column("Severity", style="bold")
            table.add_column("Count", justify="right")
            table.add_column("Percentage", justify="right")
            table.add_column("Visual", min_width=20)
            
            for severity, count in data.items():
                percentage = (count / total) * 100 if total > 0 else 0
                
                # Create visual bar
                bar_length = int((count / total) * 15) if total > 0 else 0
                color = self._get_severity_color(severity.lower())
                
                visual_bar = Text("█" * bar_length, style=color)
                visual_bar.append("░" * (15 - bar_length), style="dim")
                
                table.add_row(
                    severity.title(),
                    str(count),
                    f"{percentage:.1f}%",
                    visual_bar
                )
            
            return table
        else:
            lines.append("📊 Vulnerability Distribution")
            lines.append("-" * 40)
            
            for severity, count in data.items():
                percentage = (count / total) * 100 if total > 0 else 0
                emoji = self.ascii_colors.get(severity.lower(), '⚪')
                
                # Create simple bar
                bar_length = int((count / total) * 15) if total > 0 else 0
                bar = "█" * bar_length + "░" * (15 - bar_length)
                
                lines.append(f"{emoji} {severity.title():<8} {count:>4} ({percentage:>5.1f}%) |{bar}|")
            
            return "\n".join(lines)
    
    def create_trend_chart(self, trend_data: List[TrendDataPoint], width: int = 60, height: int = 10) -> str:
        """Create detailed trend chart with multiple data series"""
        if not trend_data:
            return "No trend data"
        
        if self.use_rich:
            return self._create_rich_trend_chart(trend_data, width, height)
        else:
            return self._create_ascii_trend_chart(trend_data, width, height)
    
    def _create_rich_trend_chart(self, trend_data: List[TrendDataPoint], width: int, height: int) -> str:
        """Create rich trend chart with multiple series"""
        
        # Create main layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="chart", size=height + 5),
            Layout(name="legend", size=4)
        )
        
        # Header
        layout["header"].update(
            Panel(
                Align.center(f"📈 Vulnerability Trends ({len(trend_data)} days)"),
                style="bold blue"
            )
        )
        
        # Create chart table
        chart_table = Table(show_header=False, box=None, padding=0)
        chart_table.add_column("Date", min_width=12)
        chart_table.add_column("Chart", min_width=width)
        chart_table.add_column("Total", justify="right", min_width=8)
        
        # Get max values for scaling
        max_total = max(t.total_vulnerabilities for t in trend_data) if trend_data else 1
        max_critical = max(t.critical for t in trend_data) if trend_data else 1
        
        for trend in trend_data[-10:]:  # Show last 10 days
            date_str = trend.date
            
            # Create stacked bar
            total_bar_length = int((trend.total_vulnerabilities / max_total) * width) if max_total > 0 else 0
            
            # Calculate proportions
            total = trend.total_vulnerabilities
            if total > 0:
                critical_len = int((trend.critical / total) * total_bar_length)
                high_len = int((trend.high / total) * total_bar_length)
                medium_len = int((trend.medium / total) * total_bar_length)
                low_len = total_bar_length - critical_len - high_len - medium_len
            else:
                critical_len = high_len = medium_len = low_len = 0
            
            # Create colored bar
            bar = Text()
            if critical_len > 0:
                bar.append("█" * critical_len, style="red")
            if high_len > 0:
                bar.append("█" * high_len, style="orange1")
            if medium_len > 0:
                bar.append("█" * medium_len, style="yellow")
            if low_len > 0:
                bar.append("█" * low_len, style="green")
            
            # Add empty space
            empty_len = width - total_bar_length
            if empty_len > 0:
                bar.append("░" * empty_len, style="dim")
            
            chart_table.add_row(date_str, bar, str(trend.total_vulnerabilities))
        
        layout["chart"].update(chart_table)
        
        # Legend
        legend_table = Table(show_header=False, box=None)
        legend_table.add_column("Legend", justify="center")
        legend_items = [
            Text("🔴 Critical  🟠 High  🟡 Medium  🟢 Low", justify="center")
        ]
        legend_table.add_row(legend_items[0])
        layout["legend"].update(legend_table)
        
        return layout
    
    def _create_ascii_trend_chart(self, trend_data: List[TrendDataPoint], width: int, height: int) -> str:
        """Create ASCII trend chart"""
        lines = []
        lines.append(f"📈 Vulnerability Trends ({len(trend_data)} days)")
        lines.append("=" * (width + 20))
        
        max_val = max(t.total_vulnerabilities for t in trend_data) if trend_data else 1
        
        lines.append(f"Scale: Max {max_val} vulnerabilities")
        lines.append("Legend: 🔴 Critical  🟠 High  🟡 Medium  🟢 Low")
        lines.append("")
        
        for trend in trend_data[-10:]:
            bar_length = int((trend.total_vulnerabilities / max_val) * width) if max_val > 0 else 0
            
            # Simple stacked representation
            total = trend.total_vulnerabilities
            if total > 0:
                critical_ratio = trend.critical / total
                high_ratio = trend.high / total
                medium_ratio = trend.medium / total
                
                # Use different characters to represent different severities
                bar = ""
                for i in range(bar_length):
                    pos = i / bar_length if bar_length > 0 else 0
                    if pos < critical_ratio:
                        bar += "█"
                    elif pos < critical_ratio + high_ratio:
                        bar += "▓"
                    elif pos < critical_ratio + high_ratio + medium_ratio:
                        bar += "▒"
                    else:
                        bar += "░"
            else:
                bar = "·" * bar_length
            
            bar += "·" * (width - bar_length)
            lines.append(f"{trend.date} |{bar}| {total:>3}")
        
        return "\n".join(lines)
    
    def create_summary_dashboard(self, summary: ScanSummary, show_charts: bool = True) -> str:
        """Create comprehensive summary dashboard"""
        if not self.use_rich:
            return self._create_ascii_summary_dashboard(summary, show_charts)
        
        # Create main layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=4),
            Layout(name="content")
        )
        
        # Header with scan info
        header_table = Table(show_header=False, box=None)
        header_table.add_column("Key", style="bold cyan")
        header_table.add_column("Value")
        
        header_table.add_row("🔍 Scan ID:", summary.scan_id)
        header_table.add_row("📅 Timestamp:", summary.timestamp.strftime('%Y-%m-%d %H:%M:%S'))
        if summary.repository:
            header_table.add_row("📁 Repository:", summary.repository)
        header_table.add_row("📊 Security Score:", f"{summary.security_score:.1f}/100")
        
        layout["header"].update(Panel(header_table, title="Scan Overview", border_style="blue"))
        
        # Content area
        layout["content"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1)
        )
        
        # Left: Vulnerability breakdown
        vuln_data = {
            'critical': summary.critical_count,
            'high': summary.high_count,
            'medium': summary.medium_count,
            'low': summary.low_count
        }
        
        if show_charts:
            pie_chart = self.create_pie_chart_text(vuln_data)
            layout["left"].update(Panel(pie_chart, title="Vulnerability Distribution", border_style="yellow"))
        
        # Right: Top rules
        if summary.top_rules:
            rules_table = Table(title="🎯 Top Security Issues", box=box.SIMPLE)
            rules_table.add_column("Rule", style="bold")
            rules_table.add_column("Severity")
            rules_table.add_column("Hits", justify="right")
            
            for rule in summary.top_rules[:5]:
                severity_color = self._get_severity_color(rule['severity'])
                rules_table.add_row(
                    rule['rule_name'],
                    Text(rule['severity'].title(), style=severity_color),
                    str(rule['hits'])
                )
            
            layout["right"].update(Panel(rules_table, border_style="green"))
        
        return layout
    
    def _create_ascii_summary_dashboard(self, summary: ScanSummary, show_charts: bool) -> str:
        """ASCII version of summary dashboard"""
        lines = []
        lines.append("🔍 Security Audit Summary Dashboard")
        lines.append("=" * 60)
        
        lines.append(f"Scan ID: {summary.scan_id}")
        lines.append(f"Timestamp: {summary.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        if summary.repository:
            lines.append(f"Repository: {summary.repository}")
        lines.append(f"Security Score: {summary.security_score:.1f}/100")
        lines.append("")
        
        if show_charts:
            vuln_data = {
                'critical': summary.critical_count,
                'high': summary.high_count,
                'medium': summary.medium_count,
                'low': summary.low_count
            }
            pie_chart = self.create_pie_chart_text(vuln_data)
            lines.append(pie_chart)
            lines.append("")
        
        if summary.top_rules:
            lines.append("🎯 Top Security Issues:")
            for i, rule in enumerate(summary.top_rules[:5], 1):
                emoji = self.ascii_colors.get(rule['severity'].lower(), '⚪')
                lines.append(f"  {i}. {emoji} {rule['rule_name']} ({rule['severity']}) - {rule['hits']} hits")
        
        return "\n".join(lines)
    
    def _get_severity_color(self, severity: str) -> str:
        """Get Rich color style for severity level"""
        color_map = {
            'critical': 'red',
            'high': 'orange1', 
            'medium': 'yellow',
            'low': 'green',
            'info': 'blue'
        }
        return color_map.get(severity.lower(), 'white')
    
    def print_rich_output(self, content) -> None:
        """Print content using Rich console"""
        if self.use_rich and hasattr(self, 'console'):
            self.console.print(content)
        else:
            print(str(content))
    
    def create_progress_bar(self, description: str = "Processing"):
        """Create a Rich progress bar"""
        if not self.use_rich:
            return None
        
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        )


# Global instance
visual_components = VisualComponents()