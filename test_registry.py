"""Test the registry system"""

import ait
from pathlib import Path
from typing import Dict, Any

# Create some test analyzers
class HTMLAnalyzer(ait.BaseAnalyzer):
    """Analyzes HTML files"""
    
    def can_analyze(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in ['.html', '.htm']
    
    def analyze(self, file_path: Path) -> Dict[str, Any]:
        return {
            'file': file_path.name,
            'type': 'HTML',
            'analyzer': self.name
        }

class PythonAnalyzer(ait.BaseAnalyzer):
    """Analyzes Python files"""
    
    def can_analyze(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == '.py'
    
    def analyze(self, file_path: Path) -> Dict[str, Any]:
        return {
            'file': file_path.name,
            'type': 'Python',
            'analyzer': self.name
        }

def test_registry():
    print("Testing Registry System...")
    
    # Create analyzers
    html_analyzer = HTMLAnalyzer("HTMLAnalyzer")
    python_analyzer = PythonAnalyzer("PythonAnalyzer")
    
    # Register them
    ait.registry.register_analyzer("html", html_analyzer)
    ait.registry.register_analyzer("python", python_analyzer)
    
    # Show all registered
    print(f"\nRegistry count: {ait.registry.count()}")
    ait.registry.show_all()
    
    # Test getting analyzers
    print(f"\nAnalyzer names: {ait.registry.list_analyzers()}")
    
    # Get specific analyzer
    html = ait.registry.get_analyzer("html")
    if html:
        print(f"Found HTML analyzer: {html.get_info()}")
        
        # Test it
        test_file = Path("test.html")
        can_analyze = html.can_analyze(test_file)
        print(f"Can analyze {test_file}: {can_analyze}")
        
        if can_analyze:
            result = html.analyze(test_file)
            print(f"Analysis result: {result}")
    
    # Try non-existent analyzer
    missing = ait.registry.get_analyzer("nonexistent")
    print(f"Non-existent analyzer: {missing}")
    
    print("\nRegistry test complete!")

if __name__ == "__main__":
    test_registry()