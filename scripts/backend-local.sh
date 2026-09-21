#!/bin/bash
# Start backend locally with AI access
# Use this instead of Docker when you need AI features

set -e

echo "🚀 Starting MauEkspor Backend (Local Mode with AI Access)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if AI service is running
if curl -s http://localhost:20128/v1/models --max-time 2 > /dev/null; then
    echo "✅ AI service detected at http://localhost:20128"
else
    echo "⚠️  AI service not running at http://localhost:20128"
    echo "   AI features will fall back to mock responses"
fi

# Check if PostgreSQL is running in Docker
if docker ps | grep -q mauekspor-db-prod; then
    echo "✅ PostgreSQL running in Docker (port 5447)"
    export MAUEKSPOR_DATABASE_URL="postgresql://mauekspor:mauekspor@localhost:5447/mauekspor"
else
    echo "⚠️  PostgreSQL not running, using SQLite fallback"
    export MAUEKSPOR_DATABASE_URL="sqlite:///./mauekspor.db"
fi

# Load environment
set -a
source /home/vxm/programming/mauekspor/.env
set +a

# Override AI settings for local access
export MAUEKSPOR_AI_MODE=remote
export MAUEKSPOR_AI_BASE_URL="http://localhost:20128/v1"
export MAUEKSPOR_AI_API_KEY="sk-dede08aea594e222-upk4p8-5bfa2c54"
export MAUEKSPOR_AI_MODEL="qd/dmodel"

# Set backend port
export MAUEKSPOR_BACKEND_PORT=8016

echo ""
echo "Configuration:"
echo "  Database: ${MAUEKSPOR_DATABASE_URL}"
echo "  AI Mode: ${MAUEKSPOR_AI_MODE}"
echo "  AI Endpoint: ${MAUEKSPOR_AI_BASE_URL}"
echo "  Backend Port: ${MAUEKSPOR_BACKEND_PORT}"
echo ""
echo "Starting server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd /home/vxm/programming/mauekspor/backend

# Kill any existing uvicorn on port 8016
pkill -f "uvicorn.*8016" 2>/dev/null || true
sleep 1

# Start uvicorn
exec .venv/bin/uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8016 \
    --reload \
    --log-level info
