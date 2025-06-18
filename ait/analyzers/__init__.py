"""Code analyzers for different frameworks"""

from .framework_detector import FrameworkDetector
from .html_analyzer import HTMLAnalyzer

__all__ = ['FrameworkDetector', 'HTMLAnalyzer']