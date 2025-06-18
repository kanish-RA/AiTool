"""Test the configuration system"""

import ait

def test_config():
    print("Testing Configuration System...")
    
    # Show current config
    ait.config.show_all()
    
    # Get a value
    verbose = ait.config.get('verbose')
    print(f"\nVerbose mode: {verbose}")
    
    # Set a value
    print("\nEnabling verbose mode...")
    ait.config.set('verbose', True)
    
    # Set another value (should show message now)
    print("Setting AI timeout...")
    ait.config.set('ai_timeout', 60)
    
    # Get a non-existent value with default
    custom_setting = ait.config.get('custom_setting', 'default_value')
    print(f"Custom setting: {custom_setting}")
    
    # Show final config
    print("\nFinal configuration:")
    ait.config.show_all()
    
    print("\nConfig test complete!")

if __name__ == "__main__":
    test_config()