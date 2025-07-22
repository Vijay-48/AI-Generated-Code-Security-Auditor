"""
Enhanced Gradient Heatmaps with ANSI 256-color support
"""

from typing import List, Dict, Any, Optional, Tuple
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
import math
from .terminal import terminal, ColorScheme, get_gradient_colors


class GradientHeatmap:
    """Generate advanced gradient heatmaps with rich color support"""
    
    def __init__(self, color_scheme: ColorScheme = ColorScheme.DEFAULT):
        self.console = Console()
        self.color_scheme = terminal.get_color_scheme(color_scheme)
        self.gradient_colors = get_gradient_colors(self.color_scheme)
    
    def calculate_intensity_level(self, value: float, max_value: float, levels: int = 8) -> int:
        """Calculate intensity level for gradient mapping"""
        if max_value == 0:
            return 0
        
        normalized = min(1.0, value / max_value)
        level = int(normalized * (levels - 1))
        return min(level, levels - 1)
    
    def get_heat_character(self, intensity_level: int) -> str:
        """Get character/color for given intensity level"""
        if self.color_scheme == ColorScheme.MONOCHROME:
            chars = ['·', '░', '▒', '▓', '█', '█', '█', '█']
            return chars[min(intensity_level, len(chars) - 1)]
        else:
            # Use gradient colors from terminal.py
            if intensity_level < len(self.gradient_colors):
                return self.gradient_colors[intensity_level]
            else:
                return self.gradient_colors[-1]  # Use highest intensity
    
    def generate_directory_heatmap(self, heatmap_data: List[Any], 
                                  width: int = 50, max_path_length: int = 30) -> List[str]:
        """Generate enhanced directory heatmap with gradient colors"""
        if not heatmap_data:
            return ["No heatmap data available"]
        
        lines = []
        
        # Calculate max hits for intensity scaling
        max_hits = max(getattr(entry, 'rule_hits', 0) for entry in heatmap_data) or 1
        
        # Header with enhanced styling
        lines.append("🔥 Security Heatmap - Vulnerability Density by Directory")
        lines.append("=" * (width + 35))
        
        # Legend for gradient
        if self.color_scheme == ColorScheme.MONOCHROME:
            legend = "Legend: · (min) ░ ▒ ▓ █ (max)"
        else:
            legend_chars = []
            for i in range(0, len(self.gradient_colors), 2):  # Sample every 2nd color
                legend_chars.append(self.gradient_colors[i])
            legend = f"Legend: {' '.join(legend_chars)} (intensity: low → high)"
        
        lines.append(legend)
        lines.append(f"Max hits per directory: {max_hits}")
        lines.append("")
        
        # Generate heatmap bars
        for entry in heatmap_data[:20]:  # Limit to top 20 directories
            hits = getattr(entry, 'rule_hits', 0)
            files_count = getattr(entry, 'files_count', 0)
            path = getattr(entry, 'path', 'unknown')
            
            # Calculate intensity and get appropriate character
            intensity = self.calculate_intensity_level(hits, max_hits)
            heat_char = self.get_heat_character(intensity)
            
            # Create heat bar
            bar_length = int((hits / max_hits) * (width - 30)) if max_hits > 0 else 0
            heat_bar = heat_char * bar_length
            
            # Pad remaining space with cool characters
            remaining_space = (width - 30) - bar_length
            if remaining_space > 0:
                cool_char = self.get_heat_character(0)  # Coolest character
                if self.color_scheme != ColorScheme.MONOCHROME:
                    cool_char = '[bright_black]·[/bright_black]'
                heat_bar += cool_char * remaining_space
            
            # Format path for display
            display_path = path
            if len(display_path) > max_path_length:
                display_path = "..." + display_path[-(max_path_length-3):]
            
            # Generate line with proper spacing
            line = f"{display_path:<{max_path_length}} │{heat_bar}│ {hits:>4} hits ({files_count} files)"
            lines.append(line)
        
        # Add summary statistics
        total_hits = sum(getattr(entry, 'rule_hits', 0) for entry in heatmap_data)
        total_dirs = len(heatmap_data)
        avg_hits = total_hits / total_dirs if total_dirs > 0 else 0
        
        lines.append("")
        lines.append("📊 Heatmap Summary:")
        lines.append(f"   Total Directories: {total_dirs}")
        lines.append(f"   Total Rule Hits: {total_hits}")
        lines.append(f"   Average Hits/Dir: {avg_hits:.1f}")
        
        return lines
    
    def generate_time_heatmap(self, time_data: List[Dict], hours_width: int = 24) -> List[str]:
        """Generate time-based heatmap showing activity patterns"""
        if not time_data:
            return ["No time data available"]
        
        lines = []
        lines.append("⏰ Temporal Heatmap - Activity by Hour")
        lines.append("=" * 60)
        
        # Create 24-hour grid (if we had hourly data)
        # For now, create a demo pattern
        hours = list(range(24))
        
        # Mock data - in real implementation, this would come from time_data
        activity_levels = [
            0, 0, 0, 0, 0, 0, 1, 2, 4, 5, 6, 7,  # Morning ramp-up
            8, 8, 7, 6, 5, 4, 3, 2, 1, 1, 0, 0   # Evening wind-down
        ]
        
        max_activity = max(activity_levels) or 1
        
        # Generate hourly heatmap
        hour_line = "Hours: "
        heat_line = "Heat:  "
        
        for hour, activity in zip(hours, activity_levels):
            intensity = self.calculate_intensity_level(activity, max_activity, 5)
            heat_char = self.get_heat_character(intensity)
            
            hour_line += f"{hour:2d} "
            heat_line += f"{heat_char}  "
        
        lines.append(hour_line)
        lines.append(heat_line)
        
        return lines
    
    def generate_file_type_heatmap(self, file_data: Dict[str, int], width: int = 40) -> List[str]:
        """Generate heatmap for vulnerability distribution by file type"""
        if not file_data:
            return ["No file type data available"]
        
        lines = []
        lines.append("📁 File Type Vulnerability Heatmap")
        lines.append("=" * 50)
        
        max_vulns = max(file_data.values()) or 1
        
        # Sort by vulnerability count
        sorted_files = sorted(file_data.items(), key=lambda x: x[1], reverse=True)
        
        for file_type, vuln_count in sorted_files[:10]:  # Top 10 file types
            intensity = self.calculate_intensity_level(vuln_count, max_vulns)
            heat_char = self.get_heat_character(intensity)
            
            # Create mini heat bar
            bar_length = int((vuln_count / max_vulns) * width)
            heat_bar = heat_char * bar_length
            remaining = width - bar_length
            if remaining > 0:
                cool_char = self.get_heat_character(0)
                heat_bar += cool_char * remaining
            
            lines.append(f"{file_type:<12} │{heat_bar}│ {vuln_count} vulns")
        
        return lines
    
    def generate_severity_heatmap(self, severity_data: Dict[str, Dict], width: int = 30) -> List[str]:
        """Generate 2D heatmap for severity distribution across time/categories"""
        if not severity_data:
            return ["No severity data available"]
        
        lines = []
        lines.append("🌡️  Severity Distribution Heatmap")
        lines.append("=" * 60)
        
        severities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        
        # Create header
        header = "Category     " + "".join(f"{s:<8}" for s in severities)
        lines.append(header)
        lines.append("-" * len(header))
        
        # Generate heatmap rows
        for category, sev_counts in severity_data.items():
            if isinstance(sev_counts, dict):
                line = f"{category:<12} "
                
                for severity in severities:
                    count = sev_counts.get(severity, 0)
                    max_in_category = max(sev_counts.values()) or 1
                    
                    intensity = self.calculate_intensity_level(count, max_in_category, 4)
                    heat_char = self.get_heat_character(intensity)
                    
                    # Create mini heat indicator
                    heat_indicator = heat_char * 3 + f" {count:>3}"
                    line += f"{heat_indicator:<8}"
                
                lines.append(line)
        
        return lines
    
    def generate_correlation_heatmap(self, correlation_matrix: Dict[str, Dict[str, float]], 
                                   size: int = 10) -> List[str]:
        """Generate correlation heatmap between different metrics"""
        # This is a placeholder for advanced correlation analysis
        lines = []
        lines.append("🔗 Metric Correlation Heatmap")
        lines.append("=" * 40)
        lines.append("(Advanced feature - implementation depends on available metrics)")
        
        # Example: Show correlation between file size, complexity, and vulnerability count
        metrics = ["Size", "Complexity", "Vulnerabilities", "Age"]
        
        # Mock correlation data
        lines.append("     " + "".join(f"{m:<12}" for m in metrics))
        lines.append("-" * 60)
        
        for i, metric1 in enumerate(metrics):
            line = f"{metric1:<4} "
            for j, metric2 in enumerate(metrics):
                if i == j:
                    correlation = 1.0  # Perfect self-correlation
                else:
                    # Mock correlation values
                    correlation = abs(math.sin(i + j)) * 0.8
                
                intensity = self.calculate_intensity_level(correlation, 1.0, 5)
                heat_char = self.get_heat_character(intensity)
                line += f"{heat_char * 3} {correlation:4.2f}   "
            
            lines.append(line)
        
        return lines