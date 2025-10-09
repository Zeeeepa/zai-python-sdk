#!/bin/bash
# Z.AI OpenAI-Compatible API - Simple Deployment Script
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

REPO="Zeeeepa/zai-python-sdk"
BRANCH="${1:-main}"
PROJECT_DIR="zai-openai-api"

clear
echo ""
echo "============================================================"
echo -e "${CYAN}🚀 Z.AI OpenAI-Compatible API - Deployment${NC}"
echo "============================================================"
echo "Repository: $REPO"
echo "Branch: $BRANCH"
echo ""

# Step 1: Clone
echo "Step 1: Cloning Repository..."
if [ -d "$PROJECT_DIR" ]; then
    rm -rf "$PROJECT_DIR"
fi
git clone --depth 1 --branch "$BRANCH" "https://github.com/${REPO}.git" "$PROJECT_DIR"
cd "$PROJECT_DIR"
echo -e "${GREEN}✅ Cloned${NC}"
echo ""

# Step 2: Configure with defaults
echo "Step 2: Creating Configuration..."
cat > .env.zai << 'EOF'
SERVER_HOST="0.0.0.0"
SERVER_PORT="7000"
ZAI_API_KEY=""
ZAI_BASE_URL="https://z.hhgzs.com/api/v1"
DEFAULT_MODEL="glm-4.5v"
TIMEOUT="10"
EOF

source .env.zai
export SERVER_HOST SERVER_PORT ZAI_API_KEY ZAI_BASE_URL DEFAULT_MODEL TIMEOUT
echo -e "${GREEN}✅ Configured (host:$SERVER_HOST port:$SERVER_PORT model:$DEFAULT_MODEL)${NC}"
echo ""

# Step 3: Install dependencies
echo "Step 3: Installing Dependencies..."
pip install -q fastapi uvicorn requests pydantic openai 2>&1 | grep -v "already satisfied" | head -3 || true
echo -e "${GREEN}✅ Installed${NC}"
echo ""

# Step 4: Start server
echo "Step 4: Starting Server..."
python openai_standalone_server_with_fallback.py > deployment.log 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > .deployment.pid
echo "Server PID: $SERVER_PID"

# Wait for startup
for i in {1..15}; do
    if curl -s http://localhost:7000/health >/dev/null 2>&1; then
        break
    fi
    sleep 1
done
echo -e "${GREEN}✅ Server Running${NC}"
echo ""

# Step 5: Validate
echo "Step 5: Validation with OpenAI Client..."
echo "============================================================"
python << 'PYTEST'
from openai import OpenAI
import json

client = OpenAI(base_url="http://localhost:7000/v1", api_key="dummy", timeout=30)

print("\n✅ Test 1: List Models")
models = client.models.list()
print(f"Found {len(models.data)} models: {[m.id for m in models.data[:3]]}")

print("\n✅ Test 2: Chat Completion")
response = client.chat.completions.create(
    model="glm-4.5v",
    messages=[{"role": "user", "content": "What is your model name?"}]
)

print("\n📤 OpenAI Format Response:")
print("="*70)
print(json.dumps({
    "id": response.id,
    "model": response.model,
    "choices": [{
        "message": response.choices[0].message.model_dump(),
        "finish_reason": response.choices[0].finish_reason
    }],
    "usage": response.usage.model_dump() if response.usage else None
}, indent=2))
print("="*70)

print("\n💬 Content:")
print("-"*70)
print(response.choices[0].message.content)
print("-"*70)

print("\n✅ Test 3: Haiku")
r = client.chat.completions.create(
    model="glm-4.5v",
    messages=[{"role": "user", "content": "Write a haiku"}]
)
print(r.choices[0].message.content)

print("\n✅ ALL TESTS PASSED!")
PYTEST

echo ""
echo "============================================================"
echo -e "${GREEN}✅ DEPLOYMENT SUCCESSFUL!${NC}"
echo "============================================================"
echo ""
echo "Server Information:"
echo "  • URL: http://localhost:7000"
echo "  • Health: http://localhost:7000/health"
echo "  • Docs: http://localhost:7000/docs"
echo "  • PID: $SERVER_PID"
echo "  • Logs: deployment.log"
echo ""
echo "To stop: kill $SERVER_PID"
echo ""
echo "Server running in background. Press Ctrl+C to exit monitoring."
echo ""

# Monitor
trap "echo ''; echo 'Monitoring stopped. Server still running (PID: $SERVER_PID)'; exit 0" INT

while true; do
    if ! kill -0 $SERVER_PID 2>/dev/null; then
        echo "Server stopped!"
        exit 1
    fi
    REQS=$(grep -c "POST\|GET" deployment.log 2>/dev/null || echo "0")
    echo -ne "\r✅ Server alive - Requests: $REQS - $(date '+%H:%M:%S')  "
    sleep 5
done
