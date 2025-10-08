#!/usr/bin/env python3
"""
Standalone OpenAI-Compatible API Server for Z.AI

This is a self-contained FastAPI server that provides OpenAI-compatible endpoints
for the Z.AI API. It can be run independently without complex package installations.

Usage:
    python openai_proxy_server.py

Then use with OpenAI client:
    from openai import OpenAI
    client = OpenAI(base_url="http://localhost:7000/v1", api_key="your-z-ai-token")
    response = client.chat.completions.create(
        model="glm-4.5",
        messages=[{"role": "user", "content": "Hello!"}]
    )
"""

import asyncio
import json
import os
import time
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, AsyncIterator
from enum import Enum

import requests
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field


# ============================================================================
# Configuration
# ============================================================================

class Config:
    """Configuration for the OpenAI proxy server."""
    
    # Server settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "7000"))
    
    # Z.AI API settings
    ZAI_BASE_URL = os.getenv("ZAI_BASE_URL", "https://glm-4-5v-api.lingyiwanwu.com")
    ZAI_CHAT_ENDPOINT = "/v4/chat/completions"
    
    # Model mappings (OpenAI model names -> Z.AI model names)
    MODEL_MAPPINGS = {
        "gpt-4": "0727-360B-API",
        "gpt-4-turbo": "0727-360B-API",
        "gpt-3.5-turbo": "glm-4.5v",
        "glm-4.5": "glm-4.5v",
        "glm-4.5v": "glm-4.5v",
        "glm-4.6": "glm-4.5v",
    }
    
    # Supported models list
    AVAILABLE_MODELS = [
        {"id": "gpt-4", "object": "model", "created": 1677610602, "owned_by": "openai"},
        {"id": "gpt-4-turbo", "object": "model", "created": 1677610602, "owned_by": "openai"},
        {"id": "gpt-3.5-turbo", "object": "model", "created": 1677610602, "owned_by": "openai"},
        {"id": "glm-4.5", "object": "model", "created": 1677610602, "owned_by": "zhipu"},
        {"id": "glm-4.5v", "object": "model", "created": 1677610602, "owned_by": "zhipu"},
        {"id": "glm-4.6", "object": "model", "created": 1677610602, "owned_by": "zhipu"},
    ]


# ============================================================================
# Pydantic Models (OpenAI-Compatible)
# ============================================================================

class Role(str, Enum):
    """Message roles."""
    system = "system"
    user = "user"
    assistant = "assistant"


class ChatMessage(BaseModel):
    """A chat message."""
    role: Role
    content: str


class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request."""
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = Field(default=0.7, ge=0, le=2)
    top_p: Optional[float] = Field(default=1.0, ge=0, le=1)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    stream: Optional[bool] = False
    n: Optional[int] = Field(default=1, ge=1, le=1)  # Only support n=1


class ChatCompletionResponseChoice(BaseModel):
    """A choice in the chat completion response."""
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None


class ChatCompletionResponse(BaseModel):
    """OpenAI-compatible chat completion response."""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionResponseChoice]
    usage: Optional[Dict[str, int]] = None


class ChatCompletionChunkDelta(BaseModel):
    """Delta in a streaming chunk."""
    role: Optional[str] = None
    content: Optional[str] = None


class ChatCompletionChunkChoice(BaseModel):
    """A choice in a streaming chunk."""
    index: int
    delta: ChatCompletionChunkDelta
    finish_reason: Optional[str] = None


class ChatCompletionChunk(BaseModel):
    """OpenAI-compatible streaming chunk."""
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[ChatCompletionChunkChoice]


class ModelObject(BaseModel):
    """OpenAI-compatible model object."""
    id: str
    object: str = "model"
    created: int
    owned_by: str


class ModelList(BaseModel):
    """OpenAI-compatible model list."""
    object: str = "list"
    data: List[ModelObject]


# ============================================================================
# Z.AI Client
# ============================================================================

class ZAIClient:
    """Simple Z.AI API client."""
    
    def __init__(self, api_key: str):
        """Initialize the client."""
        self.api_key = api_key
        self.base_url = Config.ZAI_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })
    
    def _map_model(self, model: str) -> str:
        """Map OpenAI model name to Z.AI model name."""
        return Config.MODEL_MAPPINGS.get(model, model)
    
    def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        top_p: float = 1.0,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> Any:
        """Create a chat completion."""
        url = f"{self.base_url}{Config.ZAI_CHAT_ENDPOINT}"
        
        # Build request payload
        payload = {
            "model": self._map_model(model),
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "stream": stream,
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        if stream:
            # Return streaming response
            response = self.session.post(url, json=payload, stream=True, timeout=60)
            response.raise_for_status()
            return response
        else:
            # Return complete response
            response = self.session.post(url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Z.AI OpenAI-Compatible API",
    description="OpenAI-compatible API proxy for Z.AI",
    version="1.0.0",
)


def get_client(authorization: Optional[str] = Header(None)) -> ZAIClient:
    """Get Z.AI client from authorization header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    api_key = authorization[7:]  # Remove "Bearer " prefix
    return ZAIClient(api_key=api_key)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "z-ai-openai-proxy"}


@app.get("/v1/models")
async def list_models():
    """List available models (OpenAI-compatible)."""
    models = [ModelObject(**model) for model in Config.AVAILABLE_MODELS]
    return ModelList(data=models)


@app.post("/v1/chat/completions")
async def create_chat_completion(
    request: ChatCompletionRequest,
    authorization: Optional[str] = Header(None),
):
    """Create a chat completion (OpenAI-compatible)."""
    client = get_client(authorization)
    
    # Convert messages to dict format
    messages = [{"role": msg.role.value, "content": msg.content} for msg in request.messages]
    
    if request.stream:
        # Streaming response
        async def generate_stream():
            """Generate streaming response."""
            try:
                response = client.chat_completion(
                    model=request.model,
                    messages=messages,
                    temperature=request.temperature,
                    top_p=request.top_p,
                    max_tokens=request.max_tokens,
                    stream=True,
                )
                
                completion_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
                created = int(time.time())
                
                # First chunk with role
                first_chunk = ChatCompletionChunk(
                    id=completion_id,
                    created=created,
                    model=request.model,
                    choices=[
                        ChatCompletionChunkChoice(
                            index=0,
                            delta=ChatCompletionChunkDelta(role="assistant"),
                            finish_reason=None,
                        )
                    ],
                )
                yield f"data: {first_chunk.model_dump_json()}\n\n"
                
                # Stream content chunks
                for line in response.iter_lines():
                    if not line:
                        continue
                    
                    line = line.decode('utf-8')
                    if not line.startswith('data: '):
                        continue
                    
                    data = line[6:]  # Remove "data: " prefix
                    if data == '[DONE]':
                        # Final chunk
                        final_chunk = ChatCompletionChunk(
                            id=completion_id,
                            created=created,
                            model=request.model,
                            choices=[
                                ChatCompletionChunkChoice(
                                    index=0,
                                    delta=ChatCompletionChunkDelta(),
                                    finish_reason="stop",
                                )
                            ],
                        )
                        yield f"data: {final_chunk.model_dump_json()}\n\n"
                        yield "data: [DONE]\n\n"
                        break
                    
                    try:
                        chunk_data = json.loads(data)
                        if 'choices' in chunk_data and chunk_data['choices']:
                            delta = chunk_data['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            
                            if content:
                                chunk = ChatCompletionChunk(
                                    id=completion_id,
                                    created=created,
                                    model=request.model,
                                    choices=[
                                        ChatCompletionChunkChoice(
                                            index=0,
                                            delta=ChatCompletionChunkDelta(content=content),
                                            finish_reason=None,
                                        )
                                    ],
                                )
                                yield f"data: {chunk.model_dump_json()}\n\n"
                    except json.JSONDecodeError:
                        continue
                        
            except Exception as e:
                error_chunk = {"error": {"message": str(e), "type": "internal_error"}}
                yield f"data: {json.dumps(error_chunk)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
        )
    else:
        # Non-streaming response
        try:
            response = client.chat_completion(
                model=request.model,
                messages=messages,
                temperature=request.temperature,
                top_p=request.top_p,
                max_tokens=request.max_tokens,
                stream=False,
            )
            
            # Convert Z.AI response to OpenAI format
            completion_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
            created = int(time.time())
            
            content = response['choices'][0]['message']['content']
            usage = response.get('usage', {})
            
            return ChatCompletionResponse(
                id=completion_id,
                created=created,
                model=request.model,
                choices=[
                    ChatCompletionResponseChoice(
                        index=0,
                        message=ChatMessage(role=Role.assistant, content=content),
                        finish_reason="stop",
                    )
                ],
                usage=usage,
            )
        except requests.exceptions.HTTPError as e:
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Z.AI OpenAI-Compatible API Server...")
    print(f"📍 Server will run at: http://{Config.HOST}:{Config.PORT}")
    print(f"📚 API Documentation: http://{Config.HOST}:{Config.PORT}/docs")
    print("\n🔧 Model mappings:")
    for openai_model, zai_model in Config.MODEL_MAPPINGS.items():
        print(f"   {openai_model} → {zai_model}")
    print("\n")
    
    uvicorn.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        log_level="info",
    )

