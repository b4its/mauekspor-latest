#!/bin/bash
# MauEkspor - Frontend Dependencies Install Script
# Handles network issues and slow downloads

set -e

echo "=============================================="
echo "🚀 MauEkspor - Frontend Dependencies"
echo "=============================================="
echo ""

cd frontend

# Check if node_modules already exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies from scratch..."
else
    echo "⚠️  node_modules found. Reinstalling to ensure consistency..."
    rm -rf node_modules
fi

# Configure pnpm for better network handling
echo ""
echo "⚙️ Configuring pnpm with extended timeouts..."
pnpm config set network-timeout 300000
pnpm config set fetch-retries 5
pnpm config set fetchRetryMaxTimeout 120000
pnpm config set fetchRetryInterval 20000

# Try frozen lockfile first (fastest)
echo ""
echo "🔒 Attempt 1: Installing with frozen lockfile..."
if pnpm install --frozen-lockfile 2>&1 | tee /tmp/pnpm-install-1.log; then
    echo ""
    echo "✅ Installation successful with frozen lockfile!"
    exit 0
fi

echo ""
echo "❌ Frozen lockfile failed, trying without freeze..."

# If frozen fails, try regular install
echo ""
echo "📥 Attempt 2: Installing without frozen lockfile..."
if pnpm install --no-frozen-lockfile 2>&1 | tee /tmp/pnpm-install-2.log; then
    echo ""
    echo "✅ Installation successful!"
    
    # Update lockfile
    echo ""
    echo "💾 Updating lockfile..."
    pnpm install --lockfile-only
    
    echo ""
    echo "✅ Lockfile updated successfully!"
    exit 0
fi

echo ""
echo "❌ Regular install also failed."
echo ""
echo "Troubleshooting steps:"
echo ""
echo "1. Check your internet connection:"
echo "   ping -c 3 registry.npmjs.org"
echo ""
echo "2. Try using npm registry mirror:"
echo "   pnpm config set registry https://registry.npmmirror.com"
echo ""
echo "3. Clear pnpm cache:"
echo "   pnpm store prune"
echo ""
echo "4. Check available disk space:"
echo "   df -h"
echo ""
echo "5. Try installing system packages that might be missing:"
echo "   sudo apt-get update && sudo apt-get install -y curl wget unzip"
echo ""
exit 1
