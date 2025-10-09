"""
OpenAI-Compatible Standalone Server for Z.AI
Fully self-contained - no SDK imports needed!
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Literal, Dict, Any, Generator
import time
import json
import uuid
import requests
import hashlib
import base64

app = FastAPI(title="Z.AI OpenAI-Compatible API (Standalone)")

# Z.AI Configuration
ZAI_API_BASE = "https://z.hhgzs.com/api/v1"
ZAI_AUTH_URL = f"{ZAI_API_BASE}/authentication/token"
ZAI_CHAT_URL = f"{ZAI_API_BASE}/chatbot/completion"

# Model mappings
MODEL_MAPPINGS = {
    "gpt-4": "0727-360B-API",
    "gpt-4-turbo": "0727-360B-API", 
    "gpt-3.5-turbo": "glm-4.5v",
    "glm-4.5": "glm-4.5v",
    "glm-4.5v": "glm-4.5v",
    "glm-4.6": "GLM-4-6-API-V1",
}

class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 100
    stream: Optional[bool] = False

def get_zai_token() -> str:
    """Get authentication token from Z.AI"""
    try:
        response = requests.post(ZAI_AUTH_URL, json={}, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("token", "")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auth failed: {str(e)}")

def chat_with_zai(message: str, model: str, stream: bool = False, token: str = None) -> Any:
    """Chat with Z.AI API"""
    if not token:
        token = get_zai_token()
    
    payload = {
        "messages": [{"role": "user", "content": message}],
        "model": model,
        "stream": stream,
        "enable_thinking": False,
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 500
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        if stream:
            response = requests.post(ZAI_CHAT_URL, json=payload, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            return response
        else:
            response = requests.post(ZAI_CHAT_URL, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Z.AI API error: {str(e)}")

@app.get("/v1/models")
async def list_models():
    """List available models"""
    return {
        "object": "list",
        "data": [
            {"id": name, "object": "model", "created": int(time.time()), "owned_by": "zai"}
            for name in MODEL_MAPPINGS.keys()
        ]
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """Handle chat completion requests"""
    zai_model = MODEL_MAPPINGS.get(request.model, request.model)
    user_msg = request.messages[-1].content
    
    # Get token once
    token = get_zai_token()
    
    if request.stream:
        async def generate():
            try:
                response_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
                stream_response = chat_with_zai(user_msg, zai_model, stream=True, token=token)
                
                for line in stream_response.iter_lines():
                    if line:
                        line_text = line.decode('utf-8')
                        if line_text.startswith('data: '):
                            data_str = line_text[6:]
                            if data_str.strip() == '[DONE]':
                                continue
                            
                            try:
                                data = json.loads(data_str)
                                content = data.get('choices', [{}])[0].get('delta', {}).get('content', '')
                                
                                if content:
                                    chunk = {
                                        "id": response_id,
                                        "object": "chat.completion.chunk",
                                        "created": int(time.time()),
                                        "model": request.model,
                                        "choices": [{
                                            "index": 0,
                                            "delta": {"content": content},
                                            "finish_reason": None
                                        }]
                                    }
                                    yield f"data: {json.dumps(chunk)}\n\n"
                            except json.JSONDecodeError:
                                continue
                
                # Send final chunk
                final = {
                    "id": response_id,
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": request.model,
                    "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
                }
                yield f"data: {json.dumps(final)}\n\n"
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                error = {"error": {"message": str(e), "type": "server_error"}}
                yield f"data: {json.dumps(error)}\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    
    else:
        # Non-streaming response
        try:
            zai_response = chat_with_zai(user_msg, zai_model, stream=False, token=token)
            
            # Extract content from Z.AI response
            content = ""
            if isinstance(zai_response, dict):
                choices = zai_response.get('choices', [])
                if choices:
                    content = choices[0].get('message', {}).get('content', '')
            
            return {
                "id": f"chatcmpl-{uuid.uuid4().hex[:24]}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": len(user_msg.split()),
                    "completion_tokens": len(content.split()) if content else 0,
                    "total_tokens": len(user_msg.split()) + (len(content.split()) if content else 0)
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "zai-openai-compatible"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Z.AI OpenAI-Compatible API Server",
        "endpoints": {
            "health": "/health",
            "models": "/v1/models",
            "chat": "/v1/chat/completions",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("="*60)
    print("🚀 Z.AI OpenAI-Compatible Server (Standalone)")
    print("="*60)
    print("📍 Server: http://0.0.0.0:7000")
    print("📚 API Docs: http://0.0.0.0:7000/docs")
    print("🔧 Health: http://0.0.0.0:7000/health")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=7000, log_level="info")
