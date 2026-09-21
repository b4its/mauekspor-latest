#!/bin/bash
# scripts/prod-up.sh — Start production Docker stack, handle port conflicts.
# Usage: ./scripts/prod-up.sh [--rebuild]
#
# PORT LAYOUT:
#   Production Docker: db=5447, backend=8015, frontend=3015, nginx=8080
#   Dev local:         backend=8016, frontend=5188

set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "══════════════════════════════════════════════"
echo "  🚀 MauEkspor Production Stack"
echo "══════════════════════════════════════════════"
echo ""

# ── 1. Hentikan dev uvicorn yang mungkin running ──────────────────────────────
echo "⚙️  Cleaning up dev processes..."
pkill -f "uvicorn.*app.main" 2>/dev/null && echo "  ↳ uvicorn dev dihentikan" || echo "  ↳ tidak ada uvicorn dev"
sleep 1

# ── 2. Hentikan container lama ────────────────────────────────────────────────
echo ""
echo "🛑 Stopping existing production containers..."
docker compose -f docker-compose.production.yml down --remove-orphans 2>/dev/null || true
docker rm -f \
    mauekspor-db-prod \
    mauekspor-backend-prod \
    mauekspor-frontend-prod \
    mauekspor-nginx-prod \
    mauekspor-ngrok-prod 2>/dev/null || true
sleep 2

# ── 3. Rebuild jika diminta ───────────────────────────────────────────────────
if [[ "$1" == "--rebuild" ]]; then
    echo ""
    echo "🔨 Rebuilding Docker images..."
    docker compose -f docker-compose.production.yml build db backend frontend-prod nginx
fi

# ── 4. Cek port (info only, Docker yang pegang jadi skip exit) ────────────────
echo ""
echo "🔍 Port status check:"
for port in 8015 8080 3015 5447; do
    if ss -tlnH 2>/dev/null | grep -q ":$port "; then
        echo "  ⚠️  $port sudah terpakai (mungkin container lain atau sistem)"
    else
        echo "  ✅ $port bebas"
    fi
done

# ── 5. Start stack ─────────────────────────────────────────────────────────────
echo ""
echo "🐳 Starting database..."
docker compose -f docker-compose.production.yml up -d db
echo "   Waiting for db healthy (max 40s)..."
WAIT=0
until docker inspect mauekspor-db-prod 2>/dev/null | grep -q '"healthy"' || [ $WAIT -ge 40 ]; do
    sleep 2; WAIT=$((WAIT+2)); printf "."
done
echo ""

echo ""
echo "🐳 Starting backend, frontend, nginx..."
docker compose -f docker-compose.production.yml up -d backend frontend-prod nginx

echo "   Waiting for backend healthy (max 60s)..."
WAIT=0
until docker inspect mauekspor-backend-prod 2>/dev/null | grep -q '"healthy"' || [ $WAIT -ge 60 ]; do
    sleep 2; WAIT=$((WAIT+2)); printf "."
done
echo ""

# ── 6. Status ──────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Production Stack Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker ps --filter "name=mauekspor" \
    --format "  {{.Names}}\t{{.Status}}\t{{.Ports}}" \
    | column -t
echo ""
echo "  Local URLs:"
echo "    Frontend → http://localhost:3015"
echo "    Backend  → http://localhost:8015/api/v1"
echo "    Nginx    → http://localhost:8080"
echo ""
echo "  Test login:"
echo "    curl -s -X POST http://localhost:8080/api/v1/auth/login/ \\"
echo "      -H 'Content-Type: application/json' \\"
echo "      -d '{\"email\":\"admin@mauekspor.example\",\"password\":\"admin123\"}'"
echo ""
echo "  Start tunnel: make ngrok-tunnel-start"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
