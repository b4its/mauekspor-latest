#!/bin/bash
# MauEkspor - Auto fix firewall for local development
# Checks if UFW is active and adds necessary rules
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔥 Checking firewall..."

# Check if ufw exists
if ! command -v ufw &> /dev/null; then
    echo -e "${GREEN}[✓]${NC} No UFW found - skipping"
    exit 0
fi

# Check if ufw is enabled
if grep -q "ENABLED=yes" /etc/ufw/ufw.conf 2>/dev/null; then
    echo -e "${YELLOW}[!]${NC} UFW firewall is ACTIVE"
    
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        echo ""
        echo "⚠️  Firewall is blocking LAN access!"
        echo "   Run these commands to allow access:"
        echo ""
        echo "   sudo ufw allow 8016/tcp    # Backend API"
        echo "   sudo ufw allow 5188/tcp    # Frontend"
        echo ""
        echo "   Or disable firewall for dev:"
        echo "   sudo ufw disable"
        echo ""
        exit 0
    fi
    
    # If root, add rules
    echo -e "${GREEN}[→]${NC} Adding firewall rules..."
    ufw allow 8016/tcp 2>/dev/null || true
    ufw allow 5188/tcp 2>/dev/null || true
    echo -e "${GREEN}[✓]${NC} Firewall rules added"
else
    echo -e "${GREEN}[✓]${NC} UFW is not enabled - OK"
fi
