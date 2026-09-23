# MauEkspor - Complete Local Development with Docker + LAN Access
# ================================================================
# Auto-installation dengan Docker - support akses dari device lain
# ================================================================

.PHONY: help install dev-up dev-down dev-restart dev-status dev-logs \
        dev-logs-backend dev-logs-frontend dev-shell-backend dev-network \
        dev-clean dev-rebuild dev-db-reset

SHELL := /bin/bash
COMPOSE_FILE := docker-compose.dev.yml
PROJECT_NAME := mauekspor-dev
ENV_FILE := .env.local

help:
	@echo ""
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║  🚀 MauEkspor - Docker Development Commands (LAN Ready)  ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "🎯 FIRST TIME SETUP:"
	@echo "  make install          # Run complete auto-installation"
	@echo ""
	@echo "🚀 DAILY COMMANDS:"
	@echo "  make dev-up           # Start all services (build if needed)"
	@echo "  make dev-down         # Stop all services"
	@echo "  make dev-restart      # Restart all services"
	@echo "  make dev-status       # Show status & health checks"
	@echo "  make dev-network      # Show LAN network access URLs"
	@echo ""
	@echo "📊 MONITORING:"
	@echo "  make dev-logs         # Show all logs"
	@echo "  make dev-logs-backend # Backend logs only"
	@echo "  make dev-logs-frontend# Frontend logs only"
	@echo "  make dev-shell-backend# Open shell in backend container"
	@echo ""
	@echo "🧹 MAINTENANCE:"
	@echo "  make dev-clean        # Remove containers, volumes, images"
	@echo "  make dev-rebuild      # Clean rebuild from scratch"
	@echo "  make dev-db-reset     # Reset database (HAPUS SEMUA DATA!)"
	@echo ""
	@echo "🌐 URLs:"
	@echo "  Local:    http://localhost:5188"
	@echo "  LAN:      http://$$(make -s _host-ip):5188"
	@echo "  Backend:  http://localhost:8016/api/v1"
	@echo ""
	@echo "🔑 Login: admin@mauekspor.example / admin123"
	@echo ""

_host-ip:
	@bash -c 'IP=$$(ip route get 1.1.1.1 2>/dev/null | grep -oP "src \K\S+"); [ -z "$$IP" ] && IP=$$(ip addr show 2>/dev/null | grep -E "inet .* scope global" | head -1 | awk "{print \$$2}" | cut -d/ -f1); [ -z "$$IP" ] && IP="127.0.0.1"; echo "$$IP"'

install:
	@bash ./install.sh

dev-up:
	@bash ./scripts/fix-firewall.sh
	@echo ""
	@echo "🚀 Starting MauEkspor development stack..."
	@docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE) --env-file $(ENV_FILE) up -d --build
	@echo ""
	@echo "⏳ Waiting for services..."
	@sleep 20
	@make dev-status

dev-down:
	@echo ""
	@echo "🛑 Stopping MauEkspor development stack..."
	@docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE) --env-file $(ENV_FILE) down
	@echo "✅ Services stopped"

dev-restart:
	@echo ""
	@echo "🔄 Restarting services..."
	@docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE) --env-file $(ENV_FILE) restart
	@echo "✅ Services restarted"

dev-status:
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  📊 Services Status"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE) --env-file $(ENV_FILE) ps
	@echo ""
	@echo "🔍 Health Checks:"
	@echo -n "  Database  : " && docker inspect --format='{{.State.Health.Status}}' mauekspor-dev-db 2>/dev/null || echo "N/A"
	@echo -n "  Backend   : " && (curl -s --max-time 3 http://localhost:8016/api/v1/health 2>/dev/null | grep -q ok && echo "✅ OK") || echo "❌ Not responding"
	@echo -n "  Frontend  : " && (curl -s --max-time 3 http://localhost:5188/ 2>/dev/null | head -c 1 | grep -q . && echo "✅ OK") || echo "❌ Not responding"
	@echo -n "  AI Service: " && (curl -s --max-time 3 http://localhost:20128/v1/models 2>/dev/null | grep -q qd && echo "✅ OK") || echo "❌ Not responding"
	@echo ""
	@make -s dev-network

dev-network:
	@HOST_IP=$$(make -s _host-ip); \
	echo "🌐 Network Access (same WiFi/LAN):"; \
	echo "  This device: http://localhost:5188"; \
	echo "  Other devices: http://$$HOST_IP:5188"; \
	echo "  Backend API:   http://$$HOST_IP:8016/api/v1"; \
	echo "  Swagger Docs:  http://$$HOST_IP:8016/docs"

dev-logs:
	@docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE) --env-file $(ENV_FILE) logs -f

dev-logs-backend:
	@docker logs -f mauekspor-dev-backend

dev-logs-frontend:
	@docker logs -f mauekspor-dev-frontend

dev-logs-db:
	@docker logs -f mauekspor-dev-db

dev-shell-backend:
	@docker exec -it mauekspor-dev-backend /bin/bash

dev-shell-frontend:
	@docker exec -it mauekspor-dev-frontend /bin/sh

dev-clean:
	@echo ""
	@echo "🧹 Cleaning up all development resources..."
	@docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE) --env-file $(ENV_FILE) down -v --remove-orphans
	@echo "✅ Cleanup complete"

dev-rebuild:
	@echo ""
	@echo "🔨 Rebuilding from scratch..."
	@docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE) --env-file $(ENV_FILE) down -v --remove-orphans
	@docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE) --env-file $(ENV_FILE) build --no-cache
	@docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE) --env-file $(ENV_FILE) up -d
	@echo "✅ Rebuild complete"

dev-db-reset:
	@echo ""
	@echo "🗑️  Resetting database - ALL DATA WILL BE LOST!"
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE) --env-file $(ENV_FILE) down; \
		docker volume rm mauekspor-dev_db-data 2>/dev/null || true; \
		docker volume rm mauekspor-dev_uploads 2>/dev/null || true; \
		docker compose -p $(PROJECT_NAME) -f $(COMPOSE_FILE) --env-file $(ENV_FILE) up -d; \
		echo "✅ Database reset complete"; \
	else \
		echo "❌ Cancelled"; \
	fi
