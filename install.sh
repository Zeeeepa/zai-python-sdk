#!/bin/bash
# Z.AI OpenAI-Compatible API - One-Click Installer
# Usage: curl -fsSL <raw-github-url>/install.sh | bash
# Or: curl -fsSL <raw-github-url>/install.sh -o install.sh && bash install.sh [branch-name]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo "============================================================"
echo -e "${CYAN}🚀 Z.AI OpenAI-Compatible API - Installer${NC}"
echo "============================================================"
echo ""

# Determine branch
BRANCH="${1:-main}"
REPO="Zeeeepa/zai-python-sdk"

echo -e "${BLUE}📥 Downloading from branch: ${BRANCH}${NC}"
echo ""

# Download setup script
DOWNLOAD_URL="https://raw.githubusercontent.com/${REPO}/${BRANCH}/setup_and_deploy.sh"

echo -e "${CYAN}Downloading setup_and_deploy.sh...${NC}"
curl -fsSL "$DOWNLOAD_URL" -o setup_and_deploy.sh

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to download setup script${NC}"
    echo "URL: $DOWNLOAD_URL"
    exit 1
fi

chmod +x setup_and_deploy.sh
echo -e "${GREEN}✅ Downloaded successfully${NC}"
echo ""

# Run setup
echo -e "${CYAN}Starting setup...${NC}"
echo ""
bash setup_and_deploy.sh

