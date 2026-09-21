#!/bin/bash
set -e

# Ngrok tunnel entrypoint
# Usage: docker run -e AUTHTOKEN=<token> -e PORT=8080 -e SERVICE_NAME=nginx <image>

if [ -z "$AUTHTOKEN" ]; then
    echo "❌ ERROR: AUTHTOKEN environment variable is required"
    exit 1
fi

# Default to nginx service on port 8080 if not specified
PORT="${PORT:-8080}"
SERVICE_NAME="${SERVICE_NAME:-nginx}"
REGION="${REGION:-ap}"

# Determine target. If SERVICE_NAME is set, use service name (Docker DNS).
# Otherwise, use localhost/127.0.0.1 for the given port.
if [ -n "$SERVICE_NAME" ] && [ "$SERVICE_NAME" != "localhost" ]; then
    TARGET="${SERVICE_NAME}:${PORT}"
else
    TARGET="localhost:${PORT}"
fi

echo "═══════════════════════════════════════════"
echo "🌐 Starting Ngrok Tunnel"
echo "   Target: ${TARGET}"
echo "   Region: ${REGION}"
echo "═══════════════════════════════════════════"

# Configure ngrok with authtoken
ngrok config add-authtoken "$AUTHTOKEN" >/dev/null 2>&1 || true

# Start ngrok HTTP tunnel
exec dumb-init ngrok http "${TARGET}" \
    --region="${REGION}" \
    --log=stdout \
    --log-format=json
