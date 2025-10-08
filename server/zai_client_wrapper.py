"""
Wrapper to import Z.AI client from installed package.
"""

# Import from installed zai package
from client import ZAIClient
from core.exceptions import ZAIError

__all__ = ['ZAIClient', 'ZAIError']

