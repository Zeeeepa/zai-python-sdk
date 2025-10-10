#!/bin/bash
################################################################################
# Z.AI OpenAI-Compatible API Server - Deployment Script
# 
# This script automates the complete deployment process:
# 1. Clone repository (if not present)
# 2. Install dependencies
# 3. Start server
# 4. Test API with sample request
# 5. Display models and connection info
#
# Usage:
#   bash deploy.sh [PORT]
#
# Environment Variables:
#   PORT      - Server port (default: 8000)
#   REPO_URL  - Repository URL (default: current repo)
################################################################################

set -e  # Exit on error

# Configuration
REPO_URL="${REPO_URL:-https://github.com/Zeeeepa/zai-python-sdk.git}"
REPO_DIR="zai-python-sdk"
DEFAULT_PORT="${PORT:-8000}"
SERVER_SCRIPT="server.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Helper functions
print_banner() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║      Z.AI OpenAI-Compatible API Server - Deployment Script        ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "\n${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Find available port
find_available_port() {
    local port=$1
    while lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; do
        print_warning "Port $port is already in use"
        port=$((port + 1))
    done
    echo $port
}

# Main deployment process
main() {
    print_banner

    # Parse arguments
    PORT="${1:-$DEFAULT_PORT}"

    # Step 1: Check dependencies
    print_step "Checking dependencies..."
    
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_success "Python ${PYTHON_VERSION} found"

    if ! command_exists git; then
        print_error "Git is not installed. Please install git first."
        exit 1
    fi
    print_success "Git found"

    if ! command_exists pip3; then
        print_warning "pip3 not found, attempting to install..."
        python3 -m ensurepip --upgrade || {
            print_error "Failed to install pip. Please install pip3 manually."
            exit 1
        }
    fi
    print_success "pip3 found"

    # Step 2: Clone or update repository
    print_step "Setting up repository..."
    
    if [ -d "$REPO_DIR" ]; then
        print_info "Repository already exists at $REPO_DIR"
        cd "$REPO_DIR"
        
        # Check if it's a git repository
        if [ -d ".git" ]; then
            print_info "Pulling latest changes..."
            git pull || print_warning "Could not pull latest changes"
        else
            print_warning "Directory exists but is not a git repository"
        fi
    else
        print_info "Cloning repository from $REPO_URL"
        git clone "$REPO_URL" "$REPO_DIR" || {
            print_error "Failed to clone repository"
            exit 1
        }
        cd "$REPO_DIR"
        print_success "Repository cloned successfully"
    fi

    # Step 3: Install dependencies
    print_step "Installing dependencies..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv venv || {
            print_error "Failed to create virtual environment"
            exit 1
        }
        print_success "Virtual environment created"
    fi

    # Activate virtual environment
    source venv/bin/activate || {
        print_error "Failed to activate virtual environment"
        exit 1
    }

    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip -q

    # Install required packages
    print_info "Installing required packages..."
    pip install fastapi uvicorn requests pydantic -q || {
        print_error "Failed to install dependencies"
        exit 1
    }
    print_success "All dependencies installed"

    # Step 4: Find available port
    print_step "Checking port availability..."
    ACTUAL_PORT=$(find_available_port $PORT)
    
    if [ "$ACTUAL_PORT" != "$PORT" ]; then
        print_warning "Port $PORT was in use, using port $ACTUAL_PORT instead"
    else
        print_success "Port $PORT is available"
    fi

    # Step 5: Start server in background
    print_step "Starting server on port $ACTUAL_PORT..."
    
    # Kill any existing server process
    pkill -f "$SERVER_SCRIPT" 2>/dev/null || true
    
    # Start server
    python3 "$SERVER_SCRIPT" --port "$ACTUAL_PORT" > server.log 2>&1 &
    SERVER_PID=$!
    
    print_info "Server PID: $SERVER_PID"
    print_info "Log file: $(pwd)/server.log"
    
    # Wait for server to start
    print_info "Waiting for server to initialize..."
    sleep 5

    # Check if server is running
    if ! ps -p $SERVER_PID > /dev/null; then
        print_error "Server failed to start. Check server.log for details:"
        tail -n 20 server.log
        exit 1
    fi
    
    print_success "Server is running!"

    # Step 6: Test API endpoints
    print_step "Testing API endpoints..."
    
    BASE_URL="http://localhost:$ACTUAL_PORT"
    
    # Test health endpoint
    print_info "Testing health endpoint..."
    HEALTH_RESPONSE=$(curl -s "$BASE_URL/health")
    if [ $? -eq 0 ]; then
        print_success "Health check passed"
        echo "$HEALTH_RESPONSE" | python3 -m json.tool
    else
        print_error "Health check failed"
    fi

    echo ""
    
    # Test models endpoint
    print_info "Testing models endpoint..."
    MODELS_RESPONSE=$(curl -s "$BASE_URL/v1/models")
    if [ $? -eq 0 ]; then
        print_success "Models endpoint working"
        echo "$MODELS_RESPONSE" | python3 -m json.tool
    else
        print_error "Models endpoint failed"
    fi

    echo ""

    # Step 7: Test chat completion
    print_step "Testing chat completion..."
    
    print_info "Sending test message: 'What is 2+2?'"
    
    CHAT_RESPONSE=$(curl -s -X POST "$BASE_URL/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d '{
            "model": "glm-4.5v",
            "messages": [
                {"role": "user", "content": "What is 2+2? Answer in one short sentence."}
            ],
            "stream": false
        }')
    
    if [ $? -eq 0 ]; then
        print_success "Chat completion test passed"
        echo "$CHAT_RESPONSE" | python3 -m json.tool
    else
        print_error "Chat completion test failed"
    fi

    # Step 8: Display summary
    echo ""
    print_step "Deployment Summary"
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════════╗"
    echo -e "║                   ✓ Server Successfully Deployed                   ║"
    echo -e "╚════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}📡 Server Information:${NC}"
    echo -e "   • Base URL:    http://localhost:$ACTUAL_PORT"
    echo -e "   • Process ID:  $SERVER_PID"
    echo -e "   • Log File:    $(pwd)/server.log"
    echo ""
    echo -e "${CYAN}📋 Available Endpoints:${NC}"
    echo -e "   • Health:      http://localhost:$ACTUAL_PORT/health"
    echo -e "   • Models:      http://localhost:$ACTUAL_PORT/v1/models"
    echo -e "   • Chat:        http://localhost:$ACTUAL_PORT/v1/chat/completions"
    echo -e "   • API Docs:    http://localhost:$ACTUAL_PORT/docs"
    echo ""
    echo -e "${CYAN}🔧 Management Commands:${NC}"
    echo -e "   • View logs:   tail -f $(pwd)/server.log"
    echo -e "   • Stop server: kill $SERVER_PID"
    echo -e "   • Restart:     bash $0 $ACTUAL_PORT"
    echo ""
    echo -e "${CYAN}💡 Example Usage:${NC}"
    echo ""
    echo -e "${YELLOW}# Non-streaming request${NC}"
    echo -e "curl -X POST http://localhost:$ACTUAL_PORT/v1/chat/completions \\"
    echo -e "  -H 'Content-Type: application/json' \\"
    echo -e "  -d '{"
    echo -e '    "model": "glm-4.5v",'
    echo -e '    "messages": [{"role": "user", "content": "Hello!"}],'
    echo -e '    "stream": false'
    echo -e "  }'"
    echo ""
    echo -e "${YELLOW}# Streaming request${NC}"
    echo -e "curl -X POST http://localhost:$ACTUAL_PORT/v1/chat/completions \\"
    echo -e "  -H 'Content-Type: application/json' \\"
    echo -e "  -d '{"
    echo -e '    "model": "glm-4.5v",'
    echo -e '    "messages": [{"role": "user", "content": "Count to 5"}],'
    echo -e '    "stream": true'
    echo -e "  }'"
    echo ""
    echo -e "${GREEN}✨ Server is now running and ready to accept requests!${NC}"
    echo ""

    # Keep script running to show server status
    print_info "Press Ctrl+C to stop monitoring (server will continue running)"
    echo ""
    
    # Monitor server logs
    tail -f server.log
}

# Trap Ctrl+C to provide cleanup instructions
trap ctrl_c INT
ctrl_c() {
    echo ""
    print_info "Monitoring stopped. Server is still running in the background."
    print_info "To stop the server, run: kill $SERVER_PID"
    echo ""
    exit 0
}

# Run main function
main "$@"

