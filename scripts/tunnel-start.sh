#!/bin/bash
# scripts/tunnel-start.sh — Buka ngrok public tunnel ke nginx:8080
set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

NGROK_TOKEN="${NGROK_TOKEN:-3IGWSdWwxcOQkQcxP0BcRkfHa5m_3nMcbXKdN93eUqsM1Hxjf}"
NGINX_PORT="${NGINX_PORT:-8080}"
NGROK_LOG="${NGROK_LOG:-/tmp/ngrok-mauekspor.log}"

echo "═══════════════════════════════════════════"
echo "  🌐 Starting Ngrok Public Tunnel"
echo "  Target: localhost:${NGINX_PORT}"
echo "  Log:    ${NGROK_LOG}"
echo "═══════════════════════════════════════════"

# Hentikan ngrok lama (ignore error jika tidak ada)
pkill -f "ngrok http" 2>/dev/null || true
sleep 1

# Pastikan nginx benar-benar berjalan dulu
if ! curl -s "http://localhost:${NGINX_PORT}" --max-time 3 -o /dev/null; then
    echo "⚠️  WARNING: Nginx di port ${NGINX_PORT} tidak merespons"
    echo "   Pastikan production stack berjalan: make ngrok-prod-up"
    echo ""
fi

# Buka tunnel (background)
ngrok http "${NGINX_PORT}" \
    --authtoken "${NGROK_TOKEN}" \
    --log "${NGROK_LOG}" \
    --log-format json \
    2>>"${NGROK_LOG}" &

NGROK_PID=$!
echo "   Ngrok PID: ${NGROK_PID}"
echo "   Waiting for tunnel (10s)..."
sleep 10

# Ambil URL dari API
TUNNEL_URL=$(curl -s http://127.0.0.1:4040/api/tunnels 2>/dev/null \
    | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    tunnels = d.get('tunnels', [])
    for t in tunnels:
        if 'public_url' in t:
            print(t['public_url'])
            break
except:
    pass
" 2>/dev/null || echo "")

if [ -n "$TUNNEL_URL" ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  ✅ Tunnel AKTIF!"
    echo ""
    echo "  🌍 Public URL:"
    echo "     ${TUNNEL_URL}"
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
    echo "  Quick test..."
    HTTP=$(curl -s "${TUNNEL_URL}" --max-time 8 -o /dev/null -w "%{http_code}" 2>/dev/null || echo "000")
    if [ "$HTTP" = "200" ]; then
        echo "  ✅ Frontend: HTTP ${HTTP} OK"
    else
        echo "  ⚠️  Frontend: HTTP ${HTTP} (mungkin butuh beberapa detik lagi)"
    fi

    API=$(curl -s -X POST "${TUNNEL_URL}/api/v1/auth/login/" \
        -H "Content-Type: application/json" \
        -d '{"email":"admin@mauekspor.example","password":"admin123"}' \
        --max-time 10 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('role','?'))" 2>/dev/null || echo "error")
    if [ "$API" = "Admin" ]; then
        echo "  ✅ API login: Admin OK"
    else
        echo "  ⚠️  API login: ${API}"
    fi
else
    echo ""
    echo "  ❌ Tunnel belum aktif setelah 10s."
    echo "  Cek log: tail -f ${NGROK_LOG}"
    echo "  Atau tunggu sebentar dan cek: curl http://127.0.0.1:4040/api/tunnels"
    exit 1
fi
