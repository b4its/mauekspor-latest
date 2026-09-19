# MauEkspor Makefile - Production with Ngrok Tunnel

.PHONY: help ngrok-prod-up ngrok-prod-stop ngrok-prod-build ngrok-prod-logs ngrok-prod-reseed ngrok-tunnel-start ngrok-tunnel-stop ngrok-show-urls local stop restart build docker-up docker-down

NGROK_TOKEN := 3IGWSdWwxcOQkQcxP0BcRkfHa5m_3nMcbXKdN93eUqsM1Hxjf
BACKEND_PORT := 8016
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
	@echo "  make ngrok-prod-build"
	@echo "  make ngrok-prod-up"
	@echo "  [NEW TERMINAL] make ngrok-tunnel-start"
	@echo ""
	@echo "Commands:"
	@echo "  make ngrok-prod-up     - Start services (not ngrok)"
	@echo "  make ngrok-tunnel-start- Start ngrok public tunnel"
	@echo "  make ngrok-prod-stop   - Stop everything"
	@echo "  make ngrok-prod-logs   - View logs"
	@echo ""

ngrok-prod-build:
	@echo "Building Docker images..."
	docker compose -f docker-compose.production.yml build db backend frontend-prod nginx
	@echo "✅ Build complete!"

ngrok-prod-up: 
	@echo "Starting production services..."
	-docker compose -f docker-compose.production.yml down
	-docker rm -f mauekspor-db-prod mauekspor-backend-prod mauekspor-frontend-prod mauekspor-nginx-prod 2>/dev/null || true
	
	docker compose -f docker-compose.production.yml up -d db
	@sleep 8
	
	docker compose -f docker-compose.production.yml up -d backend frontend-prod nginx
	
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "✅ Services Running Locally!"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "Local URLs:"
	@echo "  Frontend: http://localhost:3015"
	@echo "  Backend:  http://localhost:8015/api/v1"
	@echo "  Nginx:    http://localhost:8080"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "⚠️  NEXT STEP (in new terminal):"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "Run in NEW terminal:"
	@echo "  make ngrok-tunnel-start"
	@echo ""
	@echo "This creates PUBLIC URL for your app!"
	@echo "=========================================="

ngrok-prod-stop:
	@echo "Stopping services..."
	-docker compose -f docker-compose.production.yml down
	-docker rm -f mauekspor-db-prod mauekspor-backend-prod mauekspor-frontend-prod mauekspor-nginx-prod 2>/dev/null || true
	@echo "✅ Stopped!"

ngrok-prod-logs:
	@docker compose -f docker-compose.production.yml logs -f

ngrok-prod-reseed:
	@echo "WARNING: Deletes ALL data!"
	@read -p "Type YES: " confirm && \
	if [ "$$confirm" = "YES" ]; then \
		docker exec mauekspor-db-prod psql -U mauekspor -d mauekspor -c "DROP SCHEMA public CASCADE;" 2>/dev/null || true; \
		docker exec mauekspor-db-prod psql -U mauekspor -d mauekspor -c "CREATE SCHEMA public;" 2>/dev/null || true; \
		cd backend && .venv/bin/python -c "from app.seed import seed_if_empty; seed_if_empty()"; \
		echo "✅ Re-seeded!"; \
	else \
		echo "Cancelled"; \
	fi

ngrok-tunnel-start:
	@echo "═══════════════════════════════════════"
	@echo "🌐 Starting NGROK TUNNEL"
	@echo "═══════════════════════════════════════"
	@echo ""
	@echo "Target: localhost:8080 (nginx)"
	@echo "Creating PUBLIC URL from internet..."
	@echo ""
	-ngrok stop 2>/dev/null || true
	ngrok http 8080 --log stdout --authtoken ${NGROK_TOKEN}

ngrok-tunnel-stop:
	@echo "Stopping ngrok..."
	-ngrok stop 2>/dev/null || true
	pkill -f ngrok 2>/dev/null || true
	@echo "✅ Stopped"

ngrok-show-urls:
	@curl -s http://localhost:4040/api/tunnels | python3 -m json.tool

local:
	@echo "Local mode not configured"

stop:
	pkill -f uvicorn 2>/dev/null || true

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
