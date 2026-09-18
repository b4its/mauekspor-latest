#!/bin/bash
# MauEkspor - NGROK MANUAL INSTALL SCRIPT
# Direct download from GitHub mirrors (more reliable)

set -e

echo "=============================================="
echo "🚀 MauEkspor - Ngrok Manual Installer"
echo "=============================================="
echo ""

# Check if ngrok already exists
if command -v ngrok &> /dev/null; then
    echo "✅ ngrok is already installed!"
    echo "   Location: $(which ngrok)"
    echo ""
    exit 0
fi

echo "Starting manual installation..."
echo ""

# Create temp directory
TEMP_DIR=$(mktemp -d)
cd $TEMP_DIR
echo "📁 Working in: $TEMP_DIR"

# Try multiple mirrors in order of reliability
MIRRORS=(
    # Primary: Official S3 bucket
    "https://ngrok-agent.s3.amazonaws.com/ngrok-stable-linux-amd64.zip"
    
    # Secondary: GitHub releases (alternative)
    "https://github.com/grantustin/ngrok/releases/download/v4.2.1/ngrok-v4.2.1-linux-amd64.zip"
    
    # Tertiary: Another GitHub mirror
    "https://github.com/ngetsu/ngrok/archive/refs/tags/v3.2.2.tar.gz"
)

DOWNLOAD_SUCCESS=false

for i in "${!MIRRORS[@]}"; do
    MIRROR=${MIRRORS[$i]}
    echo "Trying mirror $((i+1))/${#MIRRORS[@]}: $MIRROR"
    
    # Try with curl first
    echo "  Using curl..."
    if curl -L --retry 3 --connect-timeout 10 -o ngrok.zip "$MIRROR" 2>/dev/null; then
        FILE_SIZE=$(ls -lh ngrok.zip | awk '{print $5}')
        
        # Verify it's a valid file (should be > 1MB for ngrok)
        if [[ $FILE_SIZE == *"G"* ]] || [[ $FILE_SIZE == *"m"* ]]; then
            echo "  ✅ Large file detected ($FILE_SIZE) - likely valid!"
            DOWNLOAD_SUCCESS=true
            break
        elif [[ ${#FILE_SIZE} -gt 8 ]] && [ "$FILE_SIZE" != "300" ]; then
            echo "  ✅ File size OK ($FILE_SIZE)"
            DOWNLOAD_SUCCESS=true
            break
        fi
        
        rm -f ngrok.zip 2>/dev/null || true
    fi
    
    # Try wget as fallback
    if [ "$DOWNLOAD_SUCCESS" = false ]; then
        echo "  Trying wget..."
        if wget -q --timeout=10 --tries=3 "$MIRROR" -O ngrok.zip 2>/dev/null; then
            FILE_SIZE=$(ls -lh ngrok.zip | awk '{print $5}')
            echo "  ✅ Downloaded: $FILE_SIZE"
            
            if [[ ${#FILE_SIZE} -gt 8 ]]; then
                DOWNLOAD_SUCCESS=true
                break
            fi
            
            rm -f ngrok.zip 2>/dev/null || true
        fi
    fi
    
    echo "  ❌ Failed or invalid size, trying next mirror..."
done

if [ "$DOWNLOAD_SUCCESS" = false ]; then
    echo ""
    echo "❌ All mirrors failed!"
    echo ""
    echo "Please try ONE of these options:"
    echo ""
    echo "Option A - Browser Download (Easiest):"
    echo "  1. Go to: https://ngrok.com/download"
    echo "  2. Click 'Download' for Linux x86-64"
    echo "  3. Unzip and run: sudo mv ngrok /usr/local/bin/"
    echo ""
    echo "Option B - Manual curl command:"
    echo "  curl -LO https://bin.equinox.io/c/bNyj1mQVAI4d/ngrok-stable-linux-amd64.tgz"
    echo "  tar xzf ngrok-stable-linux-amd64.tgz"
    echo "  sudo mv ngrok /usr/local/bin/"
    echo ""
    echo "Option C - Install via apt (Ubuntu/Debian only):"
    echo "  sudo apt install unzip && cd /tmp"
    echo "  curl -L https://bin.equinox.io/c/bNyj1mQVAI4d/ngrok-stable-linux-amd64.tgz -o ngrok.tgz"
    echo "  tar xzf ngrok.tgz && sudo mv ngrok /usr/local/bin/"
    echo ""
    echo "See NGROK_MANUAL_INSTALL.md for more details"
    
    cd ~
    rm -rf $TEMP_DIR
    exit 1
fi

echo ""
echo "📦 Extracting ngrok..."

# Try different extraction methods based on file type
if unzip -l ngrok.zip >/dev/null 2>&1; then
    echo "  It's a zip file..."
    UNZIP_OUTPUT=$(unzip -o ngrok.zip 2>&1)
    
    if echo "$UNZIP_OUTPUT" | grep -q "extracting: ngrok"; then
        EXTRACTED="ngrok"
    else
        EXTRACTED=$(echo "$UNZIP_OUTPUT" | grep "^  " | head -1 | sed 's/^  //' | cut -d'/' -f1)
        EXTRACTED="$EXTRACTED/ngrok"
    fi
elif tar tzf ngrok.zip >/dev/null 2>&1; then
    echo "  It's a tar.gz file..."
    tar xzf ngrok.zip -C . 2>/dev/null || true
    EXTRACTED=$(find . -maxdepth 1 -name "ngrok" -type f 2>/dev/null | head -1)
else
    # Try extracting anyway
    unzip -o ngrok.zip 2>/dev/null || tar xzf ngrok.zip 2>/dev/null || true
    EXTRACTED=$(find . -maxdepth 1 -name "ngrok" -executable 2>/dev/null | head -1)
fi

if [ -z "$EXTRACTED" ] || [ ! -f "$EXTRACTED" ]; then
    # Last resort: search for any executable named ngrok
    EXTRACTED=$(find . -maxdepth 2 -type f -executable 2>/dev/null | grep -i ngrok | head -1)
fi

if [ -z "$EXTRACTED" ]; then
    echo ""
    echo "❌ Could not extract ngrok binary"
    echo "Contents of archive:"
    ls -la
    
    cd ~
    rm -rf $TEMP_DIR
    exit 1
fi

echo "✅ Found ngrok at: $EXTRACTED"
echo ""
echo "🔧 Installing ngrok..."

# Move to system PATH if possible
if [ -w /usr/local/bin ]; then
    echo "   Moving to: /usr/local/bin/ngrok"
    sudo cp "$EXTRACTED" /usr/local/bin/ngrok
    sudo chmod +x /usr/local/bin/ngrok
else
    echo "   No sudo access, moving to: ~/bin/ngrok"
    mkdir -p ~/bin
    cp "$EXTRACTED" ~/bin/ngrok
    chmod +x ~/bin/ngrok
    
    # Add to PATH if needed
    if ! grep -q 'export PATH="\$HOME/bin:\$PATH"' ~/.bashrc 2>/dev/null; then
        echo '' >> ~/.bashrc
        echo '# Ngrok installation' >> ~/.bashrc
        echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
        echo ""
        echo "⚠️  Added to ~/.bashrc"
        echo "   Run: source ~/.bashrc"
    fi
fi

# Verify installation
echo ""
echo "🔍 Verifying..."
sleep 1

if command -v ngrok &> /dev/null; then
    LOCATION=$(which ngrok)
    VERSION_OUTPUT=$(ngrok version 2>&1)
    VERSION_LINE=$(echo "$VERSION_OUTPUT" | head -1)
    
    echo "=============================================="
    echo "✅ Installation SUCCESSFUL!"
    echo "=============================================="
    echo ""
    echo "Details:"
    echo "  Binary: $LOCATION"
    echo "  Version: $VERSION_LINE"
    echo ""
    echo "Now you can use Makefile commands:"
    echo "  make ngrok-prod     # Production deployment"
    echo "  make ngrok-local    # Local development"
    echo ""
    echo "Your ngrok token is configured:"
    echo "  3IGWSdWwxcOQkQcxP0BcRkfHa5m_3nMcbXKdN93eUqsM1Hxjf"
    echo ""
    echo "Next steps:"
    echo "  1. Start your app: cd ~/programming/python/mauekspor && make local"
    echo "  2. Open new terminal and run:"
    echo "     cd ~/programming/python/mauekspor && make ngrok-prod"
    echo "  3. You'll get PUBLIC URLs to share!"
    echo ""
    echo "=============================================="
    
    # Cleanup
    cd ~
    rm -rf $TEMP_DIR
    exit 0
else
    echo "❌ Verification failed - ngrok not found in PATH"
    echo "Please check: which ngrok"
    
    cd ~
    rm -rf $TEMP_DIR
    exit 1
fi
