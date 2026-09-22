# MauEkspor Makefile - Production with Ngrok Tunnel
#
# PORT LAYOUT (anti-tabrakan):
#   Production Docker  : db=5447, backend=8015, frontend=3015, nginx=8080
#   Development local  : backend=8016, frontend=5188 (vite dev dengan proxy)
#   AI endpoint lokal  : 20128
#   Ngrok admin UI     : 4040

.PHONY: help \
        ngrok-prod-build ngrok-prod-up ngrok-prod-down ngrok-prod-stop \
        ngrok-prod-logs ngrok-prod-reseed ngrok-prod-status \
        ngrok-tunnel-start ngrok-tunnel-stop ngrok-show-urls ngrok-with-ai \
        dev-backend dev-frontend dev-up dev-down \
        stop stop-all build docker-up docker-down \
        test test-backend test-frontend

# ─── Load .env (secrets & config) ─────────────────────────────────────────────
# .env is gitignored; make 'include' parses KEY=VALUE lines, 'export' passes
# them to every recipe shell. Override precedence: real env vars win.
ifneq (,$(wildcard .env))
include .env
export
endif

# ─── Ports (defaults; .env values win via ?=) ─────────────────────────────────
BACKEND_PORT      ?= 8015
NGINX_PORT        ?= 8080
FRONTEND_PORT     ?= 3015
DB_PORT           ?= 5447
DEV_BACKEND_PORT  ?= 8016
DEV_FRONTEND_PORT ?= 5188

SHELL := /bin/bash

# ─────────────────────────────────────────────────────────────────────────────
help:
	@echo "════════════════════════════════════════════════════════"
	@echo "  🌍  MauEkspor - Deployment Guide"
	@echo "════════════════════════════════════════════════════════"
	@echo ""
	@echo "  QUICK START:"
	@echo "    make ngrok-prod-build   # Build Docker images (sekali)"
	@echo "    make ngrok-prod-up      # Start production stack"
	@echo "    make ngrok-tunnel-start # Buka tunnel publik"
	@echo ""
	@echo "  PRODUCTION:"
	@echo "    ngrok-prod-build  - Build semua Docker images"
	@echo "    ngrok-prod-up     - Start db/backend/frontend/nginx (Docker)"
	@echo "    ngrok-prod-down   - Stop & remove production containers"
	@echo "    ngrok-prod-status - Cek status semua services"
	@echo "    ngrok-prod-logs   - Tail logs production"
	@echo "    ngrok-prod-reseed - Reset & seed ulang database"
	@echo ""
	@echo "  TUNNEL:"
	@echo "    ngrok-tunnel-start - Buka ngrok -> nginx:$(NGINX_PORT)"
	@echo "    ngrok-tunnel-stop  - Stop ngrok"
	@echo "    ngrok-show-urls    - Tampilkan public URL aktif"
	@echo ""
	@echo "  DEVELOPMENT:"
	@echo "    dev-backend   - Backend lokal port $(DEV_BACKEND_PORT)"
	@echo "    dev-frontend  - Frontend dev port $(DEV_FRONTEND_PORT)"
	@echo "    backend-local - Backend + AI access (port 8016, real AI not mock)"
	@echo "    ngrok-with-ai - Prod ngrok + AI via cloudflared (REAL AI, RECOMMENDED)"
	@echo "    dev-down      - Stop semua proses dev"
	@echo ""
	@echo "  TESTING:"
	@echo "    test          - Run semua tests"
	@echo "    test-backend  - Backend pytest"
	@echo "    test-frontend - Frontend vitest"
	@echo ""
	@echo "  PORT LAYOUT:"
	@echo "    Prod Docker: db=$(DB_PORT) | backend=$(BACKEND_PORT) | frontend=$(FRONTEND_PORT) | nginx=$(NGINX_PORT)"
	@echo "    Dev local:   backend=$(DEV_BACKEND_PORT) | frontend=$(DEV_FRONTEND_PORT)"
	@echo "════════════════════════════════════════════════════════"

# ─────────────────────────────────────────────────────────────────────────────
# BUILD
# ─────────────────────────────────────────────────────────────────────────────
ngrok-prod-build:
	@echo "🔨 Building Docker images..."
	docker compose -p mauekspor-prod -f docker-compose.production.yml build db backend frontend-prod nginx
	@echo "✅ Build selesai!"

# ─────────────────────────────────────────────────────────────────────────────
# PRODUCTION UP
# ─────────────────────────────────────────────────────────────────────────────
ngrok-prod-up:
	@bash scripts/prod-up.sh

ngrok-prod-down:
	@echo "🛑 Stopping production stack..."
	@docker compose -p mauekspor-prod -f docker-compose.production.yml down --remove-orphans 2>/dev/null || true
	@docker rm -f mauekspor-db-prod mauekspor-backend-prod mauekspor-frontend-prod mauekspor-nginx-prod mauekspor-ngrok-prod 2>/dev/null || true
	@echo "✅ Production stack dihentikan"

ngrok-prod-stop: ngrok-prod-down

ngrok-prod-status:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  📊 Production Stack Status"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@docker ps --format "  {{.Names}}\t{{.Status}}\t{{.Ports}}" \
		--filter "name=mauekspor" 2>/dev/null | column -t || echo "  (tidak ada container)"
	@echo ""
	@echo "  Local URLs:"
	@echo "    Frontend → http://localhost:$(FRONTEND_PORT)"
	@echo "    Backend  → http://localhost:$(BACKEND_PORT)/api/v1"
	@echo "    Nginx    → http://localhost:$(NGINX_PORT)"
	@echo ""
	@echo "  run: make ngrok-tunnel-start untuk public URL"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ngrok-prod-logs:
	docker compose -p mauekspor-prod -f docker-compose.production.yml logs -f --tail=100

ngrok-prod-reseed:
	@echo "⚠️  WARNING: Ini akan MENGHAPUS semua data!"
	@read -p "Ketik YES untuk lanjut: " confirm; \
	if [ "$$confirm" = "YES" ]; then \
		docker exec mauekspor-db-prod psql -U mauekspor -d mauekspor \
			-c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" 2>/dev/null || true; \
		docker exec mauekspor-backend-prod python -c \
			"from app.seed import seed_if_empty; seed_if_empty()" 2>/dev/null || true; \
		echo "✅ Re-seed selesai!"; \
	else \
		echo "Dibatalkan."; \
	fi

# ─────────────────────────────────────────────────────────────────────────────
# NGROK TUNNEL
# ─────────────────────────────────────────────────────────────────────────────
ngrok-tunnel-start:
	@bash scripts/tunnel-start.sh

ngrok-tunnel-stop:
	@bash scripts/tunnel-stop.sh

# Watchdog: auto-restart ngrok kalau mati (untuk free tier yang sering expire)
# Run di terminal terpisah: make tunnel-keep-alive
tunnel-keep-alive:
	@bash scripts/tunnel-monitor.sh

ngrok-show-urls:
	@echo ""
	@echo "  🌍 Public Tunnel URLs:"
	@curl -s http://127.0.0.1:4040/api/tunnels 2>/dev/null \
		| python3 -c "\
import sys, json; \
d = json.load(sys.stdin); \
tunnels = d.get('tunnels', []); \
[print('  ➤', t['public_url']) for t in tunnels] \
if tunnels else print('  (belum aktif — coba: make ngrok-tunnel-start)')" \
		2>/dev/null || echo "  (ngrok API tidak dapat dijangkau)"
	@echo ""

stop:
	@pkill -f "uvicorn" 2>/dev/null && echo "✅ uvicorn dihentikan" || echo "✅ tidak ada uvicorn"

stop-all:
	@bash -c "pkill -f 'uvicorn' 2>/dev/null || true"
	@bash -c "pkill -f 'vite.*$(DEV_FRONTEND_PORT)' 2>/dev/null || true"
	@bash -c "pkill -f 'ngrok http' 2>/dev/null || true"
	@echo "✅ Semua service lokal dihentikan"

# ─────────────────────────────────────────────────────────────────────────────
# DEVELOPMENT (port terpisah: 8016 / 5188, tidak tabrakan dengan prod 8015)
# ─────────────────────────────────────────────────────────────────────────────
dev-backend:
	@echo "🔧 Starting dev backend → http://localhost:$(DEV_BACKEND_PORT)"
	cd backend && .venv/bin/uvicorn app.main:app \
		--host 0.0.0.0 --port $(DEV_BACKEND_PORT) --reload

dev-frontend:
	@echo "🔧 Starting dev frontend → http://localhost:$(DEV_FRONTEND_PORT)"
	cd frontend && BACKEND_ORIGIN=http://localhost:$(DEV_BACKEND_PORT) pnpm dev \
		--port $(DEV_FRONTEND_PORT)

dev-up:
	@echo "🔧 Dev services:"
	@echo "   Terminal 1: make dev-backend   (port $(DEV_BACKEND_PORT))"
	@echo "   Terminal 2: make dev-frontend  (port $(DEV_FRONTEND_PORT))"

# Backend lokal dengan AI access (port 8016, connect ke PostgreSQL Docker port 5447)
# Gunakan ini saat butuh AI features yang real (bukan mock)
backend-local:
	@bash scripts/backend-local.sh

dev-down:
	@bash -c "pkill -f 'uvicorn.*$(DEV_BACKEND_PORT)' 2>/dev/null || true; echo 'Dev backend stopped'"
	@bash -c "pkill -f '$(DEV_FRONTEND_PORT)' 2>/dev/null || true; echo 'Dev frontend stopped'"

# ─────────────────────────────────────────────────────────────────────────────
# NGROK WITH AI SERVICE (production + public AI access)
# ─────────────────────────────────────────────────────────────────────────────
# Start production backend/frontend AND expose AI service via ngrok tunnel
# Use this when you want full stack accessible publicly WITH real AI responses
ngrok-with-ai:
	@bash scripts/ngrok-with-ai.sh

# ─────────────────────────────────────────────────────────────────────────────
build:
	cd frontend && pnpm build && echo "✅ Frontend build selesai!"

docker-up:
	docker compose -p mauekspor-prod -f docker-compose.production.yml up -d && echo "✅ Up!"

docker-down:
	docker compose -p mauekspor-prod -f docker-compose.production.yml down && echo "✅ Down!"

# ─────────────────────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────────────────────
test-backend:
	@echo "🧪 Backend tests..."
	cd backend && .venv/bin/python -m pytest tests/ --tb=short -q

test-frontend:
	@echo "🧪 Frontend tests..."
	cd frontend && pnpm test

test: test-backend test-frontend
	@echo "✅ All tests done"

# ─────────────────────────────────────────────────────────────────────────────
# CLOUDFLARE TUNNEL (alternatif ngrok)
# ─────────────────────────────────────────────────────────────────────────────
cloudflared-install:
	@cd /tmp && curl -L --output cloudflare.deb \
		https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb \
		&& sudo dpkg -i cloudflare.deb && rm cloudflare.deb && echo "✅ Cloudflared installed!"

cloudflared-tunnel-start:
	@echo "Starting Cloudflare Tunnel → http://localhost:$(NGINX_PORT)"
	cloudflared tunnel --url http://localhost:$(NGINX_PORT)
