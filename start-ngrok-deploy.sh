#!/bin/bash
# MauEkspor - Ngrok Deployment Script
# One-click deploy AFTER installing ngrok manually

set -e

echo "=============================================="
echo "🚀 MauEkspor Ngrok Deployment"
echo "=============================================="
echo ""

# Verify ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ERROR: ngrok not found!"
    echo ""
    echo "Please install ngrok first:"
    echo ""
    echo "1. Go to: https://ngrok.com/download"
    echo "2. Download Linux x86-64 version"
    echo "3. Extract and run:"
    echo "   cd ~/Downloads"
    echo "   unzip ngrok*.zip"
    echo "   sudo mv ngrok /usr/local/bin/"
    echo ""
    echo "Then come back and run this script."
    echo ""
    exit 1
fi

echo "✅ ngrok detected at: $(which ngrok)"
NGROK_VERSION=$(ngrok version | head -1)
echo "   Version: $NGROK_VERSION"
echo ""

# Ask user which mode they want
echo "Choose deployment mode:"
echo ""
echo "  1) Production (Docker containers)"
echo "  2) Local Development (uvicorn + pnpm)"
echo "  3) Both (run local services first, then tunnel)"
echo ""
read -p "Enter choice [1-3]: " MODE_CHOICE

case $MODE_CHOICE in
    1)
        MODE="production"
        ;;
    2)
        MODE="local"
        ;;
    *)
        MODE="both"
        ;;
esac

echo ""
echo "Starting deployment..."
echo ""

# Initialize arrays for tunnels
declare -A TUNNELS

# Function to start single tunnel
start_tunnel() {
    local SERVICE=$1
    local PORT=$2
    
    echo "🚀 Starting tunnel for $SERVICE on port $PORT..."
    
    # Start ngrok in background
    ngrok http $PORT \
        --authtoken 3IGWSdWwxcOQkQcxP0BcRkfHa5m_3nMcbXKdN93eUqsM1Hxjf \
        --log stdout &
    
    PID=$!
    TUNNEL_PIDS+=($PID)
    
    # Wait a moment for URL generation
    sleep 2
    
    echo "   Process ID: $PID"
}

# Track which ports to tunnel
PORTS_TO_TUNNEL=()
SERVICES_INFO=()

case $MODE in
    production)
        SERVICES_INFO=("Backend API:8015" "Frontend Dev:5188" "Frontend Prod:3015")
        PORTS_TO_TUNNEL=(8015 5188 3015)
        ;;
    local)
        SERVICES_INFO=("Backend API:8016" "Frontend Dev:5188")
        PORTS_TO_TUNNEL=(8016 5188)
        ;;
    both)
        SERVICES_INFO=("Backend API:8016" "Frontend Dev:5188" "Frontend Prod:3015")
        PORTS_TO_TUNNEL=(8016 5188 3015)
        ;;
esac

# Start services based on mode
case $MODE in
    production)
        echo "🐳 Starting Docker containers..."
        docker compose -f docker-compose.prod.yml --profile production up -d
        sleep 3
        
        echo "Checking if services are running..."
        sleep 2
        
        # Verify ports are listening
        for port in "${PORTS_TO_TUNNEL[@]}"; do
            if lsof -i :$port > /dev/null 2>&1; then
                echo "   ✅ Port $port is ready"
            else
                echo "   ⚠️  Port $port may not be responding yet"
            fi
        done
        ;;
    local|both)
        echo "🚦 Starting local services..."
        
        # Start backend
        echo "  Backend API..."
        cd backend
        if [ -d ".venv" ]; then
            source .venv/bin/activate
            uvicorn app.main:app --host 0.0.0.0 --port 8016 &
            BACKEND_PID=$!
        else
            echo "   Creating virtual environment..."
            python3 -m venv .venv
            .venv/bin/pip install -q -r requirements.txt
            source .venv/bin/activate
            uvicorn app.main:app --host 0.0.0.0 --port 8016 &
            BACKEND_PID=$!
        fi
        cd ..
        sleep 2
        
        # Start frontend dev
        echo "  Frontend Dev Server..."
        cd frontend
        if [ ! -d "node_modules" ]; then
            pnpm install
        fi
        pnpm run dev --host 0.0.0.0 --port 5188 &
        FRONTEND_PID=$!
        cd ..
        sleep 2
        
        echo "   ✅ Local services started"
        ;;
esac

echo ""
echo "🌐 Starting ngrok tunnels..."
echo ""

# Array to store tunnel PIDs
TUNNEL_PIDS=()

# Start all tunnels
for i in "${!SERVICES_INFO[@]}"; do
    INFO="${SERVICES_INFO[$i]}"
    SERVICE_NAME="${INFO%%:*}"
    PORT="${INFO##*:}"
    
    start_tunnel "$SERVICE_NAME" "$PORT"
done

# Give time for tunnels to establish
sleep 3

echo ""
echo "=============================================="
echo "📋 Public URLs Generated:"
echo "=============================================="
echo ""

# Display public URLs by checking logs
for i in "${!SERVICES_INFO[@]}"; do
    SERVICE_NAME="${SERVICES_INFO[$i]%"*"}"
    PORT="${SERVICES_INFO[$i]}"${SERVICE_NAME#"*"}}
    
    # Wait for URL output from ngrok
    sleep 1
done

echo "Your ngrok tunnels are running!"
echo ""
echo "To see your PUBLIC URLs, check these files:"
for port in "${PORTS_TO_TUNNEL[@]}"; do
    echo "  /tmp/ngrok-${port}.log (look for 'forwarding')"
done

echo ""
echo "Alternative: Check running tunnels directly:"
curl -s http://localhost:4040/api/tunnels 2>/dev/null || echo "(ngrok web interface may not be available)"

echo ""
echo "=============================================="
echo "⚡ Quick Commands:"
echo "=============================================="
echo ""
echo "View all running tunnels:"
echo "  curl http://localhost:4040/api/tunnels"
echo ""
echo "Stop all tunnels:"
echo "  make ngrok-stop"
echo ""
echo "Restart everything:"
echo "  bash start-ngrok-tunnels.sh"
echo ""

# Keep script running
echo "👉 Press Ctrl+C when you're done"
echo ""

# Set up trap for cleanup
cleanup() {
    echo ""
    echo "=============================================="
    echo "👋 Shutting down all services..."
    echo "=============================================="
    
    # Stop all tunnels
    echo "Stopping tunnels..."
    for pid in "${TUNNEL_PIDS[@]}"; do
        kill $pid 2>/dev/null || true
    done
    wait 2>/dev/null || true
    
    # Stop local services if running
    if [ "$MODE" != "production" ]; then
        echo "Stopping local services..."
        kill $BACKEND_PID 2>/dev/null || true
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    echo "All services stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for processes
wait
