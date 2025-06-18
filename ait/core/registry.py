"""Simple registry for managing analyzers"""

from typing import Dict, List, Optional
from .base import BaseAnalyzer

class Registry:
    """Simple registry to manage analyzers"""
    
    def __init__(self):
        self._analyzers: Dict[str, BaseAnalyzer] = {}
        print("Registry initialized!")
    
    def register_analyzer(self, name: str, analyzer: BaseAnalyzer):
        """Register an analyzer"""
        self._analyzers[name] = analyzer
        print(f"Registered analyzer: {name}")
    
    def get_analyzer(self, name: str) -> Optional[BaseAnalyzer]:
        """Get an analyzer by name"""
        return self._analyzers.get(name)
    
    def list_analyzers(self) -> List[str]:
        """List all registered analyzer names"""
        return list(self._analyzers.keys())
    
    def count(self) -> int:
        """Count registered analyzers"""
        return len(self._analyzers)
    
    def show_all(self):
        """Show all registered analyzers"""
        print(f"Registered Analyzers ({self.count()}):")
        for name, analyzer in self._analyzers.items():
            print(f"  {name}: {analyzer.get_info()}")
