#!/bin/bash
# Simple local starter - runs backend & frontend directly with real AI

set -e

echo "╔══════════════════════════════════════════════╗"
echo "║  🚀 MauEkspor Local Development Starter    ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

BACKEND_PORT=8016
FRONTEND_PORT=5188
DB_PORT=5447

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v uvicorn &> /dev/null; then
    echo "⚠️  Installing uvicorn..."
    pip install uvicorn fastapi python-multipart pydantic python-jose[ cryptography] passlib bcrypt httpx
fi

if [ ! -f .env.local ]; then
    cp .env.local.example .env.local 2>/dev/null || true
    if [ ! -f .env.local ]; then
        echo "# Creating .env.local..."
        cat > .env.local << 'EOF'
MAUEKSPOR_SECRET_KEY=dev-secret-key
MAUEKSPOR_AI_MODE=remote
MAUEKSPOR_AI_BASE_URL=http://localhost:20128/v1
MAUEKSPOR_AI_API_KEY=sk-dede08aea594e222-upk4p8-5bfa2c54
MAUEKSPOR_AI_MODEL=qd/dmodel
EOF
    fi
fi

source .env.local

echo ""
echo "🗄️  Database should be running at localhost:$DB_PORT"
echo ""
echo "🤖 Testing AI connectivity..."
if curl -s http://localhost:20128/v1/models > /dev/null 2>&1; then
    echo "✅ AI service accessible at localhost:20128"
else
    echo "⚠️  AI not accessible at localhost:20128"
    echo "   Backend will use mock responses"
    export MAUEKSPOR_AI_MODE=mock
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Starting Application"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start backend in background
echo "🔧 Starting backend on port $BACKEND_PORT..."
cd backend
uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "Waiting for backend to initialize..."
for i in {1..30}; do
    if curl -s http://localhost:$BACKEND_PORT/api/v1/health > /dev/null 2>&1; then
        echo "✅ Backend started!"
        break
    fi
    sleep 1
done

# Start frontend
echo ""
echo "🎨 Starting frontend on port $FRONTEND_PORT..."
cd frontend
pnpm dev --host 0.0.0.0 --port $FRONTEND_PORT &
FRONTEND_PID=$!

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ APPLICATION RUNNING!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Frontend: http://localhost:$FRONTEND_PORT"
echo "  Backend:  http://localhost:$BACKEND_PORT/api/v1"
echo "  Login:    admin@mauekspor.example / admin123"
echo ""
echo "  To stop: press Ctrl+C or run 'make dev-down'"
echo "  Backend PID: $BACKEND_PID"
echo "  Frontend PID: $FRONTEND_PID"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Keep running
wait
