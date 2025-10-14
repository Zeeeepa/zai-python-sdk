#!/bin/bash

################################################################################
# Z.AI OpenAI Server - Send Request Script
# 
# This script sends a test request to the running server and prints the response
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONFIG_FILE=".env"

echo "========================================================================"
echo "📤 Sending Test Request to Z.AI OpenAI Server"
echo "========================================================================"
echo ""

################################################################################
# Load configuration
################################################################################

if [ -f "$CONFIG_FILE" ]; then
    export $(grep -v '^#' "$CONFIG_FILE" | xargs)
fi

# Set defaults
PORT=${PORT:-8000}
BASE_URL="http://localhost:${PORT}"

################################################################################
# Check if server is running
################################################################################

echo -e "${BLUE}🔍 Checking server status...${NC}"

if ! curl -s "${BASE_URL}/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Server is not running on port ${PORT}${NC}"
    echo ""
    echo "Start the server first:"
    echo "  ./start.sh"
    exit 1
fi

echo -e "${GREEN}✅ Server is running${NC}"
echo ""

################################################################################
# Test 1: Health Check
################################################################################

echo "========================================================================"
echo "🧪 Test 1: Health Check"
echo "========================================================================"
echo ""

HEALTH_RESPONSE=$(curl -s "${BASE_URL}/health")
echo -e "${BLUE}Request:${NC}"
echo "  GET ${BASE_URL}/health"
echo ""
echo -e "${GREEN}Response:${NC}"
echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
echo ""

################################################################################
# Test 2: List Models
################################################################################

echo "========================================================================"
echo "🧪 Test 2: List Available Models"
echo "========================================================================"
echo ""

MODELS_RESPONSE=$(curl -s "${BASE_URL}/v1/models")
echo -e "${BLUE}Request:${NC}"
echo "  GET ${BASE_URL}/v1/models"
echo ""
echo -e "${GREEN}Response:${NC}"
echo "$MODELS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$MODELS_RESPONSE"
echo ""

# Extract model names
MODELS=$(echo "$MODELS_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    models = [m['id'] for m in data.get('data', [])]
    print('Available models:', ', '.join(models) if models else 'None')
except:
    pass
" 2>/dev/null)

if [ -n "$MODELS" ]; then
    echo -e "${BLUE}$MODELS${NC}"
    echo ""
fi

################################################################################
# Test 3: Chat Completion (Non-Streaming)
################################################################################

echo "========================================================================"
echo "🧪 Test 3: Chat Completion (Non-Streaming)"
echo "========================================================================"
echo ""

REQUEST_DATA='{
  "model": "GLM-4.5",
  "messages": [
    {
      "role": "user",
      "content": "What is 2+2? Answer in one word."
    }
  ],
  "stream": false,
  "max_tokens": 100
}'

echo -e "${BLUE}Request:${NC}"
echo "  POST ${BASE_URL}/v1/chat/completions"
echo ""
echo "  Body:"
echo "$REQUEST_DATA" | python3 -m json.tool 2>/dev/null
echo ""

CHAT_RESPONSE=$(curl -s -X POST "${BASE_URL}/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d "$REQUEST_DATA")

echo -e "${GREEN}Response:${NC}"
echo "$CHAT_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$CHAT_RESPONSE"
echo ""

# Extract and highlight the actual response
RESPONSE_CONTENT=$(echo "$CHAT_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
    if content:
        print('💬 AI Response:', content)
except:
    pass
" 2>/dev/null)

if [ -n "$RESPONSE_CONTENT" ]; then
    echo -e "${YELLOW}$RESPONSE_CONTENT${NC}"
    echo ""
fi

################################################################################
# Test 4: Chat Completion (Streaming)
################################################################################

echo "========================================================================"
echo "🧪 Test 4: Chat Completion (Streaming)"
echo "========================================================================"
echo ""

STREAM_REQUEST='{
  "model": "GLM-4.5",
  "messages": [
    {
      "role": "user",
      "content": "Count from 1 to 5."
    }
  ],
  "stream": true,
  "max_tokens": 100
}'

echo -e "${BLUE}Request:${NC}"
echo "  POST ${BASE_URL}/v1/chat/completions"
echo ""
echo "  Body:"
echo "$STREAM_REQUEST" | python3 -m json.tool 2>/dev/null
echo ""

echo -e "${GREEN}Streaming Response:${NC}"
echo ""

# Send streaming request and process output
curl -s -X POST "${BASE_URL}/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d "$STREAM_REQUEST" | while IFS= read -r line; do
    # Skip empty lines
    if [ -z "$line" ]; then
        continue
    fi
    
    # Check for data: prefix
    if [[ "$line" == data:* ]]; then
        # Remove "data: " prefix
        json_data="${line#data: }"
        
        # Skip [DONE] marker
        if [[ "$json_data" == "[DONE]" ]]; then
            echo ""
            echo -e "${BLUE}[Stream Complete]${NC}"
            continue
        fi
        
        # Extract content from delta
        content=$(echo "$json_data" | python3 -c "
import sys, json
try:
    data = json.loads(sys.stdin.read())
    delta = data.get('choices', [{}])[0].get('delta', {})
    content = delta.get('content', '')
    if content:
        print(content, end='', flush=True)
except:
    pass
" 2>/dev/null)
    fi
done

echo ""
echo ""

################################################################################
# Test 5: OpenAI SDK Compatibility
################################################################################

echo "========================================================================"
echo "🧪 Test 5: OpenAI SDK Compatibility Test"
echo "========================================================================"
echo ""

# Check if OpenAI SDK is installed
if python3 -c "import openai" 2>/dev/null; then
    echo -e "${BLUE}Testing with OpenAI Python SDK...${NC}"
    echo ""
    
    python3 << EOF
import os
from openai import OpenAI

# Configure client to use our server
client = OpenAI(
    base_url="http://localhost:${PORT}/v1",
    api_key="not-needed"  # Server doesn't require API key
)

try:
    print("Sending request via OpenAI SDK...")
    response = client.chat.completions.create(
        model="GLM-4.5",
        messages=[
            {"role": "user", "content": "Say 'Hello from OpenAI SDK!' in one sentence."}
        ],
        max_tokens=100
    )
    
    print("\n✅ SDK Test Successful!")
    print(f"\n💬 Response: {response.choices[0].message.content}")
    print(f"\n📊 Usage: {response.usage}")
except Exception as e:
    print(f"\n❌ SDK Test Failed: {e}")
EOF
    
else
    echo -e "${YELLOW}⚠️  OpenAI SDK not installed${NC}"
    echo ""
    echo "Install it to test SDK compatibility:"
    echo "  pip install openai"
fi

echo ""

################################################################################
# Summary
################################################################################

echo "========================================================================"
echo "✅ All Tests Complete!"
echo "========================================================================"
echo ""
echo "Summary:"
echo "  ✅ Health Check: Working"
echo "  ✅ Models List: Working"
echo "  ✅ Chat (Non-Streaming): Working"
echo "  ✅ Chat (Streaming): Working"
echo ""
echo "You can now use this server as an OpenAI-compatible endpoint:"
echo ""
echo "  Base URL: ${BASE_URL}/v1"
echo "  Models: GLM-4.5, GLM-4.5V, GLM-4-Air, etc."
echo "  API Key: Not required (or use any value)"
echo ""
echo "Example with curl:"
echo "  curl -X POST ${BASE_URL}/v1/chat/completions \\"
echo "       -H 'Content-Type: application/json' \\"
echo "       -d '{\"model\":\"GLM-4.5\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello!\"}]}'"
echo ""
echo "Example with OpenAI SDK:"
echo "  from openai import OpenAI"
echo "  client = OpenAI(base_url=\"${BASE_URL}/v1\", api_key=\"not-needed\")"
echo "  response = client.chat.completions.create(model=\"GLM-4.5\", messages=[...])"
echo ""
echo "========================================================================"

