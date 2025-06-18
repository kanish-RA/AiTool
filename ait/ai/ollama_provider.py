"""Ollama AI provider implementation"""

import requests
from typing import Optional, Dict, Any
from .base import BaseAIProvider

class OllamaProvider(BaseAIProvider):
    """Ollama local AI provider"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.base_url = self.config.get('base_url', 'http://localhost:11434')
        self.model = self.config.get('model', 'llama3.2:3b')
        self.timeout = self.config.get('timeout', 120)
    
    def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_text(self, prompt: str, **kwargs) -> Optional[str]:
        """Generate text using Ollama"""
        if not self.is_available():
            print("Ollama is not available, falling back to rule-based generation")
            return None
        
        try:
            url = f"{self.base_url}/api/generate"
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(url, json=data, timeout=self.timeout)
            if response.status_code == 200:
                result = response.json()["response"]
                print(f"✅ AI generated {len(result)} characters")
                return result
            else:
                print(f"❌ AI request failed with status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ AI generation error: {str(e)}")
            return None