"""AI Testing Framework - Simple and modular test automation"""

__version__ = "0.1.0"

# Import core components
from .core import BaseAnalyzer, Config, Registry

# Create global instances
config = Config()
registry = Registry()

print("AI Testing Framework loaded!")