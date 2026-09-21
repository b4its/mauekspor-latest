#!/bin/bash
# Start production stack with AI service exposed via ngrok

set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "═══════════════════════════════════════════════════════════"
echo "  🌐 MauEkspor + AI Service (Ngrok Tunnel)"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "  Starting:"
echo "    1. Production backend & frontend (Docker)"
echo "    2. AI service reverse proxy to ngrok"
echo "    3. Connect everything together"
echo ""

NGROK_TOKEN="${NGROK_TOKEN:?NGROK_TOKEN not set — check .env}"
AI_PORT="${AI_PORT:-20128}"
BACKEND_PORT="${BACKEND_PORT:-8015}"
FRONTEND_PORT="${FRONTEND_PORT:-3015}"
NGINX_PORT="${NGINX_PORT:-8080}"

# Check if services are already running
if docker ps --format '{{.Names}}' | grep -q "mauekspor-backend-prod"; then
    echo "⚠️  Backend already running, stopping first..."
    make ngrok-prod-down 2>/dev/null || true
    sleep 2
fi

# Ensure AI port is free
pkill -f "ngrok http ${AI_PORT}" 2>/dev/null || true
sleep 1

echo "🚀 Starting production stack..."
make ngrok-prod-up

# Wait for nginx to be ready
echo "   Waiting for services..."
sleep 10

# Start ngrok tunnel for AI service
echo ""
echo "🤖 Starting AI service tunnel on port ${AI_PORT}..."
nohup ngrok http "${AI_PORT}" \
    --authtoken "${NGROK_TOKEN}" \
    --log stdout \
    --log-format json \
    --region ap \
    > /tmp/ngrok-ai.log 2>&1 &

NGROK_AI_PID=$!
echo "   AI ngrok PID: ${NGROK_AI_PID}"
echo "   Waiting for AI tunnel..."
sleep 8

# Get AI public URL
AI_PUBLIC_URL=$(curl -s http://127.0.0.1:4040/api/tunnels 2>/dev/null | python3 << 'PYCODE'
import sys, json
try:
    data = json.load(sys.stdin)
    tunnels = data.get('tunnels', [])
    for t in tunnels:
        if t.get('config', {}).get('addr') == f"http://localhost:${20128}":
            print(t.get('public_url'))
            break
except Exception as e:
    pass
PYCODE
)

if [ -z "$AI_PUBLIC_URL" ]; then
    # Try finding any ngrok tunnel
    AI_PUBLIC_URL=$(curl -s http://127.0.0.1:4040/api/tunnels 2>/dev/null | python3 -c "import sys,json; [print(t['public_url']) for t in json.load(sys.stdin).get('tunnels',[])]" 2>/dev/null | head -1)
fi

if [ -z "$AI_PUBLIC_URL" ]; then
    echo ""
    echo "❌ Failed to get AI public URL!"
    echo "   Check: curl http://127.0.0.1:4040/api/tunnels"
    echo "   Logs: tail -f /tmp/ngrok-ai.log"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ SETUP COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔗 URLs:"
echo "  • Frontend:   https://YOUR-TUNNEL.ngrok-free.dev  (port 8080)"
echo "  • AI Public:  ${AI_PUBLIC_URL}"
echo ""
echo "⚙️  Environment:"
export MAUEKSPOR_AI_MODE=remote
export MAUEKSPOR_AI_BASE_URL=${AI_PUBLIC_URL}
echo "  • AI Base URL: ${MAUEKSPOR_AI_BASE_URL}"
echo ""
echo "🧪 Test AI Endpoint:"
echo "  curl '${AI_PUBLIC_URL}/v1/models'"
echo ""
echo "📱 Access your app:"
echo "  open https://$(curl -s http://127.0.0.1:4040/api/tunnels | python3 -c 'import sys,json; print(json.load(sys.stdin)["tunnels"][0]["public_url"]')" 2>/dev/null)"
echo ""
echo "╭─────────────────────────────────────────────────────────────╮"
echo "│ 💡 To stop everything: make ngrok-tunnel-stop              │"
echo "│                                                             │"
echo "│ Your AI responses will now come from the public endpoint!  │"
echo "╰─────────────────────────────────────────────────────────────╯"
echo ""

# Keep script running so you can CTRL+C to stop
echo "Press CTRL+C to stop all services..."
wait $NGROK_AI_PID
