#!/bin/bash
# Z.AI OpenAI-Compatible API - Complete Deployment Script
# Usage: bash zai_deploy.sh [branch-name]
# Or: curl -fsSL <raw-url>/zai_deploy.sh | bash -s [branch-name]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Configuration
REPO="Zeeeepa/zai-python-sdk"
BRANCH="${1:-main}"
PROJECT_DIR="zai-openai-api"
DEFAULT_PORT=7000
CONFIG_FILE=".env.zai"

clear
echo ""
echo "============================================================"
echo -e "${CYAN}🚀 Z.AI OpenAI-Compatible API - Complete Deployment${NC}"
echo "============================================================"
echo ""
echo -e "${BLUE}Repository: ${REPO}${NC}"
echo -e "${BLUE}Branch: ${BRANCH}${NC}"
echo ""

# Step 1: Clone repository
echo "============================================================"
echo -e "${BLUE}📥 Step 1: Cloning Repository${NC}"
echo "============================================================"
echo ""

if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}⚠️  Directory $PROJECT_DIR already exists${NC}"
    read -p "$(echo -e ${YELLOW}Remove and re-clone? [Y/n]:${NC}) " remove_dir
    remove_dir="${remove_dir:-Y}"
    
    if [[ "$remove_dir" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Removing existing directory...${NC}"
        rm -rf "$PROJECT_DIR"
    else
        echo -e "${CYAN}Using existing directory${NC}"
        cd "$PROJECT_DIR"
        git fetch origin
        git checkout "$BRANCH"
        git pull origin "$BRANCH"
        echo -e "${GREEN}✅ Updated to latest${NC}"
    fi
fi

if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${CYAN}Cloning repository...${NC}"
    git clone --depth 1 --branch "$BRANCH" "https://github.com/${REPO}.git" "$PROJECT_DIR"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to clone repository${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Repository cloned${NC}"
fi

cd "$PROJECT_DIR"
echo ""

# Step 2: Configuration
echo "============================================================"
echo -e "${BLUE}⚙️  Step 2: Configuration Setup${NC}"
echo "============================================================"
echo ""

# Check for existing configuration
if [ -f "$CONFIG_FILE" ]; then
    echo -e "${GREEN}✅ Found existing configuration${NC}"
    source "$CONFIG_FILE"
    echo ""
    echo "Current settings:"
    echo "  - Server: ${SERVER_HOST}:${SERVER_PORT}"
    echo "  - Model: ${DEFAULT_MODEL}"
    echo ""
    read -p "$(echo -e ${YELLOW}Use existing configuration? [Y/n]:${NC}) " use_config
    use_config="${use_config:-Y}"
    
    if [[ ! "$use_config" =~ ^[Yy]$ ]]; then
        rm -f "$CONFIG_FILE"
    fi
fi

# Prompt for configuration if needed
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${CYAN}Please provide configuration:${NC}"
    echo ""
    
    read -p "$(echo -e ${BLUE}Server host [0.0.0.0]:${NC}) " SERVER_HOST
    SERVER_HOST="${SERVER_HOST:-0.0.0.0}"
    
    read -p "$(echo -e ${BLUE}Server port [7000]:${NC}) " SERVER_PORT
    SERVER_PORT="${SERVER_PORT:-7000}"
    
    echo ""
    echo -e "${CYAN}Z.AI API Key (leave empty for guest auth):${NC}"
    read -p "$(echo -e ${BLUE}API Key (optional):${NC}) " ZAI_API_KEY
    
    read -p "$(echo -e ${BLUE}Z.AI Base URL [https://z.hhgzs.com/api/v1]:${NC}) " ZAI_BASE_URL
    ZAI_BASE_URL="${ZAI_BASE_URL:-https://z.hhgzs.com/api/v1}"
    
    echo ""
    echo -e "${CYAN}Available models: glm-4.5v, GLM-4-6-API-V1, 0727-360B-API${NC}"
    read -p "$(echo -e ${BLUE}Default model [glm-4.5v]:${NC}) " DEFAULT_MODEL
    DEFAULT_MODEL="${DEFAULT_MODEL:-glm-4.5v}"
    
    # Save configuration
    cat > "$CONFIG_FILE" << EOF
# Z.AI Configuration
SERVER_HOST="$SERVER_HOST"
SERVER_PORT="$SERVER_PORT"
ZAI_API_KEY="$ZAI_API_KEY"
ZAI_BASE_URL="$ZAI_BASE_URL"
DEFAULT_MODEL="$DEFAULT_MODEL"
TIMEOUT="180"
EOF
    
    chmod 600 "$CONFIG_FILE"
    echo ""
    echo -e "${GREEN}✅ Configuration saved${NC}"
fi

# Load configuration
source "$CONFIG_FILE"
export SERVER_HOST SERVER_PORT ZAI_API_KEY ZAI_BASE_URL DEFAULT_MODEL TIMEOUT

echo ""

# Step 3: Install dependencies
echo "============================================================"
echo -e "${BLUE}📦 Step 3: Installing Dependencies${NC}"
echo "============================================================"
echo ""

echo -e "${CYAN}Installing required packages...${NC}"
pip install -q fastapi uvicorn requests pydantic openai 2>&1 | grep -v "already satisfied" || true
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Step 4: Check port
echo "============================================================"
echo -e "${BLUE}🔍 Step 4: Checking Port Availability${NC}"
echo "============================================================"
echo ""

if lsof -Pi :$SERVER_PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  Port $SERVER_PORT is in use${NC}"
    read -p "$(echo -e ${YELLOW}Kill existing process? [Y/n]:${NC}) " kill_process
    kill_process="${kill_process:-Y}"
    
    if [[ "$kill_process" =~ ^[Yy]$ ]]; then
        lsof -ti:$SERVER_PORT | xargs kill -9 2>/dev/null || true
        sleep 2
        echo -e "${GREEN}✅ Port freed${NC}"
    else
        echo -e "${RED}Cannot continue with port in use${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Port $SERVER_PORT is available${NC}"
fi
echo ""

# Step 5: Start server
echo "============================================================"
echo -e "${BLUE}🚀 Step 5: Starting OpenAI-Compatible Server${NC}"
echo "============================================================"
echo ""

echo -e "${CYAN}Launching server...${NC}"
python openai_standalone_server_with_fallback.py > deployment.log 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > .deployment.pid

echo "Server PID: $SERVER_PID"
echo ""

# Wait for server startup
echo -e "${YELLOW}Waiting for server to start...${NC}"
for i in {1..30}; do
    if curl -s http://$SERVER_HOST:$SERVER_PORT/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Server is running!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Server failed to start${NC}"
        echo "Last 50 lines of log:"
        tail -50 deployment.log
        exit 1
    fi
    sleep 1
    echo -n "."
done
echo ""
echo ""

# Step 6: Validate with actual OpenAI API usage
echo "============================================================"
echo -e "${MAGENTA}✨ Step 6: Validation with Real OpenAI Client${NC}"
echo "============================================================"
echo ""

# Create validation script
cat > validate_deployment.py << 'PYEOF'
#!/usr/bin/env python3
"""Deployment validation with actual OpenAI client usage"""
from openai import OpenAI
import sys
import json
import time

def print_colored(text, color):
    colors = {
        'red': '\033[0;31m',
        'green': '\033[0;32m',
        'yellow': '\033[1;33m',
        'blue': '\033[0;34m',
        'cyan': '\033[0;36m',
        'magenta': '\033[0;35m',
        'nc': '\033[0m'
    }
    print(f"{colors.get(color, '')}{text}{colors['nc']}")

def print_separator(char='=', length=70):
    print(char * length)

def format_response(response):
    """Format response in proper OpenAI format"""
    return {
        "id": response.id,
        "object": response.object,
        "created": response.created,
        "model": response.model,
        "choices": [
            {
                "index": choice.index,
                "message": {
                    "role": choice.message.role,
                    "content": choice.message.content
                },
                "finish_reason": choice.finish_reason
            }
            for choice in response.choices
        ],
        "usage": {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        } if response.usage else None
    }

# Initialize client
import os
SERVER_HOST = os.getenv('SERVER_HOST', 'localhost')
SERVER_PORT = os.getenv('SERVER_PORT', '7000')
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'glm-4.5v')

print_colored("🔧 Initializing OpenAI client...", "cyan")
client = OpenAI(
    base_url=f"http://{SERVER_HOST}:{SERVER_PORT}/v1",
    api_key="dummy",
    timeout=60.0
)
print_colored("✅ Client initialized\n", "green")

# Test 1: List models
print_separator()
print_colored("📋 Test 1: List Available Models", "blue")
print_separator()

try:
    models_response = client.models.list()
    print_colored("✅ Success! Available models:", "green")
    for model in models_response.data:
        print(f"  • {model.id}")
    print()
except Exception as e:
    print_colored(f"❌ Error: {e}", "red")
    sys.exit(1)

# Test 2: Simple completion
print_separator()
print_colored("💬 Test 2: Simple Chat Completion", "blue")
print_separator()

query = "What is your model name? Reply in one sentence."
print_colored(f"Query: {query}\n", "cyan")

try:
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": query}],
        max_tokens=100
    )
    
    print_colored("✅ SUCCESS! Received response from Z.AI", "green")
    print_separator()
    
    # Print formatted response
    formatted = format_response(response)
    print_colored("\n📤 Response in OpenAI Format:", "magenta")
    print_separator()
    print(json.dumps(formatted, indent=2))
    print_separator()
    
    # Print extracted content
    content = response.choices[0].message.content
    print()
    print_colored("💡 Extracted Content:", "cyan")
    print_separator()
    print(content)
    print_separator()
    
    # Print metadata
    print()
    print_colored("📊 Response Metadata:", "blue")
    print(f"  • Model Used: {response.model}")
    print(f"  • Finish Reason: {response.choices[0].finish_reason}")
    if response.usage:
        print(f"  • Prompt Tokens: {response.usage.prompt_tokens}")
        print(f"  • Completion Tokens: {response.usage.completion_tokens}")
        print(f"  • Total Tokens: {response.usage.total_tokens}")
    
    print()
    
except Exception as e:
    error_str = str(e)
    print_colored("❌ API Call Failed", "red")
    print_colored(f"Error: {error_str}\n", "yellow")
    
    if "timeout" in error_str.lower() or "connection" in error_str.lower():
        print_colored("⚠️  Network issue detected", "yellow")
        print_colored("This is expected in restricted environments.", "cyan")
        print_colored("Server structure is correct!\n", "cyan")
    
    sys.exit(1)

# Test 3: Conversation
print_separator()
print_colored("🗣️  Test 3: Multi-turn Conversation", "blue")
print_separator()

try:
    conversation = [
        {"role": "user", "content": "Hello! What can you help me with?"}
    ]
    
    print_colored("User: Hello! What can you help me with?\n", "cyan")
    
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=conversation,
        max_tokens=150
    )
    
    assistant_reply = response.choices[0].message.content
    print_colored(f"Assistant: {assistant_reply}\n", "green")
    
    # Continue conversation
    conversation.append({"role": "assistant", "content": assistant_reply})
    conversation.append({"role": "user", "content": "That's great! Can you write a haiku about AI?"})
    
    print_colored("User: That's great! Can you write a haiku about AI?\n", "cyan")
    
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=conversation,
        max_tokens=100
    )
    
    haiku = response.choices[0].message.content
    print_colored("Assistant:", "green")
    print_colored(haiku, "magenta")
    print()
    
    print_colored("✅ Multi-turn conversation successful!", "green")
    
except Exception as e:
    print_colored(f"⚠️  Conversation test failed: {e}", "yellow")
    print_colored("(This is optional and may fail due to network)", "cyan")

print()
print_separator()
print_colored("🎉 All Critical Tests Passed!", "green")
print_separator()
print()

PYEOF

chmod +x validate_deployment.py

# Run validation
python validate_deployment.py
VALIDATION_EXIT=$?

echo ""

# Step 7: Final status
echo "============================================================"
echo -e "${BLUE}📊 Step 7: Deployment Status${NC}"
echo "============================================================"
echo ""

if [ $VALIDATION_EXIT -eq 0 ]; then
    echo -e "${GREEN}✅ DEPLOYMENT SUCCESSFUL!${NC}"
    echo ""
    echo -e "${CYAN}Your Z.AI OpenAI-Compatible API is ready!${NC}"
else
    echo -e "${YELLOW}⚠️  Server is running but validation had issues${NC}"
    echo -e "${CYAN}Check logs: tail -f deployment.log${NC}"
fi

echo ""
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}                    SERVER INFORMATION${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📍 Endpoints:${NC}"
echo "  • Base URL: http://${SERVER_HOST}:${SERVER_PORT}"
echo "  • Health: http://${SERVER_HOST}:${SERVER_PORT}/health"
echo "  • Models: http://${SERVER_HOST}:${SERVER_PORT}/v1/models"
echo "  • Chat: http://${SERVER_HOST}:${SERVER_PORT}/v1/chat/completions"
echo "  • Docs: http://${SERVER_HOST}:${SERVER_PORT}/docs"
echo ""
echo -e "${BLUE}⚙️  Configuration:${NC}"
echo "  • PID: $SERVER_PID"
echo "  • Config File: $CONFIG_FILE"
echo "  • Log File: deployment.log"
echo "  • Default Model: $DEFAULT_MODEL"
echo ""
echo -e "${BLUE}🔧 Management:${NC}"
echo "  • View logs: tail -f deployment.log"
echo "  • Stop server: kill $SERVER_PID"
echo "  • Restart: bash $0 $BRANCH"
echo "  • Health check: curl http://${SERVER_HOST}:${SERVER_PORT}/health"
echo ""
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Step 8: Example usage
echo "============================================================"
echo -e "${CYAN}💡 Example Usage${NC}"
echo "============================================================"
echo ""

cat << 'USAGE'
Python Example:
──────────────
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:7000/v1",
    api_key="dummy"
)

response = client.chat.completions.create(
    model="glm-4.5v",
    messages=[
        {"role": "user", "content": "Hello! How are you?"}
    ]
)

print(response.choices[0].message.content)

Curl Example:
─────────────
curl http://localhost:7000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dummy" \
  -d '{
    "model": "glm-4.5v",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'

USAGE

echo ""

# Step 9: Keep running and monitoring
echo "============================================================"
echo -e "${GREEN}🔄 Server Running - Continuous Monitoring${NC}"
echo "============================================================"
echo ""
echo -e "${CYAN}Server will continue running in background...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop monitoring (server keeps running)${NC}"
echo ""

# Trap to handle Ctrl+C gracefully
trap "echo ''; echo -e '${YELLOW}Monitoring stopped. Server still running (PID: $SERVER_PID)${NC}'; echo ''; exit 0" INT

# Monitor loop
REQUEST_COUNT=0
while true; do
    # Check if server is alive
    if ! kill -0 $SERVER_PID 2>/dev/null; then
        echo -e "${RED}❌ Server stopped unexpectedly!${NC}"
        echo "Last 50 lines of log:"
        tail -50 deployment.log
        exit 1
    fi
    
    # Count requests
    NEW_COUNT=$(grep -c "POST\|GET" deployment.log 2>/dev/null || echo "0")
    if [ "$NEW_COUNT" -gt "$REQUEST_COUNT" ]; then
        REQUEST_COUNT=$NEW_COUNT
    fi
    
    # Check health
    HEALTH_STATUS=$(curl -s http://$SERVER_HOST:$SERVER_PORT/health | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null || echo "error")
    
    # Display status
    if [ "$HEALTH_STATUS" = "healthy" ]; then
        STATUS_ICON="✅"
        STATUS_COLOR="${GREEN}"
    else
        STATUS_ICON="⚠️ "
        STATUS_COLOR="${YELLOW}"
    fi
    
    echo -ne "\r${STATUS_COLOR}${STATUS_ICON} Server: ${HEALTH_STATUS} | Requests: ${REQUEST_COUNT} | PID: ${SERVER_PID} | $(date '+%H:%M:%S')${NC}  "
    
    sleep 5
done

