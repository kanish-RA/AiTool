"""Test the AI-enhanced Gherkin generator"""

import ait
from ait.analyzers import HTMLAnalyzer
from ait.generators import GherkinGenerator
from ait.ai import OllamaProvider
from pathlib import Path
import tempfile

def create_complex_html():
    """Create a more complex HTML file for AI testing"""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>E-commerce Shopping Site</title>
</head>
<body>
    <header>
        <nav id="main-navigation">
            <a href="/home" id="home-link">Home</a>
            <a href="/products" id="products-link">Products</a>
            <a href="/cart" id="cart-link">Shopping Cart</a>
            <a href="/account" id="account-link">My Account</a>
        </nav>
    </header>
    
    <main>
        <section id="user-login">
            <h2>Customer Login</h2>
            <form action="/api/login" method="POST" id="customer-login-form">
                <input type="email" name="email" id="user-email" placeholder="Email address" required>
                <input type="password" name="password" id="user-password" placeholder="Password" required>
                <button type="submit" id="login-submit">Sign In</button>
                <a href="/forgot-password" id="forgot-password-link">Forgot Password?</a>
            </form>
        </section>
        
        <section id="product-catalog">
            <h2>Featured Products</h2>
            <div class="product-grid">
                <div class="product-card" data-product-id="123">
                    <img src="/images/laptop.jpg" alt="Gaming Laptop" class="product-image">
                    <h3>Gaming Laptop Pro</h3>
                    <p class="price">$1,299.99</p>
                    <button class="add-to-cart" data-product="123">Add to Cart</button>
                </div>
                <div class="product-card" data-product-id="456">
                    <img src="/images/mouse.jpg" alt="Wireless Mouse" class="product-image">
                    <h3>Wireless Gaming Mouse</h3>
                    <p class="price">$79.99</p>
                    <button class="add-to-cart" data-product="456">Add to Cart</button>
                </div>
            </div>
        </section>
        
        <section id="checkout-section">
            <h2>Checkout</h2>
            <form action="/api/checkout" method="POST" id="checkout-form">
                <fieldset>
                    <legend>Shipping Information</legend>
                    <input type="text" name="firstName" placeholder="First Name" required>
                    <input type="text" name="lastName" placeholder="Last Name" required>
                    <input type="text" name="address" placeholder="Street Address" required>
                    <input type="text" name="city" placeholder="City" required>
                    <select name="state" required>
                        <option value="">Select State</option>
                        <option value="CA">California</option>
                        <option value="NY">New York</option>
                    </select>
                </fieldset>
                
                <fieldset>
                    <legend>Payment Information</legend>
                    <input type="text" name="cardNumber" placeholder="Card Number" required>
                    <input type="text" name="expiryDate" placeholder="MM/YY" required>
                    <input type="text" name="cvv" placeholder="CVV" required>
                </fieldset>
                
                <button type="submit" id="place-order-btn">Place Order</button>
            </form>
        </section>
        
        <section id="order-history">
            <h2>Order History</h2>
            <table id="orders-table" class="data-table">
                <thead>
                    <tr>
                        <th>Order ID</th>
                        <th>Date</th>
                        <th>Total</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>#12345</td>
                        <td>2024-01-15</td>
                        <td>$1,379.98</td>
                        <td>Shipped</td>
                        <td><a href="/orders/12345">View Details</a></td>
                    </tr>
                </tbody>
            </table>
        </section>
    </main>
    
    <footer>
        <div class="footer-content">
            <a href="/support" id="support-link">Customer Support</a>
            <a href="/privacy" id="privacy-link">Privacy Policy</a>
            <a href="/terms" id="terms-link">Terms of Service</a>
        </div>
    </footer>
</body>
</html>
"""
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='_ecommerce.html', delete=False)
    temp_file.write(html_content)
    temp_file.close()
    
    return Path(temp_file.name)

def test_ai_gherkin_generator():
    print("Testing AI-Enhanced Gherkin Generator...")
    
    # Create AI provider and generator
    ai_provider = OllamaProvider()
    html_analyzer = HTMLAnalyzer()
    gherkin_generator = GherkinGenerator(ai_provider=ai_provider)
    
    print(f"AI Available: {ai_provider.is_available()}")
    
    # Create complex HTML file
    html_file = create_complex_html()
    print(f"Created complex HTML file: {html_file.name}")
    
    # Analyze the HTML
    print("\n=== Analyzing HTML ===")
    analysis_result = html_analyzer.analyze(html_file)
    
    print(f"Elements found:")
    print(f"  - Forms: {len(analysis_result['elements']['forms'])}")
    print(f"  - Buttons: {len(analysis_result['elements']['buttons'])}")
    print(f"  - Links: {len(analysis_result['elements']['links'])}")
    print(f"  - Images: {len(analysis_result['elements']['images'])}")
    print(f"  - Tables: {len(analysis_result['elements']['tables'])}")
    
    # Generate Gherkin with AI
    print(f"\n=== Generating Gherkin Scenarios ===")
    
    # Test with AI enabled
    generation_result = gherkin_generator.generate([analysis_result], {'use_ai': True})
    
    print(f"Generation method: {generation_result['generation_method']}")
    print(f"Scenarios generated: {generation_result['scenarios_count']}")
    
    # Show the generated content
    print(f"\n=== Generated Gherkin Feature File ===")
    print(generation_result['content'])
    
    # Test with AI disabled (fallback)
    print(f"\n=== Testing Fallback (AI Disabled) ===")
    fallback_result = gherkin_generator.generate([analysis_result], {'use_ai': False})
    print(f"Fallback method: {fallback_result['generation_method']}")
    print(f"Fallback scenarios: {fallback_result['scenarios_count']}")
    
    # Clean up
    html_file.unlink()
    
    print("\nAI Gherkin generator test complete!")

if __name__ == "__main__":
    test_ai_gherkin_generator()