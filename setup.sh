#!/bin/bash

################################################################################
# Z.AI OpenAI Server - Setup Script
# 
# This script:
# 1. Checks and installs all dependencies
# 2. Attempts automatic token retrieval (bookmarklet method)
# 3. Sets up configuration files
# 4. Validates the setup
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/Zeeeepa/zai-python-sdk.git"
REPO_DIR="zai-python-sdk"
CONFIG_FILE=".env"

echo "========================================================================"
echo "🚀 Z.AI OpenAI Server - Automated Setup"
echo "========================================================================"
echo ""

################################################################################
# Step 1: Check if we're in the right directory
################################################################################

if [ -f "server.py" ] && [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✅ Found existing repository${NC}"
else
    echo -e "${YELLOW}📦 Repository not found locally${NC}"
    
    if [ -d "$REPO_DIR" ]; then
        echo -e "${YELLOW}⚠️  Found existing directory, updating...${NC}"
        cd "$REPO_DIR"
        git pull origin feature/openai-api-server
    else
        echo -e "${BLUE}📥 Cloning repository...${NC}"
        git clone -b feature/openai-api-server "$REPO_URL" "$REPO_DIR"
        cd "$REPO_DIR"
    fi
fi

echo ""

################################################################################
# Step 2: Check Python version
################################################################################

echo -e "${BLUE}🐍 Checking Python installation...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python ${PYTHON_VERSION} found${NC}"
echo ""

################################################################################
# Step 3: Install Python dependencies
################################################################################

echo -e "${BLUE}📦 Installing Python dependencies...${NC}"

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q 2>&1 | grep -v "already satisfied" || true
    echo -e "${GREEN}✅ Python dependencies installed${NC}"
else
    echo -e "${RED}❌ requirements.txt not found${NC}"
    exit 1
fi

echo ""

################################################################################
# Step 4: Install Playwright (optional, for automation)
################################################################################

echo -e "${BLUE}🎭 Checking Playwright...${NC}"

if pip show playwright &> /dev/null; then
    echo -e "${GREEN}✅ Playwright already installed${NC}"
    
    # Check if browser is installed
    if playwright install chromium --dry-run 2>&1 | grep -q "is already installed"; then
        echo -e "${GREEN}✅ Chromium browser already installed${NC}"
    else
        echo -e "${YELLOW}📥 Installing Chromium browser...${NC}"
        playwright install chromium
        echo -e "${GREEN}✅ Chromium installed${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Playwright not installed (optional for automation)${NC}"
    read -p "Install Playwright for automated login? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install playwright pillow pytesseract -q
        playwright install chromium
        echo -e "${GREEN}✅ Playwright installed${NC}"
    fi
fi

echo ""

################################################################################
# Step 5: Token Retrieval
################################################################################

echo "========================================================================"
echo "🔐 Authentication Token Setup"
echo "========================================================================"
echo ""

TOKEN=""

# Check if token already exists in config
if [ -f "$CONFIG_FILE" ]; then
    SOURCE_TOKEN=$(grep -E "^ZAI_TOKEN=" "$CONFIG_FILE" 2>/dev/null | cut -d'=' -f2- | tr -d '"' | tr -d "'")
    if [ -n "$SOURCE_TOKEN" ] && [ "$SOURCE_TOKEN" != "your_token_here" ]; then
        echo -e "${GREEN}✅ Found existing token in $CONFIG_FILE${NC}"
        TOKEN="$SOURCE_TOKEN"
    fi
fi

# Check environment variable
if [ -z "$TOKEN" ] && [ -n "$ZAI_TOKEN" ]; then
    echo -e "${GREEN}✅ Found token in environment variable${NC}"
    TOKEN="$ZAI_TOKEN"
fi

# If no token found, offer retrieval options
if [ -z "$TOKEN" ]; then
    echo -e "${YELLOW}⚠️  No authentication token found${NC}"
    echo ""
    echo "Choose token retrieval method:"
    echo "  1) Use Guest Token (automatic, limited features)"
    echo "  2) Manual Entry (paste your token)"
    echo "  3) Automated Login with Playwright (requires credentials)"
    echo "  4) Skip for now (use guest token at runtime)"
    echo ""
    read -p "Select option [1-4]: " -n 1 -r OPTION
    echo ""
    echo ""
    
    case $OPTION in
        1)
            echo -e "${BLUE}🔓 Using Guest Token mode${NC}"
            echo "The server will automatically get a guest token at startup"
            TOKEN="USE_GUEST_TOKEN"
            ;;
        2)
            echo -e "${BLUE}📝 Manual Token Entry${NC}"
            echo ""
            echo "To get your token manually:"
            echo "  1. Go to https://chat.z.ai/ and login"
            echo "  2. Press F12 to open DevTools"
            echo "  3. Go to Console tab"
            echo "  4. Paste and run:"
            echo "     localStorage.getItem('token')"
            echo "  5. Copy the token (without quotes)"
            echo ""
            read -p "Enter your Z.AI token: " TOKEN
            
            # Validate token format
            if [[ ! $TOKEN =~ ^eyJ ]]; then
                echo -e "${RED}❌ Invalid token format (should start with 'eyJ')${NC}"
                echo "Falling back to guest token mode"
                TOKEN="USE_GUEST_TOKEN"
            else
                echo -e "${GREEN}✅ Token validated (format)${NC}"
            fi
            ;;
        3)
            if [ -f "login_with_captcha.py" ] && command -v playwright &> /dev/null; then
                echo -e "${BLUE}🤖 Automated Login${NC}"
                echo ""
                read -p "Enter your Z.AI email: " ZAI_EMAIL
                read -s -p "Enter your Z.AI password: " ZAI_PASSWORD
                echo ""
                echo ""
                echo -e "${BLUE}🔄 Attempting automated login...${NC}"
                
                export ZAI_EMAIL ZAI_PASSWORD
                
                # Run login script
                if python3 login_with_captcha.py; then
                    if [ -f "/tmp/zai_token.txt" ]; then
                        TOKEN=$(cat /tmp/zai_token.txt)
                        echo -e "${GREEN}✅ Token retrieved successfully!${NC}"
                    else
                        echo -e "${RED}❌ Login failed - token file not found${NC}"
                        echo "Falling back to guest token mode"
                        TOKEN="USE_GUEST_TOKEN"
                    fi
                else
                    echo -e "${RED}❌ Automated login failed${NC}"
                    echo "Falling back to guest token mode"
                    TOKEN="USE_GUEST_TOKEN"
                fi
            else
                echo -e "${RED}❌ Playwright not installed${NC}"
                echo "Falling back to guest token mode"
                TOKEN="USE_GUEST_TOKEN"
            fi
            ;;
        4)
            echo -e "${BLUE}⏭️  Skipping token setup${NC}"
            TOKEN="USE_GUEST_TOKEN"
            ;;
        *)
            echo -e "${YELLOW}Invalid option, using guest token${NC}"
            TOKEN="USE_GUEST_TOKEN"
            ;;
    esac
fi

echo ""

################################################################################
# Step 6: Create configuration file
################################################################################

echo -e "${BLUE}📝 Creating configuration file...${NC}"

# Determine port
if [ -z "$PORT" ]; then
    PORT=8000
fi

# Create .env file
cat > "$CONFIG_FILE" << EOF
# Z.AI OpenAI Server Configuration
# Generated on $(date)

# Server Configuration
PORT=${PORT}
LISTEN_PORT=${PORT}

# Authentication
# Set to your Z.AI user token for full features
# Or use "USE_GUEST_TOKEN" for automatic guest token (limited features)
ZAI_TOKEN="${TOKEN}"

# Token Mode
# Set to true to use guest token (no login required)
# Set to false to use ZAI_TOKEN above
USE_GUEST_TOKEN=$([ "$TOKEN" = "USE_GUEST_TOKEN" ] && echo "true" || echo "false")

# Logging
DEBUG_LOGGING=false

# Service Name
SERVICE_NAME=zai-openai-server
EOF

echo -e "${GREEN}✅ Configuration file created: $CONFIG_FILE${NC}"
echo ""

################################################################################
# Step 7: Validate Setup
################################################################################

echo "========================================================================"
echo "✅ Setup Validation"
echo "========================================================================"
echo ""

# Check server file
if [ -f "server.py" ]; then
    echo -e "${GREEN}✅ server.py found${NC}"
else
    echo -e "${RED}❌ server.py not found${NC}"
    exit 1
fi

# Check test file
if [ -f "test_server.py" ]; then
    echo -e "${GREEN}✅ test_server.py found${NC}"
else
    echo -e "${YELLOW}⚠️  test_server.py not found (optional)${NC}"
fi

# Validate Python imports
echo -e "${BLUE}🔍 Validating Python imports...${NC}"
python3 -c "import fastapi, uvicorn, httpx, pydantic" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ All required Python packages are available${NC}"
else
    echo -e "${RED}❌ Some Python packages are missing${NC}"
    exit 1
fi

echo ""

################################################################################
# Step 8: Summary
################################################################################

echo "========================================================================"
echo "🎉 Setup Complete!"
echo "========================================================================"
echo ""
echo "Configuration Summary:"
echo "  📍 Server Port: ${PORT}"
echo "  🔐 Auth Mode: $([ "$TOKEN" = "USE_GUEST_TOKEN" ] && echo "Guest Token (automatic)" || echo "User Token")"
echo "  📁 Config File: $CONFIG_FILE"
echo ""
echo "Next Steps:"
echo "  1. Start the server:"
echo "     ./start.sh"
echo ""
echo "  2. Send test request:"
echo "     ./send_request.sh"
echo ""
echo "  3. Or run everything:"
echo "     ./all.sh"
echo ""
echo "Server Endpoints (after starting):"
echo "  📊 Health: http://localhost:${PORT}/health"
echo "  📋 Models: http://localhost:${PORT}/v1/models"
echo "  💬 Chat: http://localhost:${PORT}/v1/chat/completions"
echo "  📖 Docs: http://localhost:${PORT}/docs"
echo ""
echo "========================================================================"

