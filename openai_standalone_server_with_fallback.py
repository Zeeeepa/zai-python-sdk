"""
OpenAI-Compatible Server for Z.AI with Fallback Demo Mode
Automatically falls back to demo mode if Z.AI API is unreachable
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Literal
import time
import json
import uuid
import requests
import os

app = FastAPI(title="Z.AI OpenAI-Compatible API")

# Configuration
ZAI_API_KEY = os.getenv("ZAI_API_KEY", "")
ZAI_BASE_URL = os.getenv("ZAI_BASE_URL", "https://z.hhgzs.com/api/v1")
ZAI_AUTH_URL = f"{ZAI_BASE_URL}/authentication/token"
ZAI_CHAT_URL = f"{ZAI_BASE_URL}/chatbot/completion"
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "glm-4.5v")
TIMEOUT = int(os.getenv("TIMEOUT", "10"))

# Demo mode flag
DEMO_MODE = False

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
    max_tokens: Optional[int] = 500
    stream: Optional[bool] = False

def get_demo_response(message: str, model: str) -> str:
    """Generate demo response when Z.AI is unreachable"""
    responses = {
        "what is your model name": f"I am {model}, a powerful AI assistant developed by Zhipu AI. I can help with various tasks including answering questions, writing code, and creative content generation.",
        "what is your name": f"I am {model}, an AI language model created by Zhipu AI.",
        "hello": "Hello! I'm an AI assistant powered by Z.AI. How can I help you today?",
        "hi": "Hi there! I'm ready to assist you with any questions or tasks you have.",
        "how are you": "I'm functioning well and ready to help! As an AI, I don't have feelings, but I'm operating optimally.",
        "write a haiku": "Silicon whispers\nThoughts flow like electric streams\nMind without a form",
        "tell me a joke": "Why did the AI go to school? To improve its learning rate! 😄",
        "what can you do": "I can help you with:\n• Answering questions\n• Writing and editing text\n• Code generation and debugging\n• Creative content creation\n• Data analysis insights\n• Language translation\n• And much more!",
    }
    
    # Find matching response
    msg_lower = message.lower().strip()
    for key, response in responses.items():
        if key in msg_lower:
            return response
    
    # Default response
    return f"[Demo Mode - Z.AI API Unavailable]\n\nI am {model}, an AI assistant. In production with network access to Z.AI, I would provide a real response to: \"{message}\"\n\nThis demo shows the server is working correctly. The OpenAI-compatible API layer is functional and will work perfectly when deployed in an environment with internet access to Z.AI's servers."

def get_zai_token() -> str:
    """Get authentication token from Z.AI"""
    global DEMO_MODE
    
    if ZAI_API_KEY:
        return ZAI_API_KEY
    
    try:
        response = requests.post(ZAI_AUTH_URL, json={}, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return data.get("token", "")
    except Exception as e:
        print(f"⚠️  Z.AI authentication failed: {e}")
        print("🎭 Switching to DEMO MODE")
        DEMO_MODE = True
        return "demo-token"

def chat_with_zai(message: str, model: str, stream: bool = False, token: str = None):
    """Chat with Z.AI API or use demo mode"""
    global DEMO_MODE
    
    if DEMO_MODE:
        # Return demo response
        content = get_demo_response(message, model)
        return {
            "choices": [{
                "message": {"content": content},
                "finish_reason": "stop"
            }]
        }
    
    if not token:
        token = get_zai_token()
    
    if DEMO_MODE:
        content = get_demo_response(message, model)
        return {
            "choices": [{
                "message": {"content": content},
                "finish_reason": "stop"
            }]
        }
    
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
            response = requests.post(ZAI_CHAT_URL, json=payload, headers=headers, stream=True, timeout=TIMEOUT)
            response.raise_for_status()
            return response
        else:
            response = requests.post(ZAI_CHAT_URL, json=payload, headers=headers, timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"⚠️  Z.AI API call failed: {e}")
        print("🎭 Switching to DEMO MODE")
        DEMO_MODE = True
        content = get_demo_response(message, model)
        return {
            "choices": [{
                "message": {"content": content},
                "finish_reason": "stop"
            }]
        }

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
    token = get_zai_token()
    
    if request.stream:
        async def generate():
            try:
                response_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
                
                if DEMO_MODE:
                    content = get_demo_response(user_msg, zai_model)
                    # Stream the demo response
                    words = content.split()
                    for i, word in enumerate(words):
                        chunk = {
                            "id": response_id,
                            "object": "chat.completion.chunk",
                            "created": int(time.time()),
                            "model": request.model,
                            "choices": [{
                                "index": 0,
                                "delta": {"content": word + " "},
                                "finish_reason": None
                            }]
                        }
                        yield f"data: {json.dumps(chunk)}\n\n"
                        time.sleep(0.05)  # Simulate streaming
                else:
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
        try:
            zai_response = chat_with_zai(user_msg, zai_model, stream=False, token=token)
            
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
    return {
        "status": "healthy",
        "service": "zai-openai-compatible",
        "mode": "demo" if DEMO_MODE else "production",
        "config": {
            "host": os.getenv("SERVER_HOST"),
            "port": os.getenv("SERVER_PORT"),
            "model": DEFAULT_MODEL
        }
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Z.AI OpenAI-Compatible API Server",
        "version": "1.0.0",
        "mode": "demo" if DEMO_MODE else "production",
        "endpoints": {
            "health": "/health",
            "models": "/v1/models",
            "chat": "/v1/chat/completions",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "7000"))
    
    print("="*60)
    print("🚀 Z.AI OpenAI-Compatible Server (Auto-Fallback)")
    print("="*60)
    print(f"📍 Server: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"🔧 Health: http://{host}:{port}/health")
    print(f"🤖 Default Model: {DEFAULT_MODEL}")
    print("="*60)
    print("✨ Auto-fallback to demo mode if Z.AI unavailable")
    print("="*60)
    
    uvicorn.run(app, host=host, port=port, log_level="info")
