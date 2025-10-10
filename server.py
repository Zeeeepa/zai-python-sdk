#!/usr/bin/env python3
"""
Z.AI OpenAI-Compatible API Server
A lightweight, production-ready server that provides OpenAI-compatible endpoints for Z.AI models.

Features:
- Automatic guest token authentication with signature
- Full OpenAI API compatibility
- Streaming and non-streaming support
- Multiple model support (GLM-4.5, GLM-4.5v, 0727-360B-API)
- Dynamic port allocation

Usage:
    python3 server.py [--port PORT]

Environment Variables:
    PORT - Server port (default: 8000)
    HOST - Server host (default: 0.0.0.0)
"""

import json
import uuid
import time
import hmac
import hashlib
import base64
import argparse
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from urllib.parse import urlencode

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
import requests
import uvicorn


# ============================================================================
# Configuration
# ============================================================================

DEFAULT_PORT = int(os.getenv("PORT", "8000"))
DEFAULT_HOST = os.getenv("HOST", "0.0.0.0")

MODELS = [
    {"id": "glm-4.5v", "name": "GLM-4.5 Vision", "description": "Visual understanding model"},
    {"id": "glm-4.5", "name": "GLM-4.5", "description": "Standard language model"},
    {"id": "0727-360B-API", "name": "GLM-4.5 360B", "description": "Advanced coding model"},
]


# ============================================================================
# Signature Generation & Authentication
# ============================================================================

def _urlsafe_b64decode(data: str) -> bytes:
    """Decode URL-safe base64 with proper padding"""
    if isinstance(data, str):
        data_bytes = data.encode("utf-8")
    else:
        data_bytes = data
    padding = b"=" * (-len(data_bytes) % 4)
    return base64.urlsafe_b64decode(data_bytes + padding)


def _decode_jwt_payload(token: str) -> Dict[str, Any]:
    """Decode JWT payload without verification"""
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return {}
        payload_raw = _urlsafe_b64decode(parts[1])
        return json.loads(payload_raw.decode("utf-8", errors="ignore"))
    except Exception:
        return {}


def _extract_user_id_from_token(token: str) -> str:
    """Extract user_id from JWT payload"""
    payload = _decode_jwt_payload(token) if token else {}
    for key in ("id", "user_id", "uid", "sub"):
        val = payload.get(key)
        if isinstance(val, (str, int)) and str(val):
            return str(val)
    return "guest"


def generate_signature(
    message_text: str,
    request_id: str,
    timestamp_ms: int,
    user_id: str,
    secret: str = "junjie"
) -> str:
    """Generate dual-layer HMAC-SHA256 signature"""
    r = str(timestamp_ms)
    e = f"requestId,{request_id},timestamp,{timestamp_ms},user_id,{user_id}"
    t = message_text or ""
    i = f"{e}|{t}|{r}"

    window_index = timestamp_ms // (5 * 60 * 1000)
    root_key = (secret or "junjie").encode("utf-8")
    derived_hex = hmac.new(root_key, str(window_index).encode("utf-8"), hashlib.sha256).hexdigest()
    signature = hmac.new(derived_hex.encode("utf-8"), i.encode("utf-8"), hashlib.sha256).hexdigest()
    return signature


def generate_uuid() -> str:
    """Generate UUID for chat/request IDs"""
    return str(uuid.uuid4())


# ============================================================================
# Pydantic Models
# ============================================================================

class Message(BaseModel):
    role: str
    content: str


class OpenAIRequest(BaseModel):
    model: str
    messages: List[Message]
    stream: bool = False
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


# ============================================================================
# Z.AI Client
# ============================================================================

class ZAIClient:
    BASE_URL = "https://chat.z.ai"

    def __init__(self):
        self.token = None
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
            "Referer": "https://chat.z.ai/",
            "Origin": "https://chat.z.ai",
        })

    def get_token(self) -> str:
        """Get guest authentication token"""
        if self.token:
            return self.token

        try:
            response = self.session.get(f"{self.BASE_URL}/api/v1/auths/")
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token", "")
                if self.token:
                    print(f"✅ Authenticated: {self.token[:30]}...")
                return self.token
        except Exception as e:
            print(f"❌ Authentication failed: {e}")

        return ""

    def chat_completion(self, request: OpenAIRequest) -> Dict[str, Any]:
        """Send chat completion request with signature"""
        token = self.get_token()
        if not token:
            raise Exception("Failed to obtain authentication token")

        # Extract last user message for signing
        last_user_text = ""
        for msg in reversed(request.messages):
            if msg.role == "user":
                last_user_text = msg.content
                break

        # Generate IDs and signature
        chat_id = generate_uuid()
        request_id = generate_uuid()
        timestamp_ms = int(time.time() * 1000)
        user_id = _extract_user_id_from_token(token)

        signature = generate_signature(
            message_text=last_user_text,
            request_id=request_id,
            timestamp_ms=timestamp_ms,
            user_id=user_id,
            secret="junjie"
        )

        # Build query parameters
        query_params = {
            "timestamp": timestamp_ms,
            "requestId": request_id,
            "user_id": user_id,
            "token": token,
            "current_url": f"https://chat.z.ai/c/{chat_id}",
            "pathname": f"/c/{chat_id}",
            "signature_timestamp": timestamp_ms,
        }

        url = f"{self.BASE_URL}/api/chat/completions?{urlencode(query_params)}"

        # Prepare headers
        headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US",
            "Authorization": f"Bearer {token}",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Origin": "https://chat.z.ai",
            "Pragma": "no-cache",
            "Referer": "https://chat.z.ai/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
            "X-FE-Version": "prod-fe-1.0.95",
            "X-Signature": signature,
        }

        # Prepare request body
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        body = {
            "stream": True,
            "model": "0727-360B-API",
            "messages": messages,
            "params": {},
            "features": {
                "image_generation": False,
                "web_search": False,
                "auto_web_search": False,
                "preview_mode": False,
                "flags": [],
                "features": [],
                "enable_thinking": False,
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
                "{{CURRENT_TIMEZONE}}": "Asia/Shanghai",
                "{{USER_LANGUAGE}}": "en-US",
            },
            "model_item": {
                "id": "0727-360B-API",
                "name": request.model,
                "owned_by": "z.ai"
            },
            "chat_id": chat_id,
            "id": request_id,
            "tools": None,
        }

        if request.temperature is not None:
            body["params"]["temperature"] = request.temperature
        if request.max_tokens is not None:
            body["params"]["max_tokens"] = request.max_tokens

        # Make request
        response = self.session.post(
            url,
            json=body,
            headers=headers,
            stream=True,
            timeout=180
        )

        if response.status_code != 200:
            error_text = response.text
            raise Exception(f"Z.AI API error: {error_text}")

        return {
            "response": response,
            "chat_id": chat_id,
            "model": request.model
        }


# ============================================================================
# FastAPI Application
# ============================================================================

client = ZAIClient()
app = FastAPI(title="Z.AI OpenAI-Compatible API", version="1.0.0")


@app.get("/")
async def root():
    """Root endpoint with server information"""
    return {
        "service": "Z.AI OpenAI-Compatible API Server",
        "version": "1.0.0",
        "status": "operational",
        "authenticated": client.token is not None,
        "endpoints": {
            "health": "/health",
            "models": "/v1/models",
            "chat": "/v1/chat/completions"
        },
        "documentation": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Z.AI OpenAI-Compatible API",
        "version": "1.0.0",
        "authenticated": client.token is not None
    }


@app.get("/v1/models")
async def list_models():
    """List available models"""
    return {
        "object": "list",
        "data": [
            {
                "id": model["id"],
                "object": "model",
                "created": int(time.time()),
                "owned_by": "z.ai",
                "description": model.get("description", "")
            }
            for model in MODELS
        ]
    }


def stream_response(response_data: Dict[str, Any], request: OpenAIRequest):
    """Stream SSE response"""
    response = response_data["response"]
    chat_id = response_data["chat_id"]
    model = response_data["model"]

    try:
        buffer = ""
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue

            buffer += line + "\n"

            while "\n" in buffer:
                current_line, buffer = buffer.split("\n", 1)
                if not current_line.strip():
                    continue

                if current_line.startswith("data:"):
                    chunk_str = current_line[5:].strip()
                    if not chunk_str or chunk_str == "[DONE]":
                        if chunk_str == "[DONE]":
                            yield "data: [DONE]\n\n"
                        continue

                    try:
                        chunk = json.loads(chunk_str)

                        if chunk.get("type") == "chat:completion":
                            data = chunk.get("data", {})
                            phase = data.get("phase")
                            delta_content = data.get("delta_content", "")

                            if phase == "answer" and delta_content:
                                openai_chunk = {
                                    "id": f"chatcmpl-{chat_id}",
                                    "object": "chat.completion.chunk",
                                    "created": int(time.time()),
                                    "model": model,
                                    "choices": [{
                                        "index": 0,
                                        "delta": {"content": delta_content},
                                        "finish_reason": None
                                    }]
                                }
                                yield f"data: {json.dumps(openai_chunk)}\n\n"

                            if data.get("usage"):
                                finish_chunk = {
                                    "id": f"chatcmpl-{chat_id}",
                                    "object": "chat.completion.chunk",
                                    "created": int(time.time()),
                                    "model": model,
                                    "choices": [{
                                        "index": 0,
                                        "delta": {},
                                        "finish_reason": "stop"
                                    }],
                                    "usage": data["usage"]
                                }
                                yield f"data: {json.dumps(finish_chunk)}\n\n"
                                yield "data: [DONE]\n\n"

                    except json.JSONDecodeError:
                        pass

    except Exception as e:
        error_chunk = {
            "error": {
                "message": str(e),
                "type": "stream_error"
            }
        }
        yield f"data: {json.dumps(error_chunk)}\n\n"
        yield "data: [DONE]\n\n"


@app.post("/v1/chat/completions")
async def chat_completions(request: OpenAIRequest):
    """OpenAI-compatible chat completions endpoint"""
    try:
        response_data = client.chat_completion(request)

        if request.stream:
            return StreamingResponse(
                stream_response(response_data, request),
                media_type="text/event-stream"
            )
        else:
            full_content = ""
            for chunk in stream_response(response_data, request):
                if chunk.startswith("data: ") and chunk != "data: [DONE]\n\n":
                    try:
                        data = json.loads(chunk[6:])
                        if "choices" in data:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                full_content += delta["content"]
                    except:
                        pass

            return {
                "id": f"chatcmpl-{response_data['chat_id']}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": full_content
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Main Entry Point
# ============================================================================

def print_banner(port: int, host: str):
    """Print server startup banner"""
    print("\n" + "=" * 70)
    print("🚀 Z.AI OpenAI-Compatible API Server")
    print("=" * 70)
    print()
    print("📋 Configuration:")
    print(f"   • Host: {host}")
    print(f"   • Port: {port}")
    print(f"   • Base URL: http://{host}:{port}")
    print()
    print("📡 Available Endpoints:")
    print(f"   • Health Check:     http://localhost:{port}/health")
    print(f"   • List Models:      http://localhost:{port}/v1/models")
    print(f"   • Chat Completions: http://localhost:{port}/v1/chat/completions")
    print(f"   • API Docs:         http://localhost:{port}/docs")
    print()
    print("🤖 Supported Models:")
    for model in MODELS:
        print(f"   • {model['id']: <20} - {model['description']}")
    print()
    print("=" * 70)
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Z.AI OpenAI-Compatible API Server")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Server port")
    parser.add_argument("--host", type=str, default=DEFAULT_HOST, help="Server host")
    args = parser.parse_args()

    print_banner(args.port, args.host)

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")

