.PHONY: help local dev prod stop restart clean build docker-build docker-up docker-down seed reseed test help-docs status logs

# Variables
NGROK_TOKEN := 3IGWSdWwxcOQkQcxP0BcRkfHa5m_3nMcbXKdN93eUqsM1Hxjf
BACKEND_PORT := 8016
FRONTEND_PORT := 5188
PROD_FRONTEND_PORT := 3015
DATABASE_PORT := 5447

SHELL := /bin/bash
.ONESHELL:
.SILENT:

help:
	@echo "=========================================="
	@echo "🌍 MauEkspor - Makefile Commands"
	@echo "=========================================="
	@echo ""
	@echo "🚀 Deployment Commands:"
	@echo "  make local           - Run development (backend + frontend on localhost)"
	@echo "  make dev             - Same as local"
	@echo "  make prod            - Run production mode with Docker containers"
	@echo ""
	@echo "⚠️  IMPORTANT: Use separate docker-compose files!"
	@echo "  • docker-compose.local.yml   - For local development (optional DB only)"
	@echo "  • docker-compose.prod.yml    - For production (full containerized)"
	@echo "  • DO NOT mix them - ports will conflict!"
	@echo ""
	@echo "🌐 Ngrok Tunnels:"
	@echo "  make ngrok-local     - Start ngrok tunnels for local/dev"
	@echo "  make ngrok-prod      - Start ngrok tunnels for production"
	@echo "  make ngrok-all       - Start all ngrok tunnels"
	@echo "  make ngrok-stop      - Stop all ngrok tunnels"
	@echo ""
	@echo "⚙️  Build & Management:"
	@echo "  make build           - Build frontend for production"
	@echo "  make docker-build    - Build Docker images (production)"
	@echo "  make docker-up       - Start production containers"
	@echo "  make docker-down     - Stop all Docker containers"
	@echo ""
	@echo "📊 Database Operations:"
	@echo "  make seed            - Seed database with initial data"
	@echo "  make reseed          - Reset and re-seed database"
	@echo "  make db-clean        - Remove database file (SQLite only)"
	@echo ""
	@echo "🔍 Monitoring:"
	@echo "  make status          - Check running services (local & docker)"
	@echo "  make logs            - View Docker logs (production)"
	@echo "  make logs-backend    - View backend logs only"
	@echo "  make logs-frontend   - View frontend logs only"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  make clean           - Clean build artifacts"
	@echo "  make distclean       - Full cleanup (including .env backups)"
	@echo ""
	@echo "💡 Usage Examples:"
	@echo "  # Local development"
	@echo "  make local"
	@echo ""
	@echo "  # Production with Docker"
	@echo "  make prod"
	@echo ""
	@echo "  # With ngrok tunnels"
	@echo "  make ngrok-prod"
	@echo ""
	@echo "=========================================="

local:
	@echo ""
	@echo "Starting MauEkspor in LOCAL mode..."
	@echo "Backend API: http://localhost:$(BACKEND_PORT)"
	@echo "Frontend Dev: http://localhost:$(FRONTEND_PORT)"
	@echo ""
	@# Install dependencies if needed
	@if [ ! -d "backend/.venv" ]; then \
		echo "📦 Setting up Python virtual environment..."; \
		cd backend && python3 -m venv .venv; \
		cd backend && .venv/bin/pip install -r requirements.txt; \
	fi
	@if [ ! -d "frontend/node_modules" ]; then \
		echo "📦 Installing frontend dependencies..."; \
		cd frontend && pnpm install; \
	fi
	
	@# Start PostgreSQL container first (optional)
	@if [ "$$START_DB" = "true" ]; then \
		echo "🗄️ Starting database container..."; \
		docker compose -f docker-compose.local.yml --profile local up -d db; \
		sleep 3; \
	fi
	
	@# Start services in background
	@echo "🚀 Starting backend server..."
	cd backend && .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port $(BACKEND_PORT) &
	@sleep 2
	
	@echo "🎨 Starting frontend dev server..."
	cd frontend && pnpm run dev --host 0.0.0.0 --port $(FRONTEND_PORT) &
	
	@echo ""
	@echo "✅ Local development server started!"
	@echo "Press Ctrl+C to stop all services"
	@wait

dev: local

prod:
	@echo ""
	@echo "Starting MauEkspor in PRODUCTION mode (Docker)..."
	@docker compose -f docker-compose.prod.yml --profile production up -d db backend frontend
	@echo ""
	@echo "✅ Production containers started!"
	@echo "Backend API: http://localhost:$(BACKEND_PORT)"
	@echo "Frontend Prod: http://localhost:$(PROD_FRONTEND_PORT)"
	@echo ""
	@echo "To view logs: make logs"

stop:
	@echo ""
	@echo "Stopping all services..."
	@pkill -f uvicorn 2>/dev/null || true
	@pkill -f pnpm 2>/dev/null || true
	@pkill -f node 2>/dev/null || true
	@echo "✅ Stopped all processes"

docker-down:
	@echo ""
	@echo "Stopping Docker containers (production)..."
	@docker compose -f docker-compose.prod.yml --profile production down
	@echo "✅ Production containers stopped"
	@# Also stop local database if running
	@docker compose -f docker-compose.local.yml --profile local down 2>/dev/null || true
	@echo "✅ Local database stopped (if running)"

restart:
	@make stop || true
	@sleep 1
	@make local

build:
	@echo ""
	@echo "Building frontend for production..."
	@cd frontend && pnpm build
	@cd frontend && pnpm package
	@echo ""
	@echo "✅ Frontend built successfully!"
	@echo "Output directory: frontend/build/"

docker-build:
	@echo ""
	@echo "Building Docker images (production)..."
	@docker compose -f docker-compose.prod.yml --profile production build db backend frontend
	@echo ""
	@echo "✅ Docker images built successfully!"

ngrok-install:
	@echo ""
	@echo "Installing pyngrok..."
	@pip install --upgrade pyngrok 2>/dev/null || pip3 install --upgrade pyngrok 2>/dev/null
	@echo "✅ pyngrok installed"

ngrok-tunnel-local:
	@python3 start-ngrok-tunnels.py

ngrok-tunnel-prod:
	@python3 start-ngrok-tunnels.py

ngrok-local: ngrok-install
	@echo ""
	@echo "Starting ngrok tunnels for LOCAL/DEV mode..."
	@echo "Tunneling ports: $(BACKEND_PORT), 5189, 3016"
	@echo ""
	@python3 start-ngrok-tunnels.py

ngrok-prod: ngrok-install
	@echo ""
	@echo "Starting ngrok tunnels for PRODUCTION mode..."
	@echo "Tunneling ports: $(BACKEND_PORT), 5189, $(PROD_FRONTEND_PORT)"
	@echo ""
	@python3 start-ngrok-tunnels.py

ngrok-all: ngrok-install
	@echo ""
	@echo "Starting ALL ngrok tunnels (development + production)..."
	@echo "Tunneling ports: $(BACKEND_PORT), 5189, 3016"
	@echo ""
	@python3 start-ngrok-tunnels.py

ngrok-stop:
	@echo ""
	@echo "Stopping all ngrok tunnels..."
	@pkill -f ngrok 2>/dev/null || true
	@echo "✅ All ngrok tunnels stopped"

seed:
	@echo ""
	@echo "Seeding database with initial data..."
	@cd backend && .venv/bin/python -c "from app.seed import seed_if_empty; seed_if_empty()"
	@echo ""
	@echo "✅ Database seeded successfully!"
	@echo "Default users created:"
	@echo "  Admin: admin@mauekspor.example / admin123"
	@echo "  Exporter: rizal@kopigayo.example / rizal123"
	@echo "  Buyer: aya@hikari.example / buyer123"

reseed:
	@echo ""
	@echo "⚠️  Warning: This will delete existing data and re-seed!"
	@read -p "Are you sure? Type 'YES' to continue: " confirm && \
	if [ "$$confirm" = "YES" ]; then \
		echo "Deleting existing data..."; \
		rm -f mauekspor.db backend/mauekspor.db; \
		echo "Re-seeding database..."; \
		cd backend && .venv/bin/python -c "from app.seed import seed_if_empty; seed_if_empty()"; \
		echo "✅ Database re-seeded successfully!"; \
	else \
		echo "❌ Operation cancelled"; \
	fi

db-clean:
	@echo ""
	@echo "Removing database file..."
	@rm -f mauekspor.db backend/mauekspor.db
	@echo "✅ Database removed (will be recreated on next run)"

test:
	@echo ""
	@echo "Running tests..."
	@cd backend && .venv/bin/pytest -v || echo "Tests completed"
	@echo ""
	@echo "✅ Tests executed"

status:
	@echo ""
	@echo "=========================================="
	@echo "📊 Service Status"
	@echo "=========================================="
	@echo ""
	@echo "🔧 Checking processes..."
	@ps aux | grep -E "(uvicorn|pnpm|node|ngrok)" | grep -v grep || echo "No active services found"
	@echo ""
	@echo "🌐 Port availability:"
	@lsof -i :$(BACKEND_PORT) 2>/dev/null || echo "  Backend ($(BACKEND_PORT)): not listening"
	@lsof -i :5189 2>/dev/null || echo "  Frontend Dev (5189): not listening"
	@lsof -i :$(PROD_FRONTEND_PORT) 2>/dev/null || echo "  Frontend Prod ($(PROD_FRONTEND_PORT)): not listening"
	@echo ""
	@echo "🐳 Production Docker containers:"
	@docker compose -f docker-compose.prod.yml --profile production ps 2>/dev/null || echo "No production containers running"
	@echo ""
	@echo "🐳 Local Docker containers (if any):"
	@docker compose -f docker-compose.local.yml --profile local ps 2>/dev/null || echo "No local containers running"
	@echo ""
	@echo "=========================================="

logs:
	@echo ""
	@echo "Viewing Docker logs (production)..."
	@docker compose -f docker-compose.prod.yml --profile production logs -f

logs-backend:
	@echo ""
	@echo "Viewing backend logs..."
	@docker compose -f docker-compose.prod.yml --profile production logs -f backend

logs-frontend:
	@echo ""
	@echo "Viewing frontend logs..."
	@docker compose -f docker-compose.prod.yml --profile production logs -f frontend

logs-db:
	@echo ""
	@echo "Viewing database logs..."
	@docker compose -f docker-compose.prod.yml --profile production logs -f db

clean:
	@echo ""
	@echo "Cleaning build artifacts..."
	@rm -rf frontend/build
	@rm -rf frontend/.svelte-kit/output
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleaned build artifacts"

distclean: clean
	@echo ""
	@echo "Performing full cleanup..."
	@rm -rf frontend/node_modules
	@rm -rf backend/.venv
	@rm -rf frontend/.pnpm-store
	@rm -f mauekspor.db backend/mauekspor.db
	@echo "✅ Full cleanup complete (dependencies and data removed)"

install:
	@echo ""
	@echo "Installing all dependencies..."
	@echo "Setting up backend..."
	@cd backend && [ ! -d ".venv" ] && python3 -m venv .venv || true
	@cd backend && .venv/bin/pip install -r requirements.txt
	@echo "Setting up frontend..."
	@cd frontend && pnpm install
	@echo "✅ All dependencies installed!"

setup: install seed
	@echo ""
	@echo "=========================================="
	@echo "🎉 Setup Complete!"
	@echo "=========================================="
	@echo ""
	@echo "You can now run:"
	@echo "  make local     - Development mode"
	@echo "  make prod      - Production mode (Docker)"
	@echo "  make ngrok-local  - With ngrok tunnels (local)"
	@echo ""
	@echo "Access URLs:"
	@echo "  Backend: http://localhost:$(BACKEND_PORT)"
	@echo "  Frontend: http://localhost:5188"
	@echo ""
	@echo "Login credentials:"
	@echo "  Admin: admin@mauekspor.example / admin123"
	@echo "  Exporter: rizal@kopigayo.example / rizal123"
	@echo "  Buyer: aya@hikari.example / buyer123"
	@echo ""
