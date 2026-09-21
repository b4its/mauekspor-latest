#!/bin/bash
# scripts/ngrok-with-ai.sh — Production stack via ngrok + AI via Cloudflare quick tunnel
#
# WHY THIS ARCHITECTURE:
#   1. Docker containers CANNOT reach host services directly (host firewall
#      blocks all container→host traffic — verified on ports 5447/20128/8080).
#   2. ngrok free tier assigns ONE shared domain — two tunnels on one domain
#      CONFLICT (requests randomly hit either upstream). Verified broken.
#
#   SOLUTION:
#   - App  : ngrok free tunnel  → nginx:8080        (1 tunnel, no conflict)
#   - AI   : cloudflared quick tunnel → localhost:20128
#            (separate service, separate random *.trycloudflare.com domain)
#   - Docker backend reaches AI via the public trycloudflare URL (internet
#     egress works from containers), bypassing the local firewall.

set -e

# Load .env (secrets) — real env vars take precedence
set -a
[ -f "$(dirname "$0")/../.env" ] && . "$(dirname "$0")/../.env"
set +a

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

: "${NGROK_TOKEN:?Set NGROK_TOKEN in .env}"
AI_PORT="${AI_PORT:-20128}"
NGINX_PORT="${NGINX_PORT:-8080}"
CLOUDFLARED_BIN="$REPO_ROOT/scripts/bin/cloudflared"

echo "═══════════════════════════════════════════════════════════"
echo "  🌐 MauEkspor Production (ngrok) + AI (cloudflared)"
echo "═══════════════════════════════════════════════════════════"

# ── 0. Pre-flight ─────────────────────────────────────────────────────────────
echo ""
echo "⚙️  Pre-flight checks..."
if ! curl -s --max-time 3 "http://localhost:${AI_PORT}/v1/models" -o /dev/null; then
    echo "  ❌ AI service tidak merespons di localhost:${AI_PORT}"
    exit 1
fi
echo "  ✅ AI service aktif di localhost:${AI_PORT}"

if [ ! -x "$CLOUDFLARED_BIN" ]; then
    echo "  ⬇️  Mengunduh cloudflared..."
    mkdir -p "$(dirname "$CLOUDFLARED_BIN")"
    curl -sL --max-time 120 -o "$CLOUDFLARED_BIN" \
        https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
    chmod +x "$CLOUDFLARED_BIN"
fi
echo "  ✅ cloudflared: $("$CLOUDFLARED_BIN" --version 2>/dev/null | head -c 30)"

# ── 1. Stop old tunnels ───────────────────────────────────────────────────────
echo "  🛑 Menghentikan tunnel lama..."
pkill -f "ngrok http"      2>/dev/null || true
pkill -f "ngrok start"     2>/dev/null || true
pkill -f "cloudflared"     2>/dev/null || true
# Stop legacy watchdog that fights over ngrok (restarts ngrok http 8080)
pkill -f "tunnel-monitor"  2>/dev/null || true
sleep 1

# ── 2. Production stack ───────────────────────────────────────────────────────
echo "  🐳 Memastikan production stack berjalan..."
if ! docker ps --format '{{.Names}}' | grep -q "mauekspor-nginx-prod"; then
    make ngrok-prod-up
else
    echo "  ✅ Production stack sudah berjalan"
fi

# ── 3. Start ngrok app tunnel (single — no domain conflict) ───────────────────
echo "  🌐 Memulai ngrok tunnel (app → nginx:${NGINX_PORT})..."
nohup ngrok http "${NGINX_PORT}" \
    --authtoken "${NGROK_TOKEN}" \
    --log /tmp/ngrok-mauekspor.log \
    --log-format json \
    > /tmp/ngrok-stdout.log 2>&1 < /dev/null &
sleep 8

APP_URL=$(curl -s --max-time 5 http://127.0.0.1:4040/api/tunnels 2>/dev/null \
    | python3 -c "import sys,json; t=json.load(sys.stdin).get('tunnels',[]); print(t[0]['public_url'] if t else 'NONE')" 2>/dev/null || echo "NONE")
if [ "$APP_URL" = "NONE" ] || [ -z "$APP_URL" ]; then
    echo "  ❌ ngrok tunnel gagal. Log: tail -30 /tmp/ngrok-mauekspor.log"
    exit 1
fi
echo "  ✅ App tunnel : ${APP_URL}"

# ── 4. Start cloudflared AI tunnel ────────────────────────────────────────────
echo "  🤖 Memulai cloudflared quick tunnel (AI → localhost:${AI_PORT})..."
nohup "$CLOUDFLARED_BIN" tunnel --url "http://localhost:${AI_PORT}" \
    --logfile /tmp/cloudflared-ai.log \
    > /tmp/cloudflared-stdout.log 2>&1 < /dev/null &

echo "     Menunggu trycloudflare URL (max 20s)..."
AI_URL="NONE"
for i in $(seq 1 10); do
    sleep 2
    AI_URL=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cloudflared-ai.log 2>/dev/null | head -1 || true)
    [ -n "$AI_URL" ] && break
done

if [ -z "$AI_URL" ]; then
    echo "  ❌ cloudflared gagal. Log: tail -30 /tmp/cloudflared-ai.log"
    exit 1
fi
echo "  ✅ AI tunnel  : ${AI_URL}"

# ── 5. Verify AI via its tunnel ───────────────────────────────────────────────
echo ""
echo "  🧪 Test AI via tunnel publik..."
AI_TEST=$(curl -s --max-time 15 "${AI_URL}/v1/models" 2>/dev/null | head -c 80)
if [ -n "$AI_TEST" ]; then
    echo "  ✅ AI merespons: ${AI_TEST:0:60}..."
else
    echo "  ⚠️  AI belum merespons via tunnel"
fi

# ── 6. Persist AI URL + restart Docker backend ────────────────────────────────
echo ""
echo "  ⚙️  Menyimpan AI URL ke .env dan restart backend..."
# Persist with /v1 suffix — backend expects base_url to include the API version
AI_BASE_URL="${AI_URL}/v1"
if grep -q "^MAUEKSPOR_AI_PUBLIC_URL=" .env 2>/dev/null; then
    sed -i "s|^MAUEKSPOR_AI_PUBLIC_URL=.*|MAUEKSPOR_AI_PUBLIC_URL=${AI_BASE_URL}|" .env
else
    echo "MAUEKSPOR_AI_PUBLIC_URL=${AI_BASE_URL}" >> .env
fi

docker compose -f docker-compose.production.yml up -d backend 2>&1 | grep -E "Recreated|Started" || true
echo "     Menunggu backend healthy..."
for i in $(seq 1 12); do
    if docker inspect mauekspor-backend-prod 2>/dev/null | grep -q '"healthy"'; then
        echo "  ✅ Backend healthy"
        break
    fi
    sleep 5
done

# ── 7. End-to-end verification ─────────────────────────────────────────────────
echo ""
echo "  🧪 Verifikasi end-to-end via app tunnel..."
sleep 3
HEALTH=$(curl -s --max-time 10 "${APP_URL}/api/v1/health" 2>/dev/null)
echo "     App health : ${HEALTH:-TIMEOUT}"
AI_STATUS=$(curl -s --max-time 20 "${APP_URL}/api/v1/ai/status/" 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)['data']
    print(f\"mode={d['mode']} health={d['health']} circuit={d.get('circuit_breaker','?')}\")
except Exception:
    print('unreachable')
" 2>/dev/null)
echo "     AI status  : ${AI_STATUS}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎉 SELESAI!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  📱 App (share this): ${APP_URL}"
echo "  🤖 AI tunnel       : ${AI_URL}"
echo "  🛠️  ngrok inspector : http://127.0.0.1:4040"
echo ""
echo "  Login: admin@mauekspor.example / admin123"
echo ""
echo "  Stop semua: make ngrok-tunnel-stop && make ngrok-prod-down"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
