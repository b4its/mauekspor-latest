#!/bin/bash
# scripts/dev.sh — Jalankan backend dev di port 8016 (tidak tabrakan dengan Docker prod 8015)
# Usage: ./scripts/dev.sh [--reload]

set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT/backend"

PORT=8016
echo "🔧 Starting dev backend on http://localhost:$PORT"
echo "   (port 8016 = dev, port 8015 = production Docker — tidak tabrakan)"
echo ""

.venv/bin/uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --reload \
    --log-level info
