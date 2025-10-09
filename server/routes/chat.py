"""Chat completions endpoint."""

import json
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import StreamingResponse

# Import from wrapper
from server.zai_client_wrapper import ZAIClient, ZAIError

from server.models.openai import ChatCompletionRequest, ChatCompletionResponse
from server.adapters import convert_openai_to_zai, convert_zai_to_openai, convert_zai_chunk_to_openai
from server.config import config


router = APIRouter()


def get_zai_client(authorization: str = None) -> ZAIClient:
    """
    Create Z.AI client with token from authorization header.
    
    Args:
        authorization: Authorization header value
        
    Returns:
        ZAIClient instance
    """
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]  # Remove "Bearer " prefix
    
    return ZAIClient(
        token=token,
        base_url=config.ZAI_BASE_URL,
        timeout=config.ZAI_TIMEOUT,
        auto_auth=token is None  # Auto-auth if no token provided
    )


@router.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
    request: ChatCompletionRequest,
    authorization: str = Header(None)
):
    """
    Create a chat completion (OpenAI-compatible endpoint).
    
    Args:
        request: Chat completion request
        authorization: Authorization header
        
    Returns:
        Chat completion response or streaming response
    """
    try:
        # Create Z.AI client
        client = get_zai_client(authorization)
        
        # Convert request to Z.AI format
        zai_params = convert_openai_to_zai(request)
        
        # Handle streaming
        if request.stream:
            async def generate_stream() -> AsyncGenerator[str, None]:
                """Generate SSE stream."""
                try:
                    # Create chat first
                    chat = client.create_chat(
                        title="OpenAI API Chat",
                        models=[zai_params["model"]]
                    )
                    
                    # Generate completion ID
                    from server.adapters.zai_to_openai import generate_completion_id
                    completion_id = generate_completion_id()
                    
                    # Stream completion
                    for chunk in client.stream_completion(
                        chat_id=chat.id,
                        messages=zai_params["messages"],
                        model=zai_params["model"],
                        enable_thinking=zai_params.get("enable_thinking", True)
                    ):
                        # Only send answer phase chunks
                        if hasattr(chunk, 'phase') and chunk.phase == 'answer':
                            openai_chunk = convert_zai_chunk_to_openai(
                                chunk,
                                request.model,
                                completion_id
                            )
                            yield f"data: {json.dumps(openai_chunk)}\n\n"
                    
                    # Send final chunk
                    final_chunk = convert_zai_chunk_to_openai(
                        type('obj', (), {'delta_content': ''})(),
                        request.model,
                        completion_id,
                        is_final=True
                    )
                    yield f"data: {json.dumps(final_chunk)}\n\n"
                    yield "data: [DONE]\n\n"
                    
                except Exception as e:
                    error_data = {
                        "error": {
                            "message": str(e),
                            "type": "server_error",
                            "code": "internal_error"
                        }
                    }
                    yield f"data: {json.dumps(error_data)}\n\n"
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream"
            )
        
        # Non-streaming response
        else:
            # Use simple_chat for single-message requests
            if len(request.messages) == 1:
                response = client.simple_chat(
                    message=request.messages[0].content,
                    model=zai_params["model"],
                    temperature=zai_params.get("temperature"),
                    top_p=zai_params.get("top_p"),
                    max_tokens=zai_params.get("max_tokens")
                )
            else:
                # Create chat and complete
                chat = client.create_chat(
                    title="OpenAI API Chat",
                    models=[zai_params["model"]]
                )
                response = client.complete_chat(
                    chat_id=chat.id,
                    messages=zai_params["messages"],
                    model=zai_params["model"]
                )
            
            # Convert to OpenAI format
            openai_response = convert_zai_to_openai(response, request.model)
            return openai_response
    
    except ZAIError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
