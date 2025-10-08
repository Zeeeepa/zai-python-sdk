"""Convert OpenAI format requests to Z.AI format."""

from typing import Dict, List
from ..models.openai import ChatCompletionRequest
from ..config import config


def convert_openai_to_zai(request: ChatCompletionRequest) -> Dict:
    """
    Convert OpenAI chat completion request to Z.AI format.
    
    Args:
        request: OpenAI ChatCompletionRequest
        
    Returns:
        Dictionary with Z.AI API parameters
    """
    # Map model name
    zai_model = config.get_zai_model(request.model)
    
    # Convert messages to Z.AI format
    # Z.AI expects a simple message format
    messages = []
    for msg in request.messages:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })
    
    # Build Z.AI parameters
    zai_params = {
        "model": zai_model,
        "messages": messages,
        "enable_thinking": True,  # Enable thinking mode by default
    }
    
    # Add optional parameters if provided
    if request.temperature is not None:
        zai_params["temperature"] = request.temperature
    
    if request.top_p is not None:
        zai_params["top_p"] = request.top_p
    
    if request.max_tokens is not None:
        zai_params["max_tokens"] = request.max_tokens
    
    return zai_params

