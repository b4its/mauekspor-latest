#!/bin/bash
# scripts/tunnel-monitor.sh — Ngrok tunnel watchdog (keeps it alive)
#
# Run: bash scripts/tunnel-monitor.sh
# Or:  make tunnel-keep-alive
#
# This script:
#   1. Starts ngrok tunnel if not running
#   2. Every 30s checks if tunnel is alive
#   3. Auto-restarts if tunnel dies
#   4. Logs all activity to /tmp/ngrok-monitor.log
#
# Ctrl+C to stop the watchdog.

set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

NGROK_TOKEN="${NGROK_TOKEN:-3IGWSdWwxcOQkQcxP0BcRkfHa5m_3nMcbXKdN93eUqsM1Hxjf}"
NGINX_PORT="${NGINX_PORT:-8080}"
PID_FILE="/tmp/ngrok-mauekspor.pid"
LOG_FILE="/tmp/ngrok-mauekspor.log"
MONITOR_LOG="/tmp/ngrok-monitor.log"

echo "══════════════════════════════════════════════════════" | tee "$MONITOR_LOG"
echo "  🛡️  Ngrok Tunnel Watchdog" | tee -a "$MONITOR_LOG"
echo "  Target: localhost:${NGINX_PORT}" | tee -a "$MONITOR_LOG"
echo "  PID file: ${PID_FILE}" | tee -a "$MONITOR_LOG"
echo "  Log: ${LOG_FILE}" | tee -a "$MONITOR_LOG"
echo "══════════════════════════════════════════════════════" | tee -a "$MONITOR_LOG"
echo "" | tee -a "$MONITOR_LOG"

# Cleanup on exit - hanya stop monitoring, JANGAN kill ngrok
# (ngrok akan jalan terus sampai mati sendiri atau di-kill manual via tunnel-stop.sh)
cleanup() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🛑 Watchdog stopped (ngrok tetap jalan)" | tee -a "$MONITOR_LOG"
    # Jangan kill ngrok di sini - biar ngrok jalan sendiri
    # Kalau mau stop ngrok, pakai: make ngrok-tunnel-stop
    exit 0
}
trap cleanup INT TERM

# Check if nginx is running
check_nginx() {
    curl -s "http://localhost:${NGINX_PORT}" --max-time 3 -o /dev/null
}

# Start ngrok tunnel
start_tunnel() {
    local ts=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$ts] 🚀 Starting ngrok tunnel to localhost:${NGINX_PORT}" | tee -a "$MONITOR_LOG"
    
    # Kill any existing ngrok
    pkill -f "ngrok http ${NGINX_PORT}" 2>/dev/null || true
    sleep 1
    
    # Start fresh
    nohup ngrok http "${NGINX_PORT}" \
        --authtoken "${NGROK_TOKEN}" \
        --log "${LOG_FILE}" \
        --log-format json \
        > /tmp/ngrok-stdout.log 2>&1 < /dev/null &
    
    local pid=$!
    echo "$pid" > "$PID_FILE"
    echo "[$ts] Ngrok PID: $pid" | tee -a "$MONITOR_LOG"
    
    # Wait for tunnel to be ready
    local wait=0
    while [ $wait -lt 15 ]; do
        sleep 1
        wait=$((wait+1))
        local url=$(get_tunnel_url)
        if [ -n "$url" ] && [ "$url" != "NO_TUNNEL" ]; then
            echo "[$ts] ✅ Tunnel active: $url" | tee -a "$MONITOR_LOG"
            return 0
        fi
    done
    echo "[$ts] ⚠️  Tunnel failed to start after 15s" | tee -a "$MONITOR_LOG"
    return 1
}

# Get current tunnel URL
get_tunnel_url() {
    curl -s http://127.0.0.1:4040/api/tunnels 2>/dev/null \
        | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    tunnels = d.get('tunnels', [])
    if tunnels:
        print(tunnels[0].get('public_url', 'NO_TUNNEL'))
    else:
        print('NO_TUNNEL')
except:
    print('NO_TUNNEL')
" 2>/dev/null
}

# Check if ngrok process is alive
is_ngrok_alive() {
    if [ ! -f "$PID_FILE" ]; then return 1; fi
    local pid=$(cat "$PID_FILE")
    kill -0 "$pid" 2>/dev/null
}

# Check if tunnel is responding via API
is_tunnel_healthy() {
    local url=$(get_tunnel_url)
    if [ -z "$url" ] || [ "$url" = "NO_TUNNEL" ]; then return 1; fi
    # Test the tunnel actually works
    curl -s "${url}/api/v1/health" --max-time 10 -o /dev/null 2>/dev/null
}

# ── Main loop ─────────────────────────────────────────────────────────────────
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting watchdog loop (30s interval)" | tee -a "$MONITOR_LOG"
echo ""

restart_count=0
while true; do
    ts=$(date '+%Y-%m-%d %H:%M:%S')
    
    if ! check_nginx; then
        echo "[$ts] ⚠️  Nginx not responding on port ${NGINX_PORT}" | tee -a "$MONITOR_LOG"
        echo "[$ts]    Run: make ngrok-prod-up" | tee -a "$MONITOR_LOG"
        sleep 30
        continue
    fi
    
    if is_ngrok_alive && is_tunnel_healthy; then
        url=$(get_tunnel_url)
        echo "[$ts] ✅ Tunnel alive: $url" | tee -a "$MONITOR_LOG"
    else
        restart_count=$((restart_count + 1))
        echo "[$ts] ⚠️  Tunnel dead! Restarting (restart #$restart_count)..." | tee -a "$MONITOR_LOG"
        start_tunnel
    fi
    
    sleep 30
done
