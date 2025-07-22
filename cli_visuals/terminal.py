"""
Terminal Capabilities Detection and Color Scheme Management
"""

import os
import sys
from enum import Enum
from typing import Optional
from rich.console import Console
from rich.terminal_theme import DEFAULT_TERMINAL_THEME
from colorama import init, just_fix_windows_console


class ColorScheme(Enum):
    """Available color schemes for visualizations"""
    DEFAULT = "default"
    MONOCHROME = "monochrome"
    DARK = "dark"
    SECURITY = "security"  # Red/yellow/green for security themes


class TerminalCapabilities:
    """Detect and manage terminal capabilities for enhanced visuals"""
    
    def __init__(self):
        # Initialize colorama for Windows compatibility
        if sys.platform.startswith('win'):
            just_fix_windows_console()
        else:
            init()
        
        self.console = Console()
        self._color_support = None
        self._width = None
    
    @property
    def supports_256_colors(self) -> bool:
        """Check if terminal supports 256 colors"""
        if self._color_support is None:
            # Check environment variables
            term = os.environ.get('TERM', '').lower()
            colorterm = os.environ.get('COLORTERM', '').lower()
            
            # Common indicators of 256-color support
            supports_256 = any([
                '256color' in term,
                'xterm' in term,
                colorterm in ['truecolor', '24bit'],
                self.console.color_system is not None,
                hasattr(self.console, '_color_system') and self.console._color_system != 'standard'
            ])
            
            # Also check if we're in a known limited environment
            limited_env = any([
                os.environ.get('CI') == 'true' and 'FORCE_COLOR' not in os.environ,
                term in ['dumb', 'unknown', ''],
                'PYCHARM' in os.environ and 'FORCE_COLOR' not in os.environ
            ])
            
            self._color_support = supports_256 and not limited_env
            
        return self._color_support
    
    @property 
    def terminal_width(self) -> int:
        """Get terminal width with fallback"""
        if self._width is None:
            try:
                self._width = self.console.width or 80
            except:
                self._width = 80
        return self._width
    
    def get_color_scheme(self, preferred: ColorScheme = ColorScheme.DEFAULT, 
                        force_monochrome: bool = False) -> ColorScheme:
        """Get appropriate color scheme based on terminal capabilities"""
        if force_monochrome or not self.supports_256_colors:
            return ColorScheme.MONOCHROME
        return preferred
    
    def test_capabilities(self) -> dict:
        """Test and return terminal capabilities for debugging"""
        return {
            'width': self.terminal_width,
            'color_system': str(self.console.color_system),
            'supports_256_colors': self.supports_256_colors,
            'term_env': os.environ.get('TERM', 'not set'),
            'colorterm_env': os.environ.get('COLORTERM', 'not set'),
            'platform': sys.platform,
            'is_jupyter': hasattr(self.console, '_jupyter'),
            'is_terminal': self.console.is_terminal
        }


# Global instance for easy access
terminal = TerminalCapabilities()


def get_gradient_colors(scheme: ColorScheme) -> list:
    """Get color codes for gradient based on scheme"""
    
    if scheme == ColorScheme.MONOCHROME:
        # Unicode block elements for monochrome gradients
        return ['·', '░', '▒', '▓', '█']
    
    elif scheme == ColorScheme.SECURITY:
        # Security-themed colors: green (safe) -> yellow -> red (dangerous)
        return [
            '[green]█[/green]',      # Safe/Low
            '[green3]█[/green3]',    # 
            '[yellow]█[/yellow]',    # Medium
            '[orange1]█[/orange1]',  #
            '[red]█[/red]'           # Critical/High
        ]
    
    elif scheme == ColorScheme.DARK:
        # Dark theme friendly colors
        return [
            '[bright_black]█[/bright_black]',
            '[blue]█[/blue]',
            '[cyan]█[/cyan]',
            '[yellow]█[/yellow]',
            '[white]█[/white]'
        ]
    
    else:  # DEFAULT
        # Full spectrum gradient using Rich color names
        return [
            '[blue]█[/blue]',
            '[bright_blue]█[/bright_blue]',
            '[cyan]█[/cyan]',
            '[green]█[/green]',
            '[yellow]█[/yellow]',
            '[orange1]█[/orange1]',
            '[red]█[/red]',
            '[bright_red]█[/bright_red]'
        ]


def get_severity_colors() -> dict:
    """Get colors for different severity levels"""
    return {
        'CRITICAL': '[bright_red]',
        'HIGH': '[red]',
        'MEDIUM': '[yellow]', 
        'LOW': '[green]',
        'INFO': '[blue]'
    }