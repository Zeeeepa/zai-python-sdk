#!/bin/bash
#
# Z.AI Python SDK Deployment Script
# Automates setup, installation, server startup, and testing
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/Zeeeepa/zai-python-sdk.git"
REPO_DIR="zai-python-sdk"
DEFAULT_PORT=8080
SERVER_PID_FILE=".server.pid"

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        print_success "$1 is installed"
        return 0
    else
        print_error "$1 is not installed"
        return 1
    fi
}

find_free_port() {
    local port=$1
    while lsof -i:$port &> /dev/null; do
        port=$((port + 1))
    done
    echo $port
}

# Main script
main() {
    print_header "Z.AI SDK Deployment"
    
    # Check prerequisites
    print_info "Checking prerequisites..."
    
    if ! check_command python3; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    if ! check_command pip3 && ! check_command pip; then
        print_error "pip is required but not installed"
        exit 1
    fi
    
    if ! check_command git; then
        print_error "git is required but not installed"
        exit 1
    fi
    
    # Check if repo exists
    if [ ! -d "$REPO_DIR" ]; then
        print_info "Repository not found. Cloning from $REPO_URL..."
        if git clone "$REPO_URL" "$REPO_DIR"; then
            print_success "Repository cloned successfully"
        else
            print_error "Failed to clone repository"
            exit 1
        fi
    else
        print_success "Repository already exists"
        print_info "Updating repository..."
        cd "$REPO_DIR"
        git pull origin main || print_info "Could not pull latest changes (continuing anyway)"
        cd ..
    fi
    
    # Navigate to repo
    cd "$REPO_DIR"
    print_success "Changed directory to $REPO_DIR"
    
    # Install dependencies
    print_header "Installing Dependencies"
    
    if [ -f "requirements.txt" ]; then
        print_info "Installing from requirements.txt..."
        if pip3 install -r requirements.txt 2>/dev/null || pip install -r requirements.txt; then
            print_success "Dependencies installed successfully"
        else
            print_error "Failed to install dependencies"
            exit 1
        fi
    else
        print_info "No requirements.txt found, installing basic dependencies..."
        pip3 install requests 2>/dev/null || pip install requests
    fi
    
    # Install package in development mode
    print_info "Installing Z.AI SDK in development mode..."
    if pip3 install -e . 2>/dev/null || pip install -e .; then
        print_success "Z.AI SDK installed successfully"
    else
        print_info "Development install failed, continuing anyway..."
    fi
    
    # Find available port
    print_header "Port Configuration"
    SELECTED_PORT=$(find_free_port $DEFAULT_PORT)
    
    if [ "$SELECTED_PORT" != "$DEFAULT_PORT" ]; then
        print_info "Port $DEFAULT_PORT is in use, using port $SELECTED_PORT instead"
    else
        print_success "Using port $SELECTED_PORT"
    fi
    
    # Start server in background
    print_header "Starting Server"
    
    print_info "Launching Z.AI OpenAI-Compatible API Server on port $SELECTED_PORT..."
    
    # Kill any existing server
    if [ -f "$SERVER_PID_FILE" ]; then
        OLD_PID=$(cat "$SERVER_PID_FILE")
        if ps -p $OLD_PID > /dev/null 2>&1; then
            print_info "Stopping existing server (PID: $OLD_PID)..."
            kill $OLD_PID 2>/dev/null || true
            sleep 2
        fi
        rm -f "$SERVER_PID_FILE"
    fi
    
    # Start new server
    python3 main.py --port $SELECTED_PORT > server.log 2>&1 &
    SERVER_PID=$!
    echo $SERVER_PID > "$SERVER_PID_FILE"
    
    print_success "Server started (PID: $SERVER_PID)"
    print_info "Waiting for server to initialize..."
    sleep 3
    
    # Check if server is running
    if ! ps -p $SERVER_PID > /dev/null 2>&1; then
        print_error "Server failed to start"
        print_info "Check server.log for details:"
        tail -20 server.log
        exit 1
    fi
    
    # Test health endpoint
    print_header "Testing Server"
    
    print_info "Testing health endpoint..."
    if curl -s "http://localhost:$SELECTED_PORT/health" > /dev/null 2>&1; then
        print_success "Health check passed"
        HEALTH_RESPONSE=$(curl -s "http://localhost:$SELECTED_PORT/health")
        echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
    else
        print_error "Health check failed"
        exit 1
    fi
    
    echo ""
    print_info "Testing models endpoint..."
    if curl -s "http://localhost:$SELECTED_PORT/v1/models" > /dev/null 2>&1; then
        print_success "Models endpoint accessible"
        MODELS_RESPONSE=$(curl -s "http://localhost:$SELECTED_PORT/v1/models")
        echo "$MODELS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$MODELS_RESPONSE"
    else
        print_error "Models endpoint failed"
    fi
    
    # Test chat completion
    print_header "Testing Chat Completion"
    
    print_info "Sending test chat request..."
    
    TEST_RESPONSE=$(curl -s -X POST "http://localhost:$SELECTED_PORT/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d '{
            "model": "glm-4.5v",
            "messages": [
                {"role": "user", "content": "Say hello and tell me your name in one sentence."}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }')
    
    if echo "$TEST_RESPONSE" | grep -q "error"; then
        print_error "Chat completion test failed"
        echo "$TEST_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$TEST_RESPONSE"
    else
        print_success "Chat completion test passed"
        echo ""
        print_info "Response:"
        echo "$TEST_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$TEST_RESPONSE"
        
        # Extract and display just the content
        echo ""
        print_info "Assistant response:"
        CONTENT=$(echo "$TEST_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null)
        echo -e "${GREEN}${CONTENT}${NC}"
    fi
    
    # Final status
    print_header "Deployment Complete"
    
    echo ""
    print_success "Z.AI API Server is running!"
    echo ""
    echo -e "${BLUE}Server Information:${NC}"
    echo "  • Base URL: http://localhost:$SELECTED_PORT"
    echo "  • PID: $SERVER_PID"
    echo "  • Log file: server.log"
    echo ""
    echo -e "${BLUE}Available Endpoints:${NC}"
    echo "  • GET  /health"
    echo "  • GET  /v1/models"
    echo "  • POST /v1/chat/completions"
    echo ""
    echo -e "${BLUE}OpenAI SDK Configuration:${NC}"
    echo "  from openai import OpenAI"
    echo "  client = OpenAI("
    echo "      base_url='http://localhost:$SELECTED_PORT/v1',"
    echo "      api_key='dummy-key'  # Not required"
    echo "  )"
    echo ""
    echo -e "${BLUE}Management Commands:${NC}"
    echo "  • View logs: tail -f server.log"
    echo "  • Stop server: kill $SERVER_PID"
    echo "  • Check status: ps -p $SERVER_PID"
    echo ""
    
    print_info "Server is running in the background. Press Ctrl+C to exit this script (server will continue running)."
    echo ""
    
    # Keep script running to show logs
    print_info "Streaming server logs (Ctrl+C to exit)..."
    echo ""
    tail -f server.log
}

# Run main function
main

