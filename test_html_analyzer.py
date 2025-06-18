"""Test the HTML analyzer"""

import ait
from ait.analyzers import HTMLAnalyzer
from pathlib import Path
import tempfile

def create_test_html():
    """Create a test HTML file"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Test Page</title>
</head>
<body>
    <header>
        <h1 id="main-title" class="page-title">Welcome to Test Site</h1>
        <nav class="navigation">
            <a href="/home" id="home-link">Home</a>
            <a href="/about" class="nav-link">About</a>
            <a href="/login" class="nav-link auth-link">Login</a>
        </nav>
    </header>
    
    <main class="content">
        <section id="login-section">
            <h2>Login Form</h2>
            <form action="/login" method="POST" id="login-form">
                <div class="form-group">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" placeholder="Enter username" required>
                </div>
                
                <div class="form-group">
                    <label for="email">Email:</label>
                    <input type="email" id="email" name="email" placeholder="Enter email" required>
                </div>
                
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" placeholder="Enter password" required>
                </div>
                
                <div class="form-actions">
                    <button type="submit" id="login-btn" class="btn btn-primary">Login</button>
                    <button type="button" id="cancel-btn" class="btn btn-secondary">Cancel</button>
                    <input type="reset" value="Clear" class="btn btn-outline">
                </div>
            </form>
        </section>
        
        <section id="content-section">
            <h3>Features</h3>
            <table id="features-table" class="data-table">
                <thead>
                    <tr>
                        <th>Feature</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>User Authentication</td>
                        <td>Active</td>
                    </tr>
                    <tr>
                        <td>Data Export</td>
                        <td>Coming Soon</td>
                    </tr>
                </tbody>
            </table>
            
            <div class="image-gallery">
                <img src="/images/logo.png" alt="Company Logo" id="logo" class="logo-img">
                <img src="/images/banner.jpg" alt="Banner Image" class="banner-img">
            </div>
        </section>
    </main>
    
    <footer>
        <div class="footer-content" data-section="footer" data-analytics="track">
            <p>&copy; 2024 Test Company</p>
        </div>
    </footer>
</body>
</html>
"""
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False)
    temp_file.write(html_content)
    temp_file.close()
    
    return Path(temp_file.name)

def test_html_analyzer():
    print("Testing HTML Analyzer...")
    
    # Create analyzer
    analyzer = HTMLAnalyzer()
    
    # Register it
    ait.registry.register_analyzer("html", analyzer)
    
    # Create test HTML file
    test_file = create_test_html()
    print(f"Created test HTML file: {test_file}")
    
    # Test analysis
    result = analyzer.analyze(test_file)
    
    print(f"\n=== HTML Analysis Results ===")
    print(f"File: {result['file_path']}")
    print(f"Framework: {result['framework']}")
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        return
    
    # Show summary
    print(f"\n=== Summary ===")
    for key, value in result['summary'].items():
        print(f"{key}: {value}")
    
    # Show some detailed results
    elements = result['elements']
    
    print(f"\n=== IDs Found ({len(elements['ids'])}) ===")
    for id_val in elements['ids']:
        print(f"  #{id_val}")
    
    print(f"\n=== Classes Found ({len(elements['classes'])}) ===")
    for class_val in elements['classes'][:10]:  # Show first 10
        print(f"  .{class_val}")
    
    print(f"\n=== Forms Found ({len(elements['forms'])}) ===")
    for i, form in enumerate(elements['forms']):
        print(f"  Form {i+1}: {form['method']} -> {form['action']}")
        print(f"    Inputs: {len(form['inputs'])}, Buttons: {len(form['buttons'])}")
    
    print(f"\n=== Buttons Found ({len(elements['buttons'])}) ===")
    for button in elements['buttons']:
        print(f"  {button['type']}: '{button['text']}' (id: {button['id']})")
    
    print(f"\n=== Data Attributes Found ({len(elements['data_attributes'])}) ===")
    for data_attr in elements['data_attributes']:
        print(f"  {data_attr['attribute']}: {data_attr['value']}")
    
    print(f"\n=== Generated XPaths (first 10) ===")
    for xpath in elements['xpaths'][:10]:
        print(f"  {xpath}")
    
    # Clean up
    test_file.unlink()
    
    print("\nHTML analyzer test complete!")

if __name__ == "__main__":
    test_html_analyzer()