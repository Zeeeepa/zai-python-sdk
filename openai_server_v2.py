#!/usr/bin/env python3
"""
Z.AI OpenAI-Compatible API Server v2
ACTUALLY WORKING implementation based on reverse engineering 3 existing implementations
"""

import json
import time
import uuid
import re
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

import requests
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field


# ============================================================================
# Configuration
# ============================================================================

class Config:
    BASE_URL = "https://chat.z.ai"
    HOST = "0.0.0.0"
    PORT = 7000
    
    # Browser-like headers (CRITICAL for bypassing bot detection)
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "X-FE-Version": "prod-fe-1.0.76",
        "sec-ch-ua": '"Not;A=Brand";v="99", "Chrome";v="139"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Origin": BASE_URL,
    }
    
    # Model mappings
    MODEL_MAPPINGS = {
        "gpt-4": "0727-360B-API",
        "gpt-4-turbo": "0727-360B-API",
        "gpt-3.5-turbo": "glm-4.5v",
        "glm-4.5": "glm-4.5v",
        "glm-4.5v": "glm-4.5v",
        "glm-4.6": "GLM-4-6-API-V1",
    }


# ============================================================================
# Pydantic Models
# ============================================================================

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False


class ChatCompletionChunkChoice(BaseModel):
    index: int
    delta: Dict[str, Any]
    finish_reason: Optional[str] = None


class ChatCompletionChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[ChatCompletionChunkChoice]


class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionResponseChoice]
    usage: Dict[str, int]


# ============================================================================
# Z.AI Client (ACTUALLY WORKING)
# ============================================================================

class ZAIClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = Config.BASE_URL
        self.session = requests.Session()
        self.session.headers.update(Config.HEADERS)
        
        # Get authentication token
        if api_key and api_key not in ("dummy-key", "dummy", ""):
            self.token = api_key
            print(f"✅ Using provided token: {self.token[:30]}...")
        else:
            print("🔄 Fetching guest token...")
            self.token = self._get_guest_token()
        
        if self.token:
            self.session.headers["Authorization"] = f"Bearer {self.token}"
        else:
            print("⚠️ No token available!")
    
    def _get_guest_token(self) -> Optional[str]:
        """Get guest token from Z.AI (GET request, not POST!)"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/auths/", timeout=10)
            response.raise_for_status()
            data = response.json()
            token = data.get("token")
            if token:
                print(f"✅ Guest token obtained: {token[:30]}...")
                return token
        except Exception as e:
            print(f"⚠️ Failed to get guest token: {e}")
        return None
    
    def _map_model(self, model: str) -> str:
        """Map OpenAI model names to Z.AI model IDs"""
        return Config.MODEL_MAPPINGS.get(model, "glm-4.5v")
    
    def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        top_p: float = 1.0,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ):
        """
        Complete a chat request using Z.AI API
        This is the CORRECT way based on reverse engineering
        """
        chat_id = str(uuid.uuid4())
        msg_id = str(uuid.uuid4())
        
        # Map model
        zai_model = self._map_model(model)
        
        # Build the payload (EXACT structure from working implementations)
        payload = {
            "stream": stream,
            "model": zai_model,
            "messages": messages,
            "params": {
                "temperature": temperature,
                "top_p": top_p,
            },
            "features": {
                "image_generation": False,
                "web_search": False,
                "auto_web_search": False,
                "preview_mode": False,
                "flags": [],
                "features": [
                    {"type": "mcp", "server": "vibe-coding", "status": "hidden"},
                    {"type": "mcp", "server": "ppt-maker", "status": "hidden"},
                    {"type": "mcp", "server": "image-search", "status": "hidden"},
                ],
                "enable_thinking": True,
            },
            "background_tasks": {
                "title_generation": False,
                "tags_generation": False,
            },
            "mcp_servers": [],
            "variables": {
                "{{USER_NAME}}": "Guest",
                "{{USER_LOCATION}}": "Unknown",
                "{{CURRENT_DATETIME}}": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "{{CURRENT_DATE}}": datetime.now().strftime("%Y-%m-%d"),
                "{{CURRENT_TIME}}": datetime.now().strftime("%H:%M:%S"),
                "{{CURRENT_WEEKDAY}}": datetime.now().strftime("%A"),
                "{{CURRENT_TIMEZONE}}": "UTC",
                "{{USER_LANGUAGE}}": "en-US",
            },
            "model_item": {
                "id": zai_model,
                "name": zai_model,
            },
            "chat_id": chat_id,
            "id": msg_id,
        }
        
        if max_tokens:
            payload["params"]["max_tokens"] = max_tokens
        
        # Add referer header (important!)
        headers = self.session.headers.copy()
        headers["Referer"] = f"{self.base_url}/c/{chat_id}"
        
        # Make request
        url = f"{self.base_url}/api/chat/completions"
        
        print(f"\n📤 Request to: {url}")
        print(f"📦 Payload model: {zai_model}")
        print(f"📦 Messages: {len(messages)} messages")
        print(f"🔑 Token: {self.token[:30] if self.token else 'None'}...")
        
        try:
            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                stream=stream,
                timeout=60
            )
            
            print(f"📥 Response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Error response: {response.text[:500]}")
                response.raise_for_status()
            
            return response
            
        except Exception as e:
            print(f"❌ Request failed: {e}")
            raise


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Z.AI OpenAI-Compatible API v2",
    description="ACTUALLY WORKING OpenAI-compatible API proxy for Z.AI",
    version="2.0.0",
)


def get_client(authorization: Optional[str] = Header(None)) -> ZAIClient:
    """Get Z.AI client from authorization header"""
    api_key = None
    if authorization:
        api_key = authorization.replace("Bearer ", "").strip()
    return ZAIClient(api_key)


@app.get("/v1/models")
async def list_models():
    """List available models"""
    models = [
        {
            "id": "gpt-4",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "openai",
        },
        {
            "id": "gpt-4-turbo",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "openai",
        },
        {
            "id": "gpt-3.5-turbo",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "openai",
        },
        {
            "id": "glm-4.5",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "zhipu",
        },
        {
            "id": "glm-4.5v",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "zhipu",
        },
        {
            "id": "glm-4.6",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "zhipu",
        },
    ]
    return {"object": "list", "data": models}


@app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    authorization: Optional[str] = Header(None)
):
    """OpenAI-compatible chat completions endpoint"""
    
    # Create client
    client = get_client(authorization)
    
    # Convert messages to dict format
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    if request.stream:
        # Streaming response
        def generate_stream():
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
                content_buffer = ""
                
                # First chunk with role
                first_chunk = ChatCompletionChunk(
                    id=completion_id,
                    created=created,
                    model=request.model,
                    choices=[
                        ChatCompletionChunkChoice(
                            index=0,
                            delta={"role": "assistant"},
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
                    
                    data_str = line[6:]  # Remove "data: " prefix
                    if not data_str.strip():
                        continue
                    
                    try:
                        chunk_data = json.loads(data_str)
                        inner_data = chunk_data.get("data", {})
                        
                        # Check if done
                        if inner_data.get("done"):
                            # Final chunk
                            final_chunk = ChatCompletionChunk(
                                id=completion_id,
                                created=created,
                                model=request.model,
                                choices=[
                                    ChatCompletionChunkChoice(
                                        index=0,
                                        delta={},
                                        finish_reason="stop",
                                    )
                                ],
                            )
                            yield f"data: {final_chunk.model_dump_json()}\n\n"
                            yield "data: [DONE]\n\n"
                            break
                        
                        # Extract content
                        phase = inner_data.get("phase", "")
                        delta_content = inner_data.get("delta_content", "") or inner_data.get("edit_content", "")
                        
                        if delta_content and phase == "answer":
                            # Send content chunk
                            chunk = ChatCompletionChunk(
                                id=completion_id,
                                created=created,
                                model=request.model,
                                choices=[
                                    ChatCompletionChunkChoice(
                                        index=0,
                                        delta={"content": delta_content},
                                        finish_reason=None,
                                    )
                                ],
                            )
                            yield f"data: {chunk.model_dump_json()}\n\n"
                            content_buffer += delta_content
                            
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
                stream=True,  # Always use stream internally
            )
            
            # Collect all content
            content_buffer = ""
            for line in response.iter_lines():
                if not line:
                    continue
                
                line = line.decode('utf-8')
                if not line.startswith('data: '):
                    continue
                
                data_str = line[6:]
                if not data_str.strip():
                    continue
                
                try:
                    chunk_data = json.loads(data_str)
                    inner_data = chunk_data.get("data", {})
                    
                    if inner_data.get("done"):
                        break
                    
                    phase = inner_data.get("phase", "")
                    delta_content = inner_data.get("delta_content", "") or inner_data.get("edit_content", "")
                    
                    if delta_content and phase == "answer":
                        content_buffer += delta_content
                        
                except json.JSONDecodeError:
                    continue
            
            # Build response
            completion_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
            created = int(time.time())
            
            return ChatCompletionResponse(
                id=completion_id,
                created=created,
                model=request.model,
                choices=[
                    ChatCompletionResponseChoice(
                        index=0,
                        message=ChatMessage(role="assistant", content=content_buffer),
                        finish_reason="stop",
                    )
                ],
                usage={
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                },
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
    
    print("🚀 Starting Z.AI OpenAI-Compatible API Server v2...")
    print(f"📍 Server will run at: http://{Config.HOST}:{Config.PORT}")
    print(f"📚 API Documentation: http://{Config.HOST}:{Config.PORT}/docs")
    print("\n🔧 Model mappings:")
    for openai_model, zai_model in Config.MODEL_MAPPINGS.items():
        print(f"   {openai_model} → {zai_model}")
    print("\n✨ This version ACTUALLY WORKS with guest tokens!\n")
    
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)
