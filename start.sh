#!/bin/bash

################################################################################
# Z.AI OpenAI Server - Start Script
# 
# This script starts the server on the specified port
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONFIG_FILE=".env"
PID_FILE=".server.pid"
LOG_FILE="server.log"

echo "========================================================================"
echo "🚀 Starting Z.AI OpenAI Server"
echo "========================================================================"
echo ""

################################################################################
# Load configuration
################################################################################

if [ -f "$CONFIG_FILE" ]; then
    echo -e "${BLUE}📋 Loading configuration from $CONFIG_FILE${NC}"
    export $(grep -v '^#' "$CONFIG_FILE" | xargs)
else
    echo -e "${YELLOW}⚠️  No configuration file found${NC}"
    echo "Run ./setup.sh first"
    exit 1
fi

# Set defaults
PORT=${PORT:-8000}
USE_GUEST_TOKEN=${USE_GUEST_TOKEN:-true}

echo -e "${GREEN}✅ Configuration loaded${NC}"
echo "  📍 Port: ${PORT}"
echo "  🔐 Guest Mode: ${USE_GUEST_TOKEN}"
echo ""

################################################################################
# Check if server is already running
################################################################################

if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Server already running (PID: $OLD_PID)${NC}"
        read -p "Kill existing server and restart? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}🛑 Stopping existing server...${NC}"
            kill "$OLD_PID" 2>/dev/null || true
            sleep 2
        else
            echo -e "${BLUE}Keeping existing server running${NC}"
            echo ""
            echo "Server Info:"
            echo "  📍 URL: http://localhost:${PORT}"
            echo "  📖 Docs: http://localhost:${PORT}/docs"
            echo "  📋 PID: $OLD_PID"
            exit 0
        fi
    fi
fi

################################################################################
# Check if server file exists
################################################################################

if [ ! -f "server.py" ]; then
    echo -e "${RED}❌ server.py not found${NC}"
    echo "Make sure you're in the correct directory"
    exit 1
fi

################################################################################
# Start the server
################################################################################

echo -e "${BLUE}🔄 Starting server...${NC}"

# Export environment variables
export USE_GUEST_TOKEN PORT

# Start server in background
nohup python3 server.py > "$LOG_FILE" 2>&1 &
SERVER_PID=$!

# Save PID
echo "$SERVER_PID" > "$PID_FILE"

echo -e "${GREEN}✅ Server starting (PID: $SERVER_PID)${NC}"
echo ""

################################################################################
# Wait for server to be ready
################################################################################

echo -e "${BLUE}⏳ Waiting for server to be ready...${NC}"

MAX_WAIT=30
WAITED=0

while [ $WAITED -lt $MAX_WAIT ]; do
    if curl -s "http://localhost:${PORT}/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Server is ready!${NC}"
        break
    fi
    
    # Check if process is still running
    if ! ps -p "$SERVER_PID" > /dev/null 2>&1; then
        echo -e "${RED}❌ Server process died${NC}"
        echo ""
        echo "Last 20 lines of log:"
        tail -20 "$LOG_FILE"
        exit 1
    fi
    
    sleep 1
    WAITED=$((WAITED + 1))
    echo -n "."
done

echo ""
echo ""

if [ $WAITED -ge $MAX_WAIT ]; then
    echo -e "${RED}❌ Server failed to start within ${MAX_WAIT} seconds${NC}"
    echo ""
    echo "Check logs:"
    echo "  tail -f $LOG_FILE"
    exit 1
fi

################################################################################
# Test endpoints
################################################################################

echo "========================================================================"
echo "🧪 Testing Endpoints"
echo "========================================================================"
echo ""

# Test health
echo -e "${BLUE}1. Testing /health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s "http://localhost:${PORT}/health")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Health endpoint working${NC}"
    echo "   Response: $HEALTH_RESPONSE"
else
    echo -e "${RED}❌ Health endpoint failed${NC}"
fi
echo ""

# Test models
echo -e "${BLUE}2. Testing /v1/models endpoint...${NC}"
MODELS_COUNT=$(curl -s "http://localhost:${PORT}/v1/models" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('data', [])))" 2>/dev/null || echo "0")
if [ "$MODELS_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ Models endpoint working (${MODELS_COUNT} models available)${NC}"
else
    echo -e "${YELLOW}⚠️  Models endpoint returned no models${NC}"
fi
echo ""

################################################################################
# Summary
################################################################################

echo "========================================================================"
echo "🎉 Server Started Successfully!"
echo "========================================================================"
echo ""
echo "Server Information:"
echo "  📍 Base URL: http://localhost:${PORT}"
echo "  📋 Process ID: ${SERVER_PID}"
echo "  📝 Log File: ${LOG_FILE}"
echo ""
echo "Available Endpoints:"
echo "  📊 Health Check:"
echo "     curl http://localhost:${PORT}/health"
echo ""
echo "  📋 List Models:"
echo "     curl http://localhost:${PORT}/v1/models"
echo ""
echo "  💬 Chat Completion:"
echo "     curl -X POST http://localhost:${PORT}/v1/chat/completions \\"
echo "          -H 'Content-Type: application/json' \\"
echo "          -d '{\"model\":\"GLM-4.5\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello!\"}]}'"
echo ""
echo "  📖 Interactive Docs:"
echo "     open http://localhost:${PORT}/docs"
echo ""
echo "Control Commands:"
echo "  📊 View logs: tail -f ${LOG_FILE}"
echo "  🛑 Stop server: kill ${SERVER_PID}"
echo "  🔄 Restart: ./start.sh"
echo ""
echo "========================================================================"

