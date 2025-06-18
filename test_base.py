"""Simple test to make sure our base class works"""

from ait import BaseAnalyzer
from pathlib import Path
from typing import Dict, Any

# Create a simple test analyzer
class TestAnalyzer(BaseAnalyzer):
    """A simple test analyzer"""
    
    def can_analyze(self, file_path: Path) -> bool:
        """Can analyze .txt files"""
        return file_path.suffix == '.txt'
    
    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """Simple analysis"""
        return {
            'file_name': file_path.name,
            'analyzer': self.name,
            'message': 'Analysis complete!'
        }

# Test it
if __name__ == "__main__":
    print("Testing BaseAnalyzer...")
    
    # Create analyzer
    analyzer = TestAnalyzer("MyTestAnalyzer")
    
    # Test with a file path
    test_file = Path("example.txt")
    
    # Check if it can analyze
    can_analyze = analyzer.can_analyze(test_file)
    print(f"Can analyze {test_file}: {can_analyze}")
    
    # Get info
    print(analyzer.get_info())
    
    # Run analysis
    if can_analyze:
        result = analyzer.analyze(test_file)
        print(f"Analysis result: {result}")
    
    print("Test complete!")