#!/bin/bash
# scripts/tunnel-start.sh — Buka ngrok public tunnel ke nginx:8080
set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

NGROK_TOKEN="${NGROK_TOKEN:?NGROK_TOKEN not set — check .env}"
NGINX_PORT="${NGINX_PORT:-8080}"
NGROK_LOG="/tmp/ngrok-mauekspor.log"

echo "═══════════════════════════════════════════"
echo "  🌐 Starting Ngrok Public Tunnel"
echo "  Target: localhost:${NGINX_PORT}"
echo "  Log:    ${NGROK_LOG}"
echo "═══════════════════════════════════════════"
echo ""
echo "  ⚠️  NOTE (free tier):"
echo "     Tunnel akan mati otomatis setelah ~1-2 jam"
echo "     atau kalau proses ngrok mati."
echo "     Untuk auto-restart: make tunnel-keep-alive"
echo ""

# Hentikan ngrok lama (ignore error jika tidak ada)
pkill -f "ngrok http ${NGINX_PORT}" 2>/dev/null || true
sleep 1

# Pastikan nginx benar-benar berjalan dulu
if ! curl -s "http://localhost:${NGINX_PORT}" --max-time 3 -o /dev/null; then
    echo "⚠️  WARNING: Nginx di port ${NGINX_PORT} tidak merespons"
    echo "   Pastikan production stack berjalan: make ngrok-prod-up"
    echo ""
fi

# Buka tunnel (background)
echo "🚀 Starting ngrok process..."
nohup ngrok http "${NGINX_PORT}" \
    --authtoken "${NGROK_TOKEN}" \
    --log "${NGROK_LOG}" \
    --log-format json \
    > /tmp/ngrok-stdout.log 2>&1 < /dev/null &

NGROK_PID=$!
echo "   Ngrok PID: ${NGROK_PID}"
echo ""

# Berikan waktu lebih untuk ngrok setup (tunggu hingga 20 detik)
echo "   Waiting for tunnel establishment... (timeout 20s)"
MAX_WAIT=20
WAITED=0

TUNNEL_URL=""
while [ $WAITED -lt $MAX_WAIT ]; do
    sleep 2
    WAITED=$((WAITED + 2))
    
    # Cek apakah ngrok masih jalan
    if ! kill -0 "$NGROK_PID" 2>/dev/null; then
        echo "❌ Ngrok process tidak aktif!"
        tail -10 "$NGROK_LOG" 2>/dev/null
        exit 1
    fi
    
    # Coba fetch tunnel URL menggunakan Python satu baris
    TUNNEL_URL=$(curl -s "http://127.0.0.1:4040/api/tunnels" 2>/dev/null | python3 -c "import sys,json; [print(t['public_url']) for t in json.load(sys.stdin).get('tunnels',[]) if t.get('public_url')]" 2>/dev/null || true)
    
    if [ -n "$TUNNEL_URL" ] && [[ "$TUNNEL_URL" != *"ERROR"* ]] && [[ "$TUNNEL_URL" != *"fail"* ]]; then
        break
    fi
    
    printf "."
done

echo ""
echo ""

if [ -z "$TUNNEL_URL" ]; then
    echo ""
    echo "  ❌ Tunnel belum aktif setelah ${MAX_WAIT}s."
    echo "  Log ngrok:"
    tail -20 "$NGROK_LOG" 2>/dev/null || echo "  (tidak ada log)"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Tunnel AKTIF!"
echo ""
echo "  🌍 Public URL:"
echo "     ${TUNNEL_URL}"
echo ""
echo "  Web UI:     http://127.0.0.1:4040"
echo "  Config API: http://127.0.0.1:4040/api"
echo ""
echo "  Test API:"
echo "     curl -s ${TUNNEL_URL}/api/v1/"
echo ""
echo "  Login:"
echo "     curl -s -X POST ${TUNNEL_URL}/api/v1/auth/login/ \\"
echo "       -H 'Content-Type: application/json' \\"
echo "       -d '{\"email\":\"admin@mauekspor.example\",\"password\":\"admin123\"}'"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Quick test via tunnel
echo ""
echo "  Quick tests..."

# Test health endpoint
HEALTH_RESULT=$(curl -s --max-time 10 "${TUNNEL_URL}/api/v1/health" 2>/dev/null | head -c 50)
if echo "$HEALTH_RESULT" | grep -q '"status"'; then
    echo "  ✅ API Health: OK (${HEALTH_RESULT})"
else
    HTTP_CODE=$(curl -s --max-time 10 -o /dev/null -w "%{http_code}" "${TUNNEL_URL}/api/v1/health" 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        echo "  ✅ API Health: HTTP 200 OK"
    else
        echo "  ⚠️  API Health: HTTP ${HTTP_CODE}"
    fi
fi

# Test login
LOGIN_RESULT=$(curl -s --max-time 15 -X POST "${TUNNEL_URL}/api/v1/auth/login/" \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@mauekspor.example","password":"admin123"}' 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('role','?'))" 2>/dev/null || echo "error")
if [ "$LOGIN_RESULT" = "Admin" ]; then
    echo "  ✅ Login: Admin authenticated successfully"
else
    echo "  ⚠️  Login: Returned '${LOGIN_RESULT}' (may be rate-limited from testing)"
fi

echo ""
echo "╭───────────────────────────────────────────────╮"
echo "│ 💡 Tips untuk production:                     │"
echo "│ • Gunakan make tunnel-keep-alive untuk        │"
echo "│   auto-restart saat tunnel mati               │"
echo "│ • Tunnel free tier akan expire dalam 1-2 jam  │"
echo "│ • Untuk stable URL, upgrade ke paid tier      │"
echo "╰───────────────────────────────────────────────╯"
echo ""
