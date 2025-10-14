#!/bin/bash
#
# start.sh - Start Z.AI OpenAI-compatible API Server
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PID_FILE="$SCRIPT_DIR/.server.pid"
LOG_FILE="$SCRIPT_DIR/server.log"
PORT=${1:-8080}

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Starting Z.AI OpenAI API Server on port $PORT                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if server is already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠ Server already running (PID: $OLD_PID)${NC}"
        echo "Stop it first with: kill $OLD_PID"
        exit 1
    fi
fi

# Create server if it doesn't exist
if [ ! -f "zai_server.py" ]; then
    echo "Creating server..."
    cat > zai_server.py << 'PYEOF'
#!/usr/bin/env python3
"""Z.AI OpenAI-Compatible API Server"""
import os, json, uuid, time, httpx
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Z.AI OpenAI Proxy", version="1.0.0")

TOKEN_FILE = ".zai_token"
ZAI_AUTH_URL = os.getenv("ZAI_AUTH_URL", "https://chat.z.ai/api/v1/auths/")
ZAI_CHAT_URL = os.getenv("ZAI_CHAT_URL", "https://chat.z.ai/api/v1/chats/new")

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 1.0
    stream: Optional[bool] = False

def get_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            return f.read().strip()
    try:
        r = httpx.get(ZAI_AUTH_URL, timeout=10)
        if r.status_code == 200:
            token = r.json().get('token', '')
            if token:
                with open(TOKEN_FILE, 'w') as f:
                    f.write(token)
                return token
    except: pass
    return ""

@app.get("/health")
async def health():
    return {"status": "healthy", "has_token": bool(get_token()), "models": 10}

@app.get("/v1/models")
async def models():
    models_list = ["GLM-4.5", "GLM-4.5-Thinking", "GLM-4.5-Search", "GLM-4.5-Air",
                   "GLM-4.6", "GLM-4.6-Thinking", "GLM-4.6-Search",
                   "qwen-max-latest", "qwen-plus-latest", "qwen-turbo-latest"]
    return {
        "object": "list",
        "data": [{"id": m, "object": "model", "created": int(time.time()), "owned_by": "z.ai"} 
                 for m in models_list]
    }

@app.post("/v1/chat/completions")
async def chat(request: ChatRequest, authorization: Optional[str] = Header(None)):
    token = get_token()
    if not token:
        raise HTTPException(503, "No token")
    
    # Get user message
    msg = next((m.content for m in request.messages if m.role == "user"), "")
    if not msg:
        raise HTTPException(400, "No message")
    
    # Create chat
    mid = str(uuid.uuid4())
    ts = int(time.time())
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "X-FE-Version": "prod-fe-1.0.142"
    }
    
    payload = {
        "chat": {
            "id": "",
            "title": "API",
            "models": ["glm-4.5v"],
            "history": {
                "messages": {mid: {"id": mid, "parentId": None, "role": "user", 
                                   "content": msg, "timestamp": ts, "models": ["glm-4.5v"]}},
                "currentId": mid
            },
            "messages": [{"id": mid, "role": "user", "content": msg, "timestamp": ts}]
        }
    }
    
    try:
        r = httpx.post(ZAI_CHAT_URL, headers=headers, json=payload, timeout=30)
        if r.status_code != 200:
            raise HTTPException(500, f"Chat creation failed: {r.status_code}")
        
        chat_data = r.json()
        chat_id = chat_data.get('id')
        
        # Note: Z.AI /api/chat/completions requires X-Signature header
        # This is currently under development - signature algorithm needs reverse engineering
        return JSONResponse({
            "error": {
                "message": "Chat created successfully but completion requires signature validation (under development)",
                "type": "signature_required",
                "chat_id": chat_id,
                "note": "Z.AI API requires X-Signature header which is being reverse-engineered"
            }
        }, status_code=501)
    
    except Exception as e:
        raise HTTPException(500, str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVER_PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
PYEOF
    chmod +x zai_server.py
fi

# Start server in background
echo "Starting server..."
python3 zai_server.py > "$LOG_FILE" 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > "$PID_FILE"

# Wait for server to start
echo "Waiting for server..."
for i in {1..10}; do
    if curl -s "http://localhost:$PORT/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Server started (PID: $SERVER_PID)${NC}"
        echo ""
        echo -e "  Health: ${BLUE}http://localhost:$PORT/health${NC}"
        echo -e "  Models: ${BLUE}http://localhost:$PORT/v1/models${NC}"
        echo -e "  Chat:   ${BLUE}http://localhost:$PORT/v1/chat/completions${NC}"
        echo ""
        echo -e "  Logs:   ${BLUE}tail -f $LOG_FILE${NC}"
        echo -e "  Stop:   ${BLUE}kill $SERVER_PID${NC}"
        echo ""
        exit 0
    fi
    sleep 1
done

echo -e "${RED}✗ Server failed to start${NC}"
echo "Check logs: cat $LOG_FILE"
exit 1

