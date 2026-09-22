#!/bin/bash
# MauEkspor - Complete Docker Auto Installer (LAN Access)
# ========================================================
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }
log_step() { echo -e "${BLUE}[→]${NC} $1"; }

get_host_ip() {
    local ip
    ip=$(ip route get 1.1.1.1 2>/dev/null | grep -oP 'src \K\S+')
    if [ -z "$ip" ]; then
        ip=$(ip addr show 2>/dev/null | grep -E "inet .* scope global" | head -1 | awk '{print $2}' | cut -d/ -f1)
    fi
    if [ -z "$ip" ]; then
        ip="127.0.0.1"
    fi
    echo "$ip"
}

HOST_IP=$(get_host_ip)

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🚀 MauEkspor - Complete Docker Setup (LAN Ready)        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

log_step "Checking system requirements..."
if command -v docker &> /dev/null; then
    log_info "Docker is installed ($(docker --version 2>/dev/null | cut -d' ' -f3))"
else
    log_error "Docker not found! Install Docker first."
fi

if docker compose version &> /dev/null; then
    log_info "Docker Compose is installed"
else
    log_error "Docker Compose not found!"
fi

log_info "Host LAN IP detected: $HOST_IP"

echo ""
log_step "Creating local development environment..."

mkdir -p backend/app/uploads
mkdir -p scripts/bin

log_step "Creating .env.local configuration..."
cat > .env.local << ENVTEMPLATE
# MauEkspor Local Development Configuration
# Supports LAN access from other devices on the same network

# Network
HOST_IP=$HOST_IP

# Database
POSTGRES_USER=mauekspor
POSTGRES_PASSWORD=mauekspor
POSTGRES_DB=mauekspor

# Ports
BACKEND_PORT=8016
FRONTEND_PORT=5188
DB_PORT=5447

# Backend settings
MAUEKSPOR_SECRET_KEY=dev-secret-key-change-in-production
MAUEKSPOR_DATABASE_URL=postgresql://mauekspor:mauekspor@localhost:5447/mauekspor
MAUEKSPOR_UPLOAD_DIR=/app/uploads

# AI Configuration - uses AI service on localhost:20128
MAUEKSPOR_AI_MODE=remote
MAUEKSPOR_AI_API_KEY=sk-dede08aea594e222-upk4p8-5bfa2c54
MAUEKSPOR_AI_BASE_URL=http://localhost:20128/v1
MAUEKSPOR_AI_MODEL=qd/dmodel

# CORS - allow localhost, LAN IP, and all local network origins
MAUEKSPOR_CORS_ORIGINS='["http://localhost","http://127.0.0.1","http://0.0.0.0","http://$HOST_IP","http://$HOST_IP:5188","http://$HOST_IP:8016"]'

# Frontend uses relative API URL, Vite proxies to backend
VITE_API_BASE_URL=/api/v1
BACKEND_ORIGIN=http://localhost:8016

# Security
MAUEKSPOR_ENABLE_CSRF=0
MAUEKSPOR_COOKIE_SECURE=0

# Disable rate limiter for local development
MAUEKSPOR_DISABLE_RATE_LIMIT=1
ENVTEMPLATE

log_info ".env.local created"

# Copy templates (pre-built correct YAML/Dockerfile)
log_step "Restoring docker-compose.dev.yml from template..."
if [ -f docker-compose.dev.yml.template ]; then
    cp docker-compose.dev.yml.template docker-compose.dev.yml
    log_info "docker-compose.dev.yml restored"
else
    log_warn "docker-compose.dev.yml.template not found - using existing"
fi

log_step "Restoring backend/Dockerfile.dev from template..."
if [ -f backend/Dockerfile.dev.template ]; then
    cp backend/Dockerfile.dev.template backend/Dockerfile.dev
    log_info "backend/Dockerfile.dev restored"
fi

log_step "Restoring frontend/Dockerfile.dev from template..."
if [ -f frontend/Dockerfile.dev.template ]; then
    cp frontend/Dockerfile.dev.template frontend/Dockerfile.dev
    log_info "frontend/Dockerfile.dev restored"
fi

log_step "Updating .gitignore..."
if ! grep -q ".env.local" .gitignore 2>/dev/null; then
    echo "" >> .gitignore
    echo "# Local environment" >> .gitignore
    echo ".env.local" >> .gitignore
fi
log_info ".gitignore updated"

log_step "Building Docker images..."
echo ""
docker compose -p mauekspor-dev -f docker-compose.dev.yml --env-file .env.local build --parallel

log_step "Starting services..."
docker compose -p mauekspor-dev -f docker-compose.dev.yml --env-file .env.local up -d

log_step "Waiting for database to be healthy..."
for i in {1..30}; do
    DB_STATUS=$(docker inspect --format='{{.State.Health.Status}}' mauekspor-dev-db 2>/dev/null || echo "none")
    if [ "$DB_STATUS" = "healthy" ]; then
        log_info "Database is healthy"
        break
    fi
    log_info "Waiting for database ($i/30)..."
    sleep 3
done

log_step "Waiting for backend API..."
for i in {1..40}; do
    if curl -s --max-time 3 http://localhost:8016/api/v1/health 2>/dev/null | grep -q ok; then
        log_info "Backend API is responding"
        break
    fi
    log_info "Waiting for backend ($i/40)..."
    sleep 3
done

log_step "Waiting for frontend..."
for i in {1..40}; do
    if curl -s --max-time 3 http://localhost:5188/ 2>/dev/null | head -c 1 | grep -q .; then
        log_info "Frontend is responding"
        break
    fi
    log_info "Waiting for frontend ($i/40)..."
    sleep 3
done

log_step "Checking AI service..."
if curl -s --max-time 5 http://localhost:20128/v1/models > /dev/null 2>&1; then
    log_info "AI service is accessible at localhost:20128"
else
    log_warn "AI service not accessible at localhost:20128"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ INSTALLATION COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Access from THIS device:"
echo "   Frontend: http://localhost:5188"
echo "   Backend:  http://localhost:8016/api/v1"
echo ""
echo "🌐 Access from OTHER devices on same network:"
echo "   Frontend: http://$HOST_IP:5188"
echo "   Backend:  http://$HOST_IP:8016/api/v1"
echo ""
echo "💾 Database: localhost:5447"
echo ""
echo "🔑 Default Credentials:"
echo "   Email: admin@mauekspor.example"
echo "   Password: admin123"
echo ""
echo "📊 Useful Commands:"
echo "   make dev-status     # Check service status"
echo "   make dev-logs       # View all logs"
echo "   make dev-down       # Stop all services"
echo "   make dev-network    # Show network access URLs"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
