"""Simple configuration for the framework"""

class Config:
    """Simple configuration manager"""
    
    def __init__(self):
        # Default settings
        self.settings = {
            'verbose': False,
            'max_file_size': 1000000,  # 1MB
            'skip_dirs': ['.git', 'node_modules', '__pycache__'],
            'ai_enabled': True,
            'ai_timeout': 30
        }
        print("Configuration loaded!")
    
    def get(self, key: str, default=None):
        """Get a configuration value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value):
        """Set a configuration value"""
        self.settings[key] = value
        if self.get('verbose'):
            print(f"Config updated: {key} = {value}")
    
    def show_all(self):
        """Show all configuration settings"""
        print("Current Configuration:")
        for key, value in self.settings.items():
            print(f"  {key}: {value}")