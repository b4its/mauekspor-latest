#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")/.." && pwd)"
FAIL=0

echo "=== 1. Backend tests (pytest) ==="
(cd "$DIR/backend" && .venv/bin/python -m pytest -q) || FAIL=1

echo ""
echo "=== 2. Frontend check (svelte-check) ==="
(cd "$DIR/frontend" && pnpm run check) || FAIL=1

echo ""
echo "=== 3. Frontend tests (vitest) ==="
(cd "$DIR/frontend" && pnpm run test) || FAIL=1

echo ""
echo "=== 4. Frontend build ==="
(cd "$DIR/frontend" && pnpm run build) || FAIL=1

echo ""
if [ "$FAIL" -eq 0 ]; then
	echo "✅ ALL TESTS PASSED"
else
	echo "❌ SOME TESTS FAILED"
	exit 1
fi