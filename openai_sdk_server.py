"""
OpenAI-Compatible Server - Direct SDK wrapper approach
Uses Z.AI SDK's working simple_chat method
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Literal
import time
import json
import uuid
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import directly from the SDK files
import importlib.util
spec = importlib.util.spec_from_file_location("client", "./client.py")
client_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client_module)

app = FastAPI(title="Z.AI OpenAI-Compatible API")

# Initialize using the example pattern
client = client_module.ChatZAI()

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
            {"id": name, "object": "model", "created": int(time.time()), "owned_by": "zai"}
            for name in MODEL_MAPPINGS.keys()
        ]
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    zai_model = MODEL_MAPPINGS.get(request.model, request.model)
    user_msg = request.messages[-1].content
    
    if request.stream:
        async def generate():
            try:
                response_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
                for chunk in client.simple_chat(user_msg, model=zai_model, stream=True):
                    if chunk:
                        data = {
                            "id": response_id,
                            "object": "chat.completion.chunk",
                            "created": int(time.time()),
                            "model": request.model,
                            "choices": [{
                                "index": 0,
                                "delta": {"content": chunk},
                                "finish_reason": None
                            }]
                        }
                        yield f"data: {json.dumps(data)}\n\n"
                
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
                yield f"data: {{\"error\": {{\"message\": \"{str(e)}\"}}}}\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    
    else:
        try:
            full_response = client.simple_chat(user_msg, model=zai_model, stream=False)
            return {
                "id": f"chatcmpl-{uuid.uuid4().hex[:24]}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": full_response},
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
    print("🚀 Z.AI OpenAI-Compatible Server Starting...")
    print("📍 Server: http://0.0.0.0:7000")
    print("📚 Docs: http://localhost:7000/docs")
    uvicorn.run(app, host="0.0.0.0", port=7000)
