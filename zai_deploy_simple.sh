#!/usr/bin/env bash
#
# ZAI Python SDK - Single Executable Deployment Script
# EXANOKE FORMAT v1.0
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/Zeeeepa/zai-python-sdk/main/zai_deploy_simple.sh -o zai_deploy.sh
#   bash zai_deploy.sh [branch_name]
#
# Example:
#   bash zai_deploy.sh codegen-bot/openai-compat-api-1759886538
#   bash zai_deploy.sh main
#

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

REPO_URL="https://github.com/Zeeeepa/zai-python-sdk.git"
DEFAULT_BRANCH="main"
INSTALL_DIR="/opt/zai-python-sdk"
SERVICE_NAME="zai-python-sdk"
LOG_FILE="/var/log/${SERVICE_NAME}.log"
PID_FILE="/var/run/${SERVICE_NAME}.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Helper Functions
# ============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        return 1
    fi
    return 0
}

install_system_dependencies() {
    log_info "Installing system dependencies..."
    
    if command -v apt-get &> /dev/null; then
        sudo apt-get update -qq
        sudo apt-get install -y -qq git python3 python3-pip python3-venv curl wget > /dev/null 2>&1
    elif command -v yum &> /dev/null; then
        sudo yum install -y -q git python3 python3-pip curl wget > /dev/null 2>&1
    elif command -v brew &> /dev/null; then
        brew install git python3 curl wget > /dev/null 2>&1
    else
        log_error "Unsupported package manager. Please install git, python3, and pip manually."
        exit 1
    fi
    
    log_success "System dependencies installed"
}

clone_repository() {
    local branch="${1:-$DEFAULT_BRANCH}"
    
    log_info "Cloning repository (branch: $branch)..."
    
    # Remove existing installation if present
    if [ -d "$INSTALL_DIR" ]; then
        log_warning "Existing installation found at $INSTALL_DIR"
        read -p "Remove and reinstall? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo rm -rf "$INSTALL_DIR"
        else
            log_info "Using existing installation"
            cd "$INSTALL_DIR"
            git fetch origin
            git checkout "$branch"
            git pull origin "$branch"
            return 0
        fi
    fi
    
    # Clone repository
    sudo mkdir -p "$INSTALL_DIR"
    sudo chown -R "$USER:$USER" "$INSTALL_DIR"
    
    git clone --depth 1 --branch "$branch" "$REPO_URL" "$INSTALL_DIR" 2>/dev/null || {
        log_error "Failed to clone branch '$branch'. Trying default branch..."
        git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
        cd "$INSTALL_DIR"
        if [ "$branch" != "$DEFAULT_BRANCH" ]; then
            git fetch origin "$branch" --depth 1
            git checkout "$branch"
        fi
    }
    
    log_success "Repository cloned successfully"
}

setup_python_environment() {
    log_info "Setting up Python environment..."
    
    cd "$INSTALL_DIR"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip > /dev/null 2>&1
    
    # Install dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt > /dev/null 2>&1
    fi
    
    if [ -f "pyproject.toml" ]; then
        pip install -e . > /dev/null 2>&1
    fi
    
    log_success "Python environment configured"
}

create_systemd_service() {
    log_info "Creating systemd service..."
    
    local service_file="/etc/systemd/system/${SERVICE_NAME}.service"
    
    sudo tee "$service_file" > /dev/null <<EOF
[Unit]
Description=ZAI Python SDK Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$INSTALL_DIR/venv/bin/python3 -m zai.example
Restart=always
RestartSec=10
StandardOutput=append:$LOG_FILE
StandardError=append:$LOG_FILE

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    log_success "Systemd service created"
}

start_service() {
    log_info "Starting service..."
    
    # Check if systemd is available
    if command -v systemctl &> /dev/null; then
        sudo systemctl enable "$SERVICE_NAME"
        sudo systemctl start "$SERVICE_NAME"
        sleep 2
        
        if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
            log_success "Service started successfully"
            sudo systemctl status "$SERVICE_NAME" --no-pager
        else
            log_error "Service failed to start"
            sudo journalctl -u "$SERVICE_NAME" --no-pager -n 20
            exit 1
        fi
    else
        log_warning "Systemd not available. Starting service in background..."
        
        cd "$INSTALL_DIR"
        source venv/bin/activate
        
        nohup python3 -m zai.example > "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
        
        log_success "Service started with PID $(cat $PID_FILE)"
        log_info "Logs: $LOG_FILE"
    fi
}

run_tests() {
    log_info "Running installation tests..."
    
    cd "$INSTALL_DIR"
    source venv/bin/activate
    
    if [ -f "test_installation.py" ]; then
        python3 test_installation.py || {
            log_warning "Some tests failed, but installation may still work"
        }
    fi
    
    log_success "Tests completed"
}

print_usage() {
    log_info "==================================================="
    log_info "ZAI Python SDK - Successfully Deployed!"
    log_info "==================================================="
    echo ""
    log_info "Installation Directory: $INSTALL_DIR"
    log_info "Log File: $LOG_FILE"
    echo ""
    log_info "Quick Start:"
    echo ""
    echo "  # Activate virtual environment"
    echo "  source $INSTALL_DIR/venv/bin/activate"
    echo ""
    echo "  # Run example"
    echo "  python3 -m zai.example"
    echo ""
    echo "  # Or use in your code"
    echo "  from zai.client import ZAIClient"
    echo "  client = ZAIClient()"
    echo "  response = client.chat('Hello!')"
    echo ""
    log_info "Service Management:"
    echo ""
    echo "  sudo systemctl status $SERVICE_NAME"
    echo "  sudo systemctl stop $SERVICE_NAME"
    echo "  sudo systemctl restart $SERVICE_NAME"
    echo "  sudo journalctl -u $SERVICE_NAME -f"
    echo ""
    log_info "==================================================="
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    local branch="${1:-$DEFAULT_BRANCH}"
    
    echo ""
    log_info "==================================================="
    log_info "ZAI Python SDK - Single Executable Deployment"
    log_info "EXANOKE FORMAT v1.0"
    log_info "==================================================="
    echo ""
    
    log_info "Deployment Configuration:"
    log_info "  Repository: $REPO_URL"
    log_info "  Branch: $branch"
    log_info "  Install Directory: $INSTALL_DIR"
    echo ""
    
    # Check for sudo access
    if ! sudo -v; then
        log_error "This script requires sudo access"
        exit 1
    fi
    
    # Step 1: Install system dependencies
    if ! check_command git || ! check_command python3; then
        install_system_dependencies
    else
        log_success "System dependencies already installed"
    fi
    
    # Step 2: Clone repository
    clone_repository "$branch"
    
    # Step 3: Setup Python environment
    setup_python_environment
    
    # Step 4: Run tests
    run_tests
    
    # Step 5: Create and start service
    create_systemd_service
    start_service
    
    # Step 6: Print usage information
    echo ""
    print_usage
    
    log_success "Deployment completed successfully! 🚀"
}

# Run main function with all arguments
main "$@"

