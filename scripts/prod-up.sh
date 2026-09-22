#!/bin/bash
# scripts/prod-up.sh — Start production Docker stack with AUTOMATIC port
# conflict resolution.
#
# ROOT CAUSE this script solves:
#   Orphaned/other-stack containers (e.g. dev `mauekspor-frontend` on 3015)
#   held production ports → `docker compose up` failed with
#   "Bind for 0.0.0.0:3015 failed: port is already allocated".
#   The old script only WARNED about conflicts — it never resolved them.
#
# PORT LAYOUT (no overlaps, permanent):
#   Production Docker : db=${DB_PORT:-5448}, backend=8015, frontend=3015, nginx=8080
#   Dev stack (docker-compose.yml) : db=5447, backend=8000 (host net),
#                                    frontend=3016, vite dev=5188
#
# Usage: scripts/prod-up.sh [--rebuild]

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# ── Load .env ──────────────────────────────────────────────────────────────────
set -a
[ -f "$REPO_ROOT/.env" ] && . "$REPO_ROOT/.env"
set +a

COMPOSE="docker compose -p mauekspor-prod -f docker-compose.production.yml"
BACKEND_PORT="${BACKEND_PORT:-8015}"
NGINX_PORT="${NGINX_PORT:-8080}"
FRONTEND_PORT="${FRONTEND_PORT:-3015}"
DB_PORT="${DB_PORT:-5448}"
FORCE_KILL="${FORCE_PORT_KILL:-0}"

# Semua container ber-prefix mauekspor- adalah milik kita (dev/prod/test) —
# aman di-auto-remove saat bentrok port produksi. Project eksternal → butuh FORCE.
OWN_CONTAINER_RE='^mauekspor-'

echo "══════════════════════════════════════════════"
echo "  🚀 MauEkspor Production Stack"
echo "══════════════════════════════════════════════"

# ── 1. Stop dev uvicorn yang mungkin memegang port backend ────────────────────
echo ""
echo "⚙️  Membersihkan proses dev lokal..."
pkill -f "uvicorn.*app.main" 2>/dev/null && echo "  ↳ uvicorn dev dihentikan" || echo "  ↳ tidak ada uvicorn dev"
sleep 1

# ── 2. Stop project production lama (config lama otomatis direcreate) ─────────
echo ""
echo "🛑 Menghentikan stack production lama..."
$COMPOSE down --remove-orphans 2>/dev/null || true

# ── 3. AUTO-RESOLVE port conflicts ────────────────────────────────────────────
resolve_port() {
    local port="$1"
    local holders
    holders=$(docker ps --filter "publish=${port}" --format '{{.Names}}\t{{.Label "com.docker.compose.project"}}' 2>/dev/null)
    if [ -z "$holders" ]; then
        echo "  ✅ ${port} bebas"
        return 0
    fi
    while IFS=$'\t' read -r cname project; do
        [ -z "$cname" ] && continue
        if echo "$cname" | grep -qE "$OWN_CONTAINER_RE"; then
            echo "  ♻️  ${port}: container production lama ${cname} dihentikan & dihapus"
            docker rm -f "$cname" >/dev/null 2>&1 || true
        elif [ "$FORCE_KILL" = "1" ] || [ "$FORCE_PORT_KILL" = "1" ]; then
            echo "  ⛔ ${port}: container non-production ${cname} (project=${project:-external}) di-FORCE stop"
            docker rm -f "$cname" >/dev/null 2>&1 || true
        else
            echo "  ❌ ${port} dipakai container LAIN: ${cname} (project=${project:-external})"
            echo "     Resolusi manual salah satu:"
            echo "       docker rm -f ${cname}"
            echo "       FORCE_PORT_KILL=1 make ngrok-prod-up   # auto-stop semua penghalang"
            exit 1
        fi
    done <<EOF
${holders}
EOF
}

# Host-process holder check (bukan docker)
resolve_host_process() {
    local port="$1"
    local pid
    pid=$(ss -tlnpH 2>/dev/null | grep ":${port} " | grep -oP 'pid=\K[0-9]+' | head -1 || true)
    if [ -n "$pid" ]; then
        local pname
        pname=$(ps -p "$pid" -o comm= 2>/dev/null || echo "?")
        if [ "$FORCE_PORT_KILL" = "1" ]; then
            echo "  ⛔ ${port}: proses host ${pname}(pid=${pid}) di-kill (FORCE_PORT_KILL=1)"
            kill -9 "$pid" 2>/dev/null || true
            sleep 1
        else
            echo "  ❌ ${port} dipakai proses HOST: ${pname} (pid=${pid})"
            echo "     Resolusi: kill ${pid}  ATAU  FORCE_PORT_KILL=1 make ngrok-prod-up"
            exit 1
        fi
    fi
}

echo ""
echo "🔍 Resolusi konflik port (prod: ${BACKEND_PORT}/${NGINX_PORT}/${FRONTEND_PORT}/${DB_PORT})..."
for port in "$BACKEND_PORT" "$NGINX_PORT" "$FRONTEND_PORT" "$DB_PORT"; do
    resolve_port "$port"
    resolve_host_process "$port"
done

# ── 4. Bersihkan container mauekspor orphan (nama lama / exited) ──────────────
ORPHANS=$(docker ps -aq --filter "name=mauekspor-frontend-test" 2>/dev/null || true)
if [ -n "$ORPHANS" ]; then
    echo "  ♻️  Menghapus container orphan: $(echo $ORPHANS | xargs docker rm -f 2>/dev/null | tr '\n' ' ')"
fi

# ── 5. Rebuild opsional ────────────────────────────────────────────────────────
if [[ "$1" == "--rebuild" ]]; then
    echo ""
    echo "🔨 Rebuild images..."
    $COMPOSE build db backend frontend-prod nginx
fi

# ── 6. Start stack ─────────────────────────────────────────────────────────────
echo ""
echo "🐳 Starting database (port ${DB_PORT})..."
$COMPOSE up -d db
echo "   Menunggu db healthy (max 40s)..."
WAIT=0
until docker inspect mauekspor-db-prod 2>/dev/null | grep -q '"healthy"' || [ $WAIT -ge 40 ]; do
    sleep 2; WAIT=$((WAIT+2)); printf "."
done
echo ""

echo ""
echo "🐳 Starting backend, frontend, nginx..."
$COMPOSE up -d backend frontend-prod nginx
echo "   Menunggu backend healthy (max 60s)..."
WAIT=0
until docker inspect mauekspor-backend-prod 2>/dev/null | grep -q '"healthy"' || [ $WAIT -ge 60 ]; do
    sleep 2; WAIT=$((WAIT+2)); printf "."
done
echo ""

# ── 7. Status ──────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Production Stack Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker ps --filter "name=mauekspor" \
    --format "  {{.Names}}\t{{.Status}}\t{{.Ports}}" | column -t
echo ""
echo "  Local URLs:"
echo "    Frontend → http://localhost:${FRONTEND_PORT}"
echo "    Backend  → http://localhost:${BACKEND_PORT}/api/v1"
echo "    Nginx    → http://localhost:${NGINX_PORT}"
echo ""
echo "  Start tunnel: make ngrok-tunnel-start  |  make ngrok-with-ai (real AI)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
