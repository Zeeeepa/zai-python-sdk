#!/bin/bash

################################################################################
# Z.AI OpenAI Server - All-in-One Script
# 
# This script runs the complete workflow:
# 1. Setup (install dependencies, get token)
# 2. Start server
# 3. Send test request
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                                    ║${NC}"
echo -e "${CYAN}║           ${MAGENTA}🚀 Z.AI OpenAI Server - Complete Setup 🚀${CYAN}            ║${NC}"
echo -e "${CYAN}║                                                                    ║${NC}"
echo -e "${CYAN}║    This script will automatically:                                ║${NC}"
echo -e "${CYAN}║      1️⃣  Install all dependencies                                  ║${NC}"
echo -e "${CYAN}║      2️⃣  Retrieve authentication token                             ║${NC}"
echo -e "${CYAN}║      3️⃣  Start the OpenAI-compatible server                        ║${NC}"
echo -e "${CYAN}║      4️⃣  Send test requests and validate responses                 ║${NC}"
echo -e "${CYAN}║                                                                    ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Make sure all scripts are executable
chmod +x setup.sh start.sh send_request.sh 2>/dev/null || true

################################################################################
# Step 1: Setup
################################################################################

echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║  Step 1/4: Running Setup                                          ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ -f "setup.sh" ]; then
    if ./setup.sh; then
        echo ""
        echo -e "${GREEN}✅ Setup completed successfully!${NC}"
        echo ""
    else
        echo ""
        echo -e "${RED}❌ Setup failed!${NC}"
        echo "Please check the error messages above"
        exit 1
    fi
else
    echo -e "${RED}❌ setup.sh not found${NC}"
    exit 1
fi

sleep 2

################################################################################
# Step 2: Start Server
################################################################################

echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║  Step 2/4: Starting Server                                        ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ -f "start.sh" ]; then
    if ./start.sh; then
        echo ""
        echo -e "${GREEN}✅ Server started successfully!${NC}"
        echo ""
    else
        echo ""
        echo -e "${RED}❌ Server failed to start!${NC}"
        echo "Please check the error messages above"
        exit 1
    fi
else
    echo -e "${RED}❌ start.sh not found${NC}"
    exit 1
fi

sleep 2

################################################################################
# Step 3: Send Test Requests
################################################################################

echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║  Step 3/4: Sending Test Requests                                  ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ -f "send_request.sh" ]; then
    if ./send_request.sh; then
        echo ""
        echo -e "${GREEN}✅ All tests passed!${NC}"
        echo ""
    else
        echo ""
        echo -e "${YELLOW}⚠️  Some tests may have failed${NC}"
        echo "But the server is still running"
        echo ""
    fi
else
    echo -e "${RED}❌ send_request.sh not found${NC}"
    exit 1
fi

sleep 2

################################################################################
# Step 4: Final Summary
################################################################################

echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║  Step 4/4: Summary & Next Steps                                   ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Load config to get PORT
if [ -f ".env" ]; then
    export $(grep -v '^#' ".env" | xargs)
fi
PORT=${PORT:-8000}

# Get PID
PID=""
if [ -f ".server.pid" ]; then
    PID=$(cat .server.pid)
fi

echo -e "${GREEN}🎉 ${CYAN}Complete Setup Successful!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}📊 Server Status:${NC}"
echo "  🟢 Running on: http://localhost:${PORT}"
if [ -n "$PID" ]; then
    echo "  📋 Process ID: ${PID}"
fi
echo "  📁 Log file: server.log"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}🔗 Available Endpoints:${NC}"
echo ""
echo "  1️⃣  Health Check:"
echo "     curl http://localhost:${PORT}/health"
echo ""
echo "  2️⃣  List Models:"
echo "     curl http://localhost:${PORT}/v1/models"
echo ""
echo "  3️⃣  Chat Completion:"
echo "     curl -X POST http://localhost:${PORT}/v1/chat/completions \\"
echo "          -H 'Content-Type: application/json' \\"
echo "          -d '{\"model\":\"GLM-4.5\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello!\"}]}'"
echo ""
echo "  4️⃣  Interactive API Docs:"
echo "     open http://localhost:${PORT}/docs"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}🐍 Use with OpenAI Python SDK:${NC}"
echo ""
echo "  from openai import OpenAI"
echo ""
echo "  client = OpenAI("
echo "      base_url=\"http://localhost:${PORT}/v1\","
echo "      api_key=\"not-needed\""
echo "  )"
echo ""
echo "  response = client.chat.completions.create("
echo "      model=\"GLM-4.5\","
echo "      messages=[{\"role\": \"user\", \"content\": \"Hello!\"}]"
echo "  )"
echo ""
echo "  print(response.choices[0].message.content)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}⚙️  Control Commands:${NC}"
echo ""
echo "  📊 View logs:"
echo "     tail -f server.log"
echo ""
echo "  🛑 Stop server:"
if [ -n "$PID" ]; then
    echo "     kill ${PID}"
else
    echo "     kill \$(cat .server.pid)"
fi
echo ""
echo "  🔄 Restart server:"
echo "     ./start.sh"
echo ""
echo "  📤 Send more test requests:"
echo "     ./send_request.sh"
echo ""
echo "  ♻️  Re-run full setup:"
echo "     ./all.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}🎯 ${CYAN}Server is ready to accept OpenAI API requests!${NC}"
echo ""
echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║             Thank you for using Z.AI OpenAI Server! 💖             ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

