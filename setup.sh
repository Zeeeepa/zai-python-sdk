#!/bin/bash
#
# setup.sh - Setup Z.AI OpenAI-compatible API Server
# Installs dependencies, retrieves tokens, and prepares environment
#

set -e  # Exit on error

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Z.AI OpenAI-Compatible API Server - Setup                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

CONFIG_FILE="$SCRIPT_DIR/.env"
TOKEN_FILE="$SCRIPT_DIR/.zai_token"
DEFAULT_PORT=8080

# Step 1: Check Python
echo -e "${YELLOW}[1/5]${NC} Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 required${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $(python3 --version 2>&1 | awk '{print $2}')${NC}"

# Step 2: Install dependencies
echo -e "${YELLOW}[2/5]${NC} Installing dependencies..."
pip3 install -q fastapi uvicorn httpx pydantic pydantic-settings python-dotenv requests openai 2>&1 | grep -v "Requirement already satisfied" || true
echo -e "${GREEN}✓ Dependencies ready${NC}"

# Step 3: Configuration
echo -e "${YELLOW}[3/5]${NC} Creating configuration..."
cat > "$CONFIG_FILE" << EOF
ZAI_API_URL=https://chat.z.ai/api/chat/completions
ZAI_AUTH_URL=https://chat.z.ai/api/v1/auths/
ZAI_CHAT_URL=https://chat.z.ai/api/v1/chats/new
SERVER_PORT=${DEFAULT_PORT}
SERVER_HOST=0.0.0.0
OPENAI_API_KEY=sk-zai-proxy
EOF
echo -e "${GREEN}✓ Config created${NC}"

# Step 4: Get token
echo -e "${YELLOW}[4/5]${NC} Retrieving Z.AI token..."
TOKEN=$(curl -s "https://chat.z.ai/api/v1/auths/" \
    -H "User-Agent: Mozilla/5.0" \
    -H "Accept: application/json" | \
    python3 -c "import sys, json; print(json.load(sys.stdin).get('token', ''))" 2>/dev/null || echo "")

if [ -n "$TOKEN" ]; then
    echo "$TOKEN" > "$TOKEN_FILE"
    chmod 600 "$TOKEN_FILE"
    echo -e "${GREEN}✓ Token saved: ${TOKEN:0:30}...${NC}"
else
    echo -e "${YELLOW}⚠ No token (will retry at runtime)${NC}"
fi

# Step 5: Create server
echo -e "${YELLOW}[5/5]${NC} Creating server..."
# Server code will be created by start.sh if needed

echo ""
echo -e "${GREEN}✓ Setup complete!${NC}"
echo -e "Run: ${BLUE}./start.sh${NC} to start server"
echo -e "     ${BLUE}./send_request.sh${NC} to test"
echo -e "     ${BLUE}./all.sh${NC} for full demo"
echo ""

