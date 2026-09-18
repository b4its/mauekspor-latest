#!/bin/bash
# MauEkspor - Auto Install Ngrok Script
# Download and install ngrok automatically

set -e

echo "=============================================="
echo "🚀 MauEkspor - Ngrok Auto-Installer"
echo "=============================================="
echo ""

# Check if ngrok already exists
if command -v ngrok &> /dev/null; then
    echo "✅ ngrok is already installed!"
    echo "   Location: $(which ngrok)"
    echo ""
    exit 0
fi

echo "❌ ngrok not found in PATH"
echo ""
echo "Starting installation..."
echo ""

# Step 1: Create temp directory
TEMP_DIR=$(mktemp -d)
echo "📁 Creating temp directory: $TEMP_DIR"

# Step 2: Try multiple download methods
echo ""
echo "⏳ Downloading ngrok..."
cd $TEMP_DIR

DOWNLOAD_URL="https://ngrok-agent.s3.amazonaws.com/ngrok.zip"

# Method 1: Try curl first
echo "Method 1: Using curl..."
if curl -L --retry 3 -o ngrok.zip "$DOWNLOAD_URL" 2>/dev/null; then
    FILE_SIZE=$(ls -lh ngrok.zip | awk '{print $5}')
    echo "✅ Downloaded successfully (curl): $FILE_SIZE"
elif wget -q --retry-connrefused --waitretry=2 $DOWNLOAD_URL -O ngrok.zip; then
    FILE_SIZE=$(ls -lh ngrok.zip | awk '{print $5}')
    echo "✅ Downloaded successfully (wget): $FILE_SIZE"
else
    echo "❌ Failed to download from S3"
    echo "Trying alternative method..."
    
    # Try GitHub releases
    GH_URL="https://github.com/grantustin/ngrok/releases/download/v4.2.1/ngrok-v4.2.1-linux-amd64.zip"
    if curl -L --retry 3 -o ngrok.zip "$GH_URL" 2>/dev/null || \
       wget -q --retry-connrefused --waitretry=2 $GH_URL -O ngrok.zip; then
        FILE_SIZE=$(ls -lh ngrok.zip | awk '{print $5}')
        echo "✅ Downloaded successfully (GitHub mirror): $FILE_SIZE"
    else
        echo "❌ All download attempts failed"
        echo ""
        echo "Please try manual installation:"
        echo "1. Go to: https://ngrok.com/download"
        echo "2. Download for Linux"
        echo "3. Follow instructions in NGROK_INSTALL_GUIDE.md"
        rm -rf $TEMP_DIR
        exit 1
    fi
fi

# Step 3: Extract (try zip since it's .zip now)
echo ""
echo "📦 Extracting..."
if unzip -q ngrok.zip; then
    echo "✅ Extracted zip successfully"
    EXTRACTED_FILE="ngrok"
elif tar xzf ngrok.zip 2>/dev/null; then
    echo "✅ Extracted tar.gz successfully"
    EXTRACTED_FILE="ngrok"
else
    echo "⚠️  Could not extract, looking for ngrok binary in archive..."
    UNZIP_DIR=$(unzip -l ngrok.zip | grep ngrok$ | head -1 | awk '{print $NF}' | cut -d'/' -f1)
    if [ -n "$UNZIP_DIR" ]; then
        unzip -o "$UNZIP_DIR/ngrok" . 2>/dev/null || true
        EXTRACTED_FILE="$UNZIP_DIR/ngrok"
    else
        echo "❌ Failed to extract"
        rm -rf $TEMP_DIR
        exit 1
    fi
fi

# Find ngrok binary
NGROK_BINARY=""
for f in ngrok $EXTRACTED_FILE; do
    if [ -f "$f" ] && file "$f" | grep -q "executable"; then
        NGROK_BINARY="$f"
        break
    fi
done

if [ -z "$NGROK_BINARY" ]; then
    # Search recursively
    NGROK_BINARY=$(find . -maxdepth 1 -name "ngrok" -type f 2>/dev/null | head -1)
fi

if [ -z "$NGROK_BINARY" ]; then
    echo "❌ Could not find ngrok binary after extraction"
    rm -rf $TEMP_DIR
    exit 1
fi

echo "✅ Found ngrok binary at: $NGROK_BINARY"

# Step 4: Move to PATH
echo ""
echo "🔧 Installing ngrok..."

# Check if we can write to /usr/local/bin
if [ -w /usr/local/bin ]; then
    echo "   Destination: /usr/local/bin/ngrok"
    sudo mv "$NGROK_BINARY" /usr/local/bin/ngrok
    sudo chmod +x /usr/local/bin/ngrok
else
    echo "   No sudo access, installing to ~/bin/ngrok"
    mkdir -p ~/bin
    cp "$NGROK_BINARY" ~/bin/ngrok
    chmod +x ~/bin/ngrok
    
    # Add to .bashrc if not already there
    if ! grep -q 'export PATH="$HOME/bin:\$PATH"' ~/.bashrc 2>/dev/null; then
        echo '' >> ~/.bashrc
        echo '# Ngrok installation' >> ~/.bashrc
        echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
        echo ""
        echo "⚠️  Added to ~/.bashrc"
        echo "   Run: source ~/.bashrc"
        echo "   Or close and reopen terminal"
    fi
fi

# Verify installation
echo ""
echo "🔍 Verifying installation..."
sleep 1

if command -v ngrok &> /dev/null; then
    VERSION_OUTPUT=$(ngrok version 2>&1)
    VERSION_LINE=$(echo "$VERSION_OUTPUT" | head -1)
    LOCATION=$(which ngrok)
    
    echo "=============================================="
    echo "✅ Installation Successful!"
    echo "=============================================="
    echo ""
    echo "Ngrok details:"
    echo "  Version: $VERSION_LINE"
    echo "  Location: $LOCATION"
    echo ""
    echo "Now you can use Makefile commands:"
    echo ""
    echo "  make ngrok-prod     # Production mode with ngrok"
    echo "  make ngrok-local    # Local development with ngrok"
    echo ""
    echo "To start deployment:"
    echo "  cd ~/programming/python/mauekspor"
    echo "  bash install-ngrok.sh && make ngrok-prod"
    echo ""
    echo "Your ngrok auth token is already configured:"
    echo "  3IGWSdWwxcOQkQcxP0BcRkfHa5m_3nMcbXKdN93eUqsM1Hxjf"
    echo ""
    
    # Cleanup
    rm -rf $TEMP_DIR
    echo "=============================================="
else
    echo "❌ Installation verification failed"
    echo "ngrok still not in PATH"
    rm -rf $TEMP_DIR
    exit 1
fi
