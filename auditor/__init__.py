"""
AI Code Security Auditor CLI Package
Hackathon-ready command-line interface for security scanning
"""

__version__ = "2.0.0"
__author__ = "AI Security Team"
__description__ = "AI-powered security scanner with intelligent fix suggestions"

# Make CLI easily importable
from .cli import main, cli

__all__ = ['main', 'cli']