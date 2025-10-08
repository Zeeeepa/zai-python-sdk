"""Server configuration."""

import os
from typing import Dict


class Config:
    """Server configuration."""
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "7000"))
    
    # CORS settings
    CORS_ORIGINS: list = ["*"]
    
    # Model mappings from OpenAI model names to Z.AI model IDs
    MODEL_MAPPINGS: Dict[str, str] = {
        "gpt-4": "0727-360B-API",
        "gpt-4-turbo": "0727-360B-API",
        "gpt-3.5-turbo": "glm-4.5v",
        "glm-4.5": "glm-4.5v",
        "glm-4.5v": "glm-4.5v",
        "glm-4.6": "glm-4.5v",  # Support the model name from user's example
    }
    
    # Default model if not specified
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "glm-4.5v")
    
    # Z.AI settings
    ZAI_BASE_URL: str = os.getenv("ZAI_BASE_URL", "https://chat.z.ai")
    ZAI_TIMEOUT: int = int(os.getenv("ZAI_TIMEOUT", "180"))
    
    @classmethod
    def get_zai_model(cls, openai_model: str) -> str:
        """
        Map OpenAI model name to Z.AI model ID.
        
        Args:
            openai_model: OpenAI model name
            
        Returns:
            Z.AI model ID
        """
        return cls.MODEL_MAPPINGS.get(openai_model, openai_model)


config = Config()

