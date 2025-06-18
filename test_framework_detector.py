"""Test the framework detector"""

import ait
from ait.analyzers import FrameworkDetector
from pathlib import Path
import json
import tempfile
import os

def create_test_project():
    """Create a test project structure"""
    # Create temporary directory
    test_dir = Path(tempfile.mkdtemp())
    
    # Create a React project structure
    (test_dir / "package.json").write_text(json.dumps({
        "name": "test-app",
        "dependencies": {
            "react": "^18.0.0",
            "react-dom": "^18.0.0"
        },
        "devDependencies": {
            "typescript": "^4.0.0"
        }
    }))
    
    # Create a React component
    (test_dir / "App.jsx").write_text("""
import React from 'react';

function App() {
    return <div>Hello World</div>;
}

export default App;
""")
    
    # Create a Django-style template
    templates_dir = test_dir / "templates"
    templates_dir.mkdir()
    (templates_dir / "index.html").write_text("""
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}My Site{% endblock %}</title>
</head>
<body>
    <h1>{{ message }}</h1>
    {% load static %}
</body>
</html>
""")
    
    return test_dir

def test_framework_detector():
    print("Testing Framework Detector...")
    
    # Create detector
    detector = FrameworkDetector()
    
    # Register it
    ait.registry.register_analyzer("framework_detector", detector)
    
    # Create test project
    test_dir = create_test_project()
    print(f"Created test project at: {test_dir}")
    
    # Test directory analysis
    print("\n=== Directory Analysis ===")
    result = detector.analyze(test_dir)
    
    print(f"Analysis type: {result['type']}")
    print(f"Files scanned: {result['files_scanned']}")
    print(f"Frameworks detected: {result['frameworks_detected']}")
    print(f"Confidence scores: {result['confidence']}")
    
    print("\nEvidence found:")
    for framework, evidence_list in result['evidence'].items():
        print(f"  {framework}:")
        for evidence in evidence_list:
            print(f"    - {evidence}")
    
    # Test single file analysis
    print("\n=== Single File Analysis ===")
    package_json = test_dir / "package.json"
    file_result = detector.analyze(package_json)
    
    print(f"File: {file_result['file']}")
    print(f"Frameworks detected: {file_result['frameworks_detected']}")
    print("Evidence:")
    for framework, evidence_list in file_result['evidence'].items():
        print(f"  {framework}: {evidence_list}")
    
    # Clean up
    import shutil
    shutil.rmtree(test_dir)
    
    print("\nFramework detector test complete!")

if __name__ == "__main__":
    test_framework_detector()