# MauEkspor Makefile - Production with Ngrok Tunnel

.PHONY: help ngrok-prod-up ngrok-prod-down ngrok-prod-build ngrok-prod-logs ngrok-prod-reseed \
        ngrok-tunnel-start ngrok-tunnel-stop ngrok-tunnel-docker ngrok-show-urls \
        local stop restart build docker-up docker-down test test-backend test-frontend

NGROK_TOKEN := 3IGWSdWwxcOQkQcxP0BcRkfHa5m_3nMcbXKdN93eUqsM1Hxjf
BACKEND_PORT := 8015
NGINX_PORT := 8080
FRONTEND_PORT := 3015
DATABASE_PORT := 5447

SHELL := /bin/bash
.ONESHELL:
.SILENT:

help:
	@echo "=========================================="
	@echo "🌍 MauEkspor - Deployment"
	@echo "=========================================="
	@echo ""
	@echo "Quick Start:"
	@echo "  make ngrok-prod-build    # Build all Docker images"
	@echo "  make ngrok-prod-up       # Start production services"
	@echo "  make ngrok-tunnel-start  # Start public ngrok tunnel"
	@echo ""
	@echo "Commands:"
	@echo "  make ngrok-prod-up       - Start production services (db/backend/frontend/nginx)"
	@echo "  make ngrok-prod-down     - Stop production services"
	@echo "  make ngrok-tunnel-start  - Start ngrok public tunnel (Docker preferred)"
	@echo "  make ngrok-tunnel-stop   - Stop ngrok tunnel"
	@echo "  make ngrok-show-urls     - Show public tunnel URLs"
	@echo "  make ngrok-prod-logs     - View production service logs"
	@echo "  make test                - Run all tests"
	@echo "  make test-backend        - Run backend tests"
	@echo "  make test-frontend       - Run frontend tests"
	@echo ""

ngrok-prod-build:
	@echo "Building Docker images..."
	docker compose -f docker-compose.production.yml build db backend frontend-prod nginx
	@echo "✅ Build complete!"

ngrok-prod-up: 
	@echo "Starting production services..."
	@echo "Checking for port conflicts on :$(BACKEND_PORT), :$(NGINX_PORT), :$(FRONTEND_PORT)..."
	@# Stop local uvicorn if it's occupying port 8015
	-pkill -f "uvicorn.*$(BACKEND_PORT)" 2>/dev/null || true
	-sleep 2
	
	@echo "Stopping any existing production containers..."
	-docker compose -f docker-compose.production.yml down
	-docker rm -f mauekspor-db-prod mauekspor-backend-prod mauekspor-frontend-prod mauekspor-nginx-prod mauekspor-ngrok-prod 2>/dev/null || true
	
	@echo "Starting database..."
	docker compose -f docker-compose.production.yml up -d db
	@sleep 5
	
	@echo "Starting backend, frontend, and nginx..."
	docker compose -f docker-compose.production.yml up -d backend frontend-prod nginx
	@sleep 8
	
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "✅ Services Running!"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "Local URLs:"
	@echo "  Frontend: http://localhost:$(FRONTEND_PORT)"
	@echo "  Backend:  http://localhost:$(BACKEND_PORT)/api/v1"
	@echo "  Nginx:    http://localhost:$(NGINX_PORT)"
	@echo ""
	@echo "Next step for public URL:"
	@echo "  make ngrok-tunnel-start"
	@echo "=========================================="

ngrok-prod-down:
	@echo "Stopping production services..."
	-docker compose -f docker-compose.production.yml down
	-docker rm -f mauekspor-db-prod mauekspor-backend-prod mauekspor-frontend-prod mauekspor-nginx-prod mauekspor-ngrok-prod 2>/dev/null || true
	@echo "✅ Stopped!"

ngrok-prod-stop: ngrok-prod-down

ngrok-prod-logs:
	@docker compose -f docker-compose.production.yml logs -f

ngrok-prod-reseed:
	@echo "WARNING: Deletes ALL data!"
	@read -p "Type YES: " confirm && \
	if [ "$$confirm" = "YES" ]; then \
		docker exec mauekspor-db-prod psql -U mauekspor -d mauekspor -c "DROP SCHEMA public CASCADE;" 2>/dev/null || true; \
		docker exec mauekspor-db-prod psql -U mauekspor -d mauekspor -c "CREATE SCHEMA public;" 2>/dev/null || true; \
		docker exec mauekspor-backend-prod python -c "from app.seed import seed_if_empty; seed_if_empty()" 2>/dev/null || true; \
		echo "✅ Re-seeded!"; \
	else \
		echo "Cancelled"; \
	fi

ngrok-tunnel-docker:
	@echo "═══════════════════════════════════════"
	@echo "🌐 Starting NGROK TUNNEL (Docker)"
	@echo "═══════════════════════════════════════"
	@docker compose -f docker-compose.ngrok-production.yml --profile ngrok up -d ngrok
	@sleep 8
	@echo ""
	@echo "✅ Ngrok tunnel container started!"
	@echo ""
	@echo "Public URLs:"
	@sleep 2
	@make ngrok-show-urls
	@echo ""
	@echo "To view logs: docker compose -f docker-compose.ngrok-production.yml logs -f ngrok"

ngrok-tunnel-start:
	@echo "═══════════════════════════════════════"
	@echo "🌐 Starting NGROK TUNNEL"
	@echo "═══════════════════════════════════════"
	@echo ""
	@echo "Target: localhost:$(NGINX_PORT) (nginx)"
	@echo "Creating PUBLIC URL from internet..."
	@echo ""
	@# Prefer Docker tunnel; fall back to local binary
	if docker compose -f docker-compose.ngrok-production.yml --profile ngrok up -d ngrok >/dev/null 2>&1; then \
		sleep 8; \
		echo "✅ Docker ngrok tunnel started"; \
		echo ""; \
		echo "Public URLs:"; \
		make ngrok-show-urls; \
		exit 0; \
	fi
	@echo "Docker tunnel failed, trying local ngrok binary..."
	-ngrok stop 2>/dev/null || true
	ngrok http $(NGINX_PORT) --log stdout --authtoken $(NGROK_TOKEN)

ngrok-tunnel-stop:
	@echo "Stopping ngrok..."
	-docker compose -f docker-compose.ngrok-production.yml --profile ngrok down 2>/dev/null || true
	-ngrok stop 2>/dev/null || true
	-pkill -f ngrok 2>/dev/null || true
	-docker rm -f mauekspor-ngrok-prod 2>/dev/null || true
	@echo "✅ Stopped"

ngrok-show-urls:
	@# Try Docker ngrok API first, then local
	@docker exec mauekspor-ngrok-prod curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -m json.tool 2>/dev/null || \
	curl -s http://localhost:4040/api/tunnels | python3 -m json.tool

local:
	@echo "Local mode:"
	@echo "  Backend:  cd backend && .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8015"
	@echo "  Frontend: cd frontend && pnpm dev"

stop:
	-pkill -f uvicorn 2>/dev/null || true

restart: stop local

build:
	cd frontend && pnpm build
	@echo "Built!"

docker-up:
	docker compose -f docker-compose.production.yml up -d
	@echo "Up!"

docker-down:
	docker compose -f docker-compose.production.yml down
	@echo "Down!"

test-backend:
	cd backend && .venv/bin/python -m pytest tests/ -q --tb=line

test-frontend:
	cd frontend && pnpm test

test: test-backend test-frontend

# Alternative: Use Cloudflare Tunnel instead of Ngrok
cloudflared-install:
	@echo "Installing Cloudflared..."
	cd /tmp && curl -L --output cloudflare.tar.gz https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && \
	sudo dpkg -i cloudflared-linux-amd64.deb && \
	rm cloudflared-linux-amd64.deb && \
	echo "✅ Cloudflared installed!"

cloudflared-tunnel-start:
	@echo "Starting Cloudflare Tunnel..."
	@echo "You'll need to configure tunnel first with: sudo cloudflared tunnel create my-tunnel"
	cloudflared tunnel run my-tunnel
