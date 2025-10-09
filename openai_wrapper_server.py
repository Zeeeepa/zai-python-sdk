"""
OpenAI-Compatible Server using Z.AI Python SDK directly
This works around the "Missing signature header" issue by using the SDK
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Literal, Dict, Any
import time
import json
import uuid
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from __init__ import ChatZAI

app = FastAPI(title="Z.AI OpenAI-Compatible API (SDK Wrapper)")

# Initialize Z.AI client  
client = ChatZAI()

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

@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {"id": model_name, "object": "model", "created": int(time.time()), "owned_by": "zai"}
            for model_name in MODEL_MAPPINGS.keys()
        ]
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    # Map model name
    zai_model = MODEL_MAPPINGS.get(request.model, request.model)
    
    # Convert messages to simple string
    conversation = "\n".join([f"{msg.role}: {msg.content}" for msg in request.messages])
    user_msg = request.messages[-1].content
    
    if request.stream:
        # Streaming response
        async def generate():
            try:
                # Use SDK's simple_chat with streaming
                response_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
                
                for chunk_text in client.simple_chat(user_msg, model=zai_model, stream=True):
                    if chunk_text:
                        chunk = {
                            "id": response_id,
                            "object": "chat.completion.chunk",
                            "created": int(time.time()),
                            "model": request.model,
                            "choices": [{
                                "index": 0,
                                "delta": {"content": chunk_text},
                                "finish_reason": None
                            }]
                        }
                        yield f"data: {json.dumps(chunk)}\n\n"
                
                # Send final chunk
                final_chunk = {
                    "id": response_id,
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": request.model,
                    "choices": [{
                        "index": 0,
                        "delta": {},
                        "finish_reason": "stop"
                    }]
                }
                yield f"data: {json.dumps(final_chunk)}\n\n"
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                error_chunk = {
                    "error": {
                        "message": str(e),
                        "type": "server_error"
                    }
                }
                yield f"data: {json.dumps(error_chunk)}\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    
    else:
        # Non-streaming response
        try:
            # Use SDK's simple_chat
            full_response = client.simple_chat(user_msg, model=zai_model, stream=False)
            
            return {
                "id": f"chatcmpl-{uuid.uuid4().hex[:24]}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": full_response
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": len(user_msg.split()),
                    "completion_tokens": len(full_response.split()) if full_response else 0,
                    "total_tokens": len(user_msg.split()) + (len(full_response.split()) if full_response else 0)
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Z.AI Error: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Z.AI OpenAI-Compatible Server (SDK Wrapper)")
    print("📍 Server: http://0.0.0.0:7000")
    print("📚 Docs: http://0.0.0.0:7000/docs")
    uvicorn.run(app, host="0.0.0.0", port=7000)
