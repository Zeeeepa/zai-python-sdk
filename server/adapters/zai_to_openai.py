"""Convert Z.AI format responses to OpenAI format."""

import time
import uuid
from typing import Dict
from ..models.openai import (
    ChatCompletionResponse,
    ChatCompletionChunk,
    ChatChoice,
    ChatChoiceDelta,
    ChatMessage,
    Usage,
)


def generate_completion_id() -> str:
    """Generate OpenAI-style completion ID."""
    return f"chatcmpl-{uuid.uuid4().hex[:24]}"


def convert_zai_to_openai(
    zai_response,
    model: str,
    completion_id: str = None
) -> ChatCompletionResponse:
    """
    Convert Z.AI response to OpenAI ChatCompletionResponse.
    
    Args:
        zai_response: Z.AI ChatCompletionResponse object
        model: Model name used in request
        completion_id: Optional completion ID (generated if not provided)
        
    Returns:
        OpenAI ChatCompletionResponse
    """
    if completion_id is None:
        completion_id = generate_completion_id()
    
    # Extract content from Z.AI response
    content = getattr(zai_response, 'content', '') or ''
    
    # Calculate token usage (estimate if not provided)
    prompt_tokens = getattr(zai_response, 'prompt_tokens', 0) or len(str(content).split()) * 2
    completion_tokens = getattr(zai_response, 'completion_tokens', 0) or len(content.split())
    
    usage = Usage(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens
    )
    
    # Create chat choice
    choice = ChatChoice(
        index=0,
        message=ChatMessage(
            role="assistant",
            content=content
        ),
        finish_reason="stop"
    )
    
    return ChatCompletionResponse(
        id=completion_id,
        object="chat.completion",
        created=int(time.time()),
        model=model,
        choices=[choice],
        usage=usage
    )


def convert_zai_chunk_to_openai(
    chunk,
    model: str,
    completion_id: str,
    is_final: bool = False
) -> Dict:
    """
    Convert Z.AI streaming chunk to OpenAI format.
    
    Args:
        chunk: Z.AI StreamingChunk
        model: Model name
        completion_id: Completion ID
        is_final: Whether this is the final chunk
        
    Returns:
        Dictionary representing OpenAI ChatCompletionChunk
    """
    # Extract delta content
    delta_content = getattr(chunk, 'delta_content', '') or ''
    
    # Build delta object
    delta = {}
    if delta_content:
        delta['content'] = delta_content
        delta['role'] = 'assistant'
    
    # Create choice
    choice = {
        "index": 0,
        "delta": delta,
        "finish_reason": "stop" if is_final else None
    }
    
    return {
        "id": completion_id,
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [choice]
    }

