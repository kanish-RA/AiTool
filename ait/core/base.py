"""Base classes for the framework"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any

class BaseAnalyzer(ABC):
    """Base class for all code analyzers"""
    
    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        print(f"Created analyzer: {self.name}")
    
    @abstractmethod
    def can_analyze(self, file_path: Path) -> bool:
        """Check if this analyzer can handle the given file"""
        pass
    
    @abstractmethod
    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """Analyze the file and return results"""
        pass
    
    def get_info(self) -> str:
        """Get analyzer information"""
        return f"Analyzer: {self.name}"

# NEW: Add base generator class
class BaseGenerator(ABC):
    """Base class for all test generators"""
    
    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        print(f"Created generator: {self.name}")
    
    @abstractmethod
    def can_generate(self, analysis_results: List[Dict[str, Any]]) -> bool:
        """Check if this generator can handle the analysis results"""
        pass
    
    @abstractmethod
    def generate(self, analysis_results: List[Dict[str, Any]], options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate test content based on analysis results"""
        pass
    
    def get_info(self) -> str:
        """Get generator information"""
        return f"Generator: {self.name}"
