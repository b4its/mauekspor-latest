#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Backend coverage (pytest --cov) ==="
(cd "$DIR/backend" && .venv/bin/python -m pytest --cov=app --cov-report=term-missing -q)

echo ""
echo "=== Frontend tests (vitest) ==="
(cd "$DIR/frontend" && pnpm run test)