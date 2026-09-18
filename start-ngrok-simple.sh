#!/bin/bash
# MauEkspor Ngrok Simple Tunnel Script
# Uses ngrok binary directly if available

NGROK_TOKEN="3IGWSdWwxcOQkQcxP0BcRkfHa5m_3nMcbXKdN93eUqsM1Hxjf"

echo "=============================================="
echo "🌍 MauEkspor - Simple Ngrok Tunnels"
echo "=============================================="
echo ""

# Services and ports
SERVICES=(
    "Backend API:8016"
    "Frontend Dev:5189"
    "Frontend Prod:3016"
)

TUNNEL_PIDS=()

cleanup() {
    echo ""
    echo "👋 Stopping all tunnels..."
    for pid in "${TUNNEL_PIDS[@]}"; do
        kill $pid 2>/dev/null || true
    done
    exit 0
}

trap cleanup SIGINT SIGTERM

# Check if ngrok exists
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok not found!"
    echo ""
    echo "Please install ngrok first:"
    echo "  1. Download from: https://ngrok.com/download"
    echo "  2. Or use: wget https://bin.equinox.io/c/bNyj1mQVAI4d/ngrok-stable-linux-amd64.tgz"
    echo "  3. Extract and add to PATH"
    echo ""
    echo "Alternative: Use pip package"
    echo "  pip3 install --break-system-packages pyngrok"
    exit 1
fi

echo "✅ ngrok found at: $(which ngrok)"
echo ""
echo "Starting tunnels for:"
for service_port in "${SERVICES[@]}"; do
    SERVICE=$(echo "$service_port" | cut -d: -f1)
    PORT=$(echo "$service_port" | cut -d: -f2)
    echo "  • $SERVICE on port $PORT"
done
echo ""
echo "Press Ctrl+C to stop all tunnels"
echo "=============================================="
echo ""

# Start each tunnel in background
for service_port in "${SERVICES[@]}"; do
    SERVICE=$(echo "$service_port" | cut -d: -f1)
    PORT=$(echo "$service_port" | cut -d: -f2)
    
    echo "🚀 Starting ngrok for $SERVICE (port $PORT)..."
    
    # Start ngrok tunnel
    ngrok http $PORT --log stdout --authtoken $NGROK_TOKEN > /tmp/ngrok-${PORT}.log 2>&1 &
    PID=$!
    TUNNEL_PIDS+=($PID)
    
    echo "   Process ID: $PID"
    echo "   Log: /tmp/ngrok-${PORT}.log"
    echo ""
    
    sleep 1
done

echo "=============================================="
echo "✅ All tunnels started!"
echo ""
echo "Logs saved to:"
for service_port in "${SERVICES[@]}"; do
    PORT=$(echo "$service_port" | cut -d: -f2)
    echo "  /tmp/ngrok-${PORT}.log"
done
echo ""
echo "To view public URLs:"
echo "  cat /tmp/ngrok-8016.log | grep 'forwarding'"
echo "  cat /tmp/ngrok-5189.log | grep 'forwarding'"  
echo "  cat /tmp/ngrok-3016.log | grep 'forwarding'"
echo ""
echo "Waiting for connections..."

# Wait for processes
wait
