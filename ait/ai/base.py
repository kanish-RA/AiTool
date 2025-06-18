"""Base AI provider class"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class BaseAIProvider(ABC):
    """Base class for AI providers"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.name = self.__class__.__name__
        print(f"Created AI provider: {self.name}")
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the AI provider is available"""
        pass
    
    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> Optional[str]:
        """Generate text using AI"""
        pass
    
    def get_info(self) -> str:
        """Get AI provider information"""
        return f"AI Provider: {self.name}"