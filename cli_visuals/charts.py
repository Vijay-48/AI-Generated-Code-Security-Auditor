"""
Chart Generation Module - Sparklines, Bar Charts, Pie Charts
"""

from typing import List, Dict, Any, Optional, Tuple
from rich.console import Console, RenderableType
from rich.text import Text
from rich.panel import Panel
from rich.columns import Columns
from rich.table import Table
from rich import box
import math
from .terminal import terminal, ColorScheme, get_gradient_colors, get_severity_colors


class SparklineChart:
    """Generate tiny inline sparklines for trend visualization"""
    
    def __init__(self, color_scheme: ColorScheme = ColorScheme.DEFAULT):
        self.console = Console()
        self.color_scheme = terminal.get_color_scheme(color_scheme)
        
        # Sparkline characters - various heights
        if self.color_scheme == ColorScheme.MONOCHROME:
            self.spark_chars = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
        else:
            # Use colored blocks for enhanced sparklines
            self.spark_chars = [
                '[bright_black]▁[/bright_black]',
                '[blue]▂[/blue]',
                '[cyan]▃[/cyan]',
                '[green]▄[/green]',
                '[yellow]▅[/yellow]',
                '[orange1]▆[/orange1]',
                '[red]▇[/red]',
                '[bright_red]█[/bright_red]'
            ]
    
    def generate_sparkline(self, values: List[float], width: int = 20) -> str:
        """Generate a sparkline from data values"""
        if not values:
            return "No data"
        
        if len(values) == 1:
            return self.spark_chars[-1] if values[0] > 0 else self.spark_chars[0]
        
        # Normalize values to sparkline character range
        min_val = min(values)
        max_val = max(values) 
        
        if max_val == min_val:
            # All values are the same
            mid_char = self.spark_chars[len(self.spark_chars) // 2]
            return mid_char * min(width, len(values))
        
        # Scale values to character indices
        sparkline = []
        values_to_show = values[-width:] if len(values) > width else values
        
        for value in values_to_show:
            normalized = (value - min_val) / (max_val - min_val)
            char_index = min(len(self.spark_chars) - 1, int(normalized * (len(self.spark_chars) - 1)))
            sparkline.append(self.spark_chars[char_index])
        
        return ''.join(sparkline)
    
    def generate_trend_sparkline(self, trend_data: List[Dict], field: str = 'total_vulnerabilities') -> str:
        """Generate sparkline from trend data"""
        values = [getattr(trend, field, 0) for trend in trend_data]
        return self.generate_sparkline(values)


class BarChart:
    """Generate horizontal bar charts with various styles"""
    
    def __init__(self, color_scheme: ColorScheme = ColorScheme.DEFAULT):
        self.console = Console()
        self.color_scheme = terminal.get_color_scheme(color_scheme)
        self.severity_colors = get_severity_colors()
    
    def generate_horizontal_bar(self, value: float, max_value: float, width: int = 40, 
                               show_percentage: bool = True, severity: str = None) -> str:
        """Generate a single horizontal bar"""
        if max_value == 0:
            return '░' * width + ' 0%'
        
        percentage = (value / max_value) * 100
        filled_width = int((value / max_value) * width)
        
        if self.color_scheme == ColorScheme.MONOCHROME:
            bar = '█' * filled_width + '░' * (width - filled_width)
        else:
            # Use colors based on severity if provided
            if severity and severity.upper() in self.severity_colors:
                color = self.severity_colors[severity.upper()]
                bar = f"{color}{'█' * filled_width}[/{color.strip('[]')}]" + '░' * (width - filled_width)
            else:
                # Default gradient coloring
                bar = '[bright_blue]' + '█' * filled_width + '[/bright_blue]' + '░' * (width - filled_width)
        
        if show_percentage:
            return f"{bar} {percentage:5.1f}%"
        else:
            return bar
    
    def generate_severity_bars(self, severity_counts: Dict[str, int], width: int = 40) -> List[str]:
        """Generate bars for vulnerability severity distribution"""
        if not severity_counts:
            return ["No data available"]
        
        max_count = max(severity_counts.values())
        bars = []
        
        # Order by severity (most critical first)
        severity_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']
        
        for severity in severity_order:
            count = severity_counts.get(severity, 0)
            if count > 0:  # Only show severities with findings
                bar = self.generate_horizontal_bar(count, max_count, width, True, severity)
                bars.append(f"{severity:<8} {bar} ({count})")
        
        return bars
    
    def generate_trend_bars(self, trend_data: List[Dict], width: int = 50) -> List[str]:
        """Generate trend bars showing vulnerability counts over time"""
        if not trend_data:
            return ["No trend data available"]
        
        max_vulns = max(getattr(t, 'total_vulnerabilities', 0) for t in trend_data[-10:])  # Last 10 days
        bars = []
        
        for trend in trend_data[-10:]:  # Show last 10 days
            count = getattr(trend, 'total_vulnerabilities', 0)
            date = getattr(trend, 'date', 'Unknown')
            
            bar = self.generate_horizontal_bar(count, max_vulns, width, False)
            bars.append(f"{str(date):<12} |{bar}| {count:>4}")
        
        return bars


class PieChart:
    """Generate ASCII pie charts using block characters"""
    
    def __init__(self, color_scheme: ColorScheme = ColorScheme.DEFAULT):
        self.console = Console()
        self.color_scheme = terminal.get_color_scheme(color_scheme)
        self.severity_colors = get_severity_colors()
    
    def generate_pie_slice(self, percentage: float, total_chars: int = 8) -> str:
        """Generate a pie chart slice representation"""
        # Pie slice characters in clockwise order
        if self.color_scheme == ColorScheme.MONOCHROME:
            slice_chars = ['○', '◔', '◑', '◕', '●']
        else:
            slice_chars = [
                '[bright_black]○[/bright_black]',  # Empty
                '[blue]◔[/blue]',                  # Quarter  
                '[yellow]◑[/yellow]',              # Half
                '[orange1]◕[/orange1]',            # Three quarters
                '[red]●[/red]'                     # Full
            ]
        
        if percentage <= 0:
            return slice_chars[0]
        elif percentage <= 25:
            return slice_chars[1] 
        elif percentage <= 50:
            return slice_chars[2]
        elif percentage <= 75:
            return slice_chars[3]
        else:
            return slice_chars[4]
    
    def generate_mini_pie(self, data: Dict[str, int], size: int = 3) -> List[str]:
        """Generate a mini pie chart using block characters"""
        if not data:
            return ["No data"]
        
        total = sum(data.values())
        if total == 0:
            return ["No data"]
        
        lines = []
        lines.append("┌─────┐")
        
        # Create a simple 3x3 grid representation
        grid = [['░' for _ in range(size)] for _ in range(size)]
        
        # Fill grid based on data percentages
        filled_cells = 0
        total_cells = size * size
        
        # Sort by value (largest first) for better visual distribution  
        sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
        
        for label, count in sorted_items:
            percentage = (count / total) * 100
            cells_to_fill = int((count / total) * total_cells)
            
            # Fill cells in spiral pattern
            for _ in range(min(cells_to_fill, total_cells - filled_cells)):
                row = filled_cells // size
                col = filled_cells % size
                if row < size and col < size:
                    if self.color_scheme != ColorScheme.MONOCHROME and label.upper() in self.severity_colors:
                        color = self.severity_colors[label.upper()]
                        grid[row][col] = f"{color}█[/{color.strip('[]')}]"
                    else:
                        grid[row][col] = '█'
                filled_cells += 1
        
        # Convert grid to strings
        for row in grid:
            lines.append("│" + "".join(row) + "│")
        
        lines.append("└─────┘")
        
        # Add legend
        lines.append("")
        for label, count in sorted_items:
            percentage = (count / total) * 100
            symbol = self.generate_pie_slice(percentage)
            lines.append(f"{symbol} {label}: {count} ({percentage:.1f}%)")
        
        return lines
    
    def generate_severity_pie(self, severity_counts: Dict[str, int]) -> List[str]:
        """Generate pie chart specifically for severity distribution"""
        return self.generate_mini_pie(severity_counts)


class InteractiveChart:
    """Interactive chart features - drill-down and navigation"""
    
    def __init__(self):
        self.console = Console()
    
    def generate_drill_down_hint(self, data_type: str, identifier: str = None) -> str:
        """Generate hint for drilling down into data"""
        hints = {
            'trend': f"💡 Drill down: Use 'auditor summary --scan-id {identifier}' for details",
            'heatmap': f"💡 Drill down: Use 'auditor scan --path {identifier}' to rescan directory", 
            'severity': "💡 Drill down: Use 'auditor scan --severity-filter high' to focus on critical issues"
        }
        
        return hints.get(data_type, "💡 Use --help for more options")
    
    def generate_navigation_help(self) -> List[str]:
        """Generate help text for chart navigation"""
        return [
            "🧭 Navigation Tips:",
            "  • Use --limit to control data range",
            "  • Use --since/--until for date filtering", 
            "  • Use --save to export data",
            "  • Use --output json/csv for programmatic access"
        ]