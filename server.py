#!/usr/bin/env python3
"""
OpenAI-Compatible Server for Z.AI
Implements /v1/chat/completions and /v1/models endpoints
"""

import os
import time
import json
import uuid
import asyncio
import httpx
from typing import Optional, Dict, Any, AsyncGenerator
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

# ============================================================================
# Configuration
# ============================================================================

ZAI_BASE_URL = os.getenv("ZAI_BASE_URL", "https://chat.z.ai")
ZAI_EMAIL = os.getenv("ZAI_EMAIL", "developer@pixelium.uk")
ZAI_PASSWORD = os.getenv("ZAI_PASSWORD", "developer123?")
USE_GUEST_TOKEN = os.getenv("USE_GUEST_TOKEN", "false").lower() == "true"
PORT = int(os.getenv("PORT", "8000"))

# Global HTTP client
http_client: Optional[httpx.AsyncClient] = None
cached_token: Optional[str] = None

# ============================================================================
# Models
# ============================================================================

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[Dict[str, Any]]
    usage: Dict[str, int] = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

# ============================================================================
# Lifespan Management
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    global http_client
    
    print("🚀 Starting Z.AI OpenAI-Compatible Server...")
    print(f"📍 Base URL: {ZAI_BASE_URL}")
    print(f"🔐 Auth Mode: {'Guest Token' if USE_GUEST_TOKEN else 'User Login'}")
    
    # Create HTTP client
    http_client = httpx.AsyncClient(timeout=60.0)
    
    # Get initial token
    token = await get_auth_token()
    if token:
        print(f"✅ Got initial token: {token[:30]}...")
    else:
        print("⚠️ Failed to get initial token, will retry on requests")
    
    yield
    
    # Cleanup
    if http_client:
        await http_client.aclose()
    print("👋 Server shutting down")

app = FastAPI(title="Z.AI OpenAI Compatible API", version="1.0.0", lifespan=lifespan)

# ============================================================================
# Authentication
# ============================================================================

async def get_guest_token() -> Optional[str]:
    """Get a guest token from Z.AI"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        
        response = await http_client.get(f"{ZAI_BASE_URL}/api/v1/auths/", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            if token:
                print(f"✅ Got guest token: {token[:30]}...")
                return token
    except Exception as e:
        print(f"❌ Guest token error: {e}")
    
    return None

async def get_user_token() -> Optional[str]:
    """Get a user token via login"""
    try:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        
        payload = {
            "email": ZAI_EMAIL,
            "password": ZAI_PASSWORD
        }
        
        response = await http_client.post(
            f"{ZAI_BASE_URL}/api/v1/auths/signin",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            if token:
                print(f"✅ Got user token: {token[:30]}...")
                return token
    except Exception as e:
        print(f"❌ User login error: {e}")
    
    return None

async def get_auth_token() -> Optional[str]:
    """Get authentication token (guest or user)"""
    global cached_token
    
    if cached_token:
        return cached_token
    
    if USE_GUEST_TOKEN:
        token = await get_guest_token()
    else:
        token = await get_user_token()
        if not token:
            print("⚠️ User login failed, falling back to guest token")
            token = await get_guest_token()
    
    if token:
        cached_token = token
    
    return token

# ============================================================================
# Z.AI API Calls
# ============================================================================

async def create_zai_chat(token: str) -> Optional[str]:
    """Create a new Z.AI chat and return chat_id"""
    try:
        headers = {
            "authorization": f"Bearer {token}",
            "content-type": "application/json",
            "x-fe-version": "prod-fe-1.0.70",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        
        message_id = str(uuid.uuid4())
        timestamp = int(time.time())
        
        payload = {
            "chat": {
                "id": "",
                "title": "Chat via OpenAI API",
                "models": ["glm-4.5v"],
                "params": {},
                "history": {
                    "messages": {},
                    "currentId": message_id
                },
                "messages": [],
                "tags": [],
                "flags": [],
                "features": [],
                "mcp_servers": [],
                "enable_thinking": False,
                "timestamp": timestamp
            }
        }
        
        response = await http_client.post(
            f"{ZAI_BASE_URL}/api/v1/chats/new",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            chat_id = data.get("id")
            print(f"✅ Created chat: {chat_id}")
            return chat_id
    except Exception as e:
        print(f"❌ Chat creation error: {e}")
    
    return None

async def get_zai_completion(
    token: str,
    chat_id: str,
    messages: list[Message],
    model: str = "glm-4.5v",
    stream: bool = False
) -> Any:
    """Get completion from Z.AI"""
    headers = {
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
        "x-fe-version": "prod-fe-1.0.70",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    
    # Convert messages to Z.AI format
    zai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
    
    payload = {
        "model": model,
        "messages": zai_messages,
        "stream": stream,
        "chatId": chat_id,
        "parentMessageId": str(uuid.uuid4())
    }
    
    if stream:
        return http_client.stream(
            "POST",
            f"{ZAI_BASE_URL}/api/chat/completions",
            headers=headers,
            json=payload
        )
    else:
        response = await http_client.post(
            f"{ZAI_BASE_URL}/api/chat/completions",
            headers=headers,
            json=payload
        )
        return response

# ============================================================================
# OpenAI-Compatible Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Z.AI OpenAI-Compatible API",
        "version": "1.0.0",
        "endpoints": [
            "/v1/models",
            "/v1/chat/completions"
        ]
    }

@app.get("/v1/models")
async def list_models():
    """List available models - proxies directly from Z.AI"""
    try:
        response = await http_client.get(f"{ZAI_BASE_URL}/api/models")
        
        if response.status_code == 200:
            data = response.json()
            # Z.AI already returns OpenAI-compatible format!
            return data
    except Exception as e:
        print(f"❌ Models list error: {e}")
    
    # Fallback to hardcoded list
    return {
        "object": "list",
        "data": [
            {
                "id": "GLM-4.5",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "z.ai"
            },
            {
                "id": "GLM-4.6",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "z.ai"
            }
        ]
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint"""
    
    print(f"📨 Request: model={request.model}, messages={len(request.messages)}, stream={request.stream}")
    
    # Get auth token
    token = await get_auth_token()
    if not token:
        raise HTTPException(status_code=500, detail="Failed to get authentication token")
    
    # Create chat
    chat_id = await create_zai_chat(token)
    if not chat_id:
        raise HTTPException(status_code=500, detail="Failed to create chat")
    
    # Get completion
    try:
        if request.stream:
            # Streaming response
            async def generate():
                async with get_zai_completion(
                    token, chat_id, request.messages, request.model, stream=True
                ) as response:
                    
                    if response.status_code != 200:
                        error_text = await response.aread()
                        print(f"❌ Z.AI error: {response.status_code} - {error_text.decode()}")
                        
                        error_chunk = {
                            "id": f"chatcmpl-{int(time.time())}",
                            "object": "chat.completion.chunk",
                            "created": int(time.time()),
                            "model": request.model,
                            "choices": [{
                                "index": 0,
                                "delta": {"content": f"Error: {response.status_code}"},
                                "finish_reason": "stop"
                            }]
                        }
                        yield f"data: {json.dumps(error_chunk)}\n\n"
                        yield "data: [DONE]\n\n"
                        return
                    
                    # Forward SSE stream
                    async for line in response.aiter_lines():
                        if line:
                            yield f"{line}\n"
            
            return StreamingResponse(generate(), media_type="text/event-stream")
        
        else:
            # Non-streaming response
            response = await get_zai_completion(
                token, chat_id, request.messages, request.model, stream=False
            )
            
            if response.status_code != 200:
                error_text = response.text
                print(f"❌ Z.AI error: {response.status_code} - {error_text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Z.AI API error: {error_text}"
                )
            
            # Return Z.AI response (already OpenAI-compatible)
            data = response.json()
            print(f"✅ Response: {json.dumps(data)[:200]}...")
            return data
    
    except Exception as e:
        print(f"❌ Completion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    token = await get_auth_token()
    return {
        "status": "healthy" if token else "degraded",
        "has_token": bool(token),
        "base_url": ZAI_BASE_URL
    }

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("🚀 Z.AI OpenAI-Compatible Server")
    print("=" * 70)
    print()
    print(f"📍 Server: http://localhost:{PORT}")
    print(f"📚 Docs: http://localhost:{PORT}/docs")
    print(f"🔐 Auth: {'Guest Token' if USE_GUEST_TOKEN else 'User Login'}")
    print()
    print("Endpoints:")
    print(f"  GET  http://localhost:{PORT}/v1/models")
    print(f"  POST http://localhost:{PORT}/v1/chat/completions")
    print()
    print("=" * 70)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=PORT)
