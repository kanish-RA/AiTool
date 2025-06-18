"""Test the Gherkin generator"""

import ait
from ait.analyzers import HTMLAnalyzer
from ait.generators import GherkinGenerator
from pathlib import Path
import tempfile

def create_sample_html():
    """Create sample HTML files for testing"""
    html_files = []
    
    # Login page
    login_html = """
<!DOCTYPE html>
<html>
<head><title>Login</title></head>
<body>
    <h1>User Login</h1>
    <form action="/login" method="POST" id="login-form">
        <input type="text" name="username" id="username" placeholder="Username" required>
        <input type="password" name="password" id="password" placeholder="Password" required>
        <button type="submit" id="login-btn">Login</button>
    </form>
    <nav>
        <a href="/home">Home</a>
        <a href="/about">About</a>
    </nav>
</body>
</html>
"""
    
    # Dashboard page
    dashboard_html = """
<!DOCTYPE html>
<html>
<head><title>Dashboard</title></head>
<body>
    <h1>Welcome to Dashboard</h1>
    <nav class="main-nav">
        <a href="/profile">Profile</a>
        <a href="/settings">Settings</a>
        <a href="/logout">Logout</a>
    </nav>
    <table id="data-table">
        <tr><th>Name</th><th>Status</th></tr>
        <tr><td>John</td><td>Active</td></tr>
    </table>
    <img src="/logo.png" alt="Company Logo" id="logo">
</body>
</html>
"""
    
    # Create temp files
    for content, name in [(login_html, 'login.html'), (dashboard_html, 'dashboard.html')]:
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=f'_{name}', delete=False)
        temp_file.write(content)
        temp_file.close()
        html_files.append(Path(temp_file.name))
    
    return html_files

def test_gherkin_generator():
    print("Testing Gherkin Generator...")
    
    # Create analyzers and generators
    html_analyzer = HTMLAnalyzer()
    gherkin_generator = GherkinGenerator()
    
    # Register them
    ait.registry.register_analyzer("html", html_analyzer)
    ait.registry.register_analyzer("gherkin", gherkin_generator)  # Note: different registry for generators needed
    
    print("Created and registered analyzer and generator")
    
    # Create sample HTML files
    html_files = create_sample_html()
    print(f"Created {len(html_files)} sample HTML files")
    
    # Analyze each HTML file
    analysis_results = []
    for html_file in html_files:
        print(f"Analyzing: {html_file.name}")
        result = html_analyzer.analyze(html_file)
        analysis_results.append(result)
    
    print(f"\n=== Analysis Complete ===")
    print(f"Analyzed {len(analysis_results)} files")
    
    # Generate Gherkin scenarios
    print("\n=== Generating Gherkin Scenarios ===")
    generation_result = gherkin_generator.generate(analysis_results)
    
    print(f"Generated {generation_result['scenarios_count']} scenarios")
    print(f"Format: {generation_result['format']}")
    print(f"Generated at: {generation_result['generated_at']}")
    
    # Show the generated Gherkin content
    print(f"\n=== Generated Gherkin Feature File ===")
    print(generation_result['content'])
    
    # Show analysis summary
    print(f"\n=== Analysis Summary ===")
    summary = generation_result['analysis_summary']
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Clean up
    for html_file in html_files:
        html_file.unlink()
    
    print("\nGherkin generator test complete!")

if __name__ == "__main__":
    test_gherkin_generator()