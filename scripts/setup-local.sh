#!/bin/bash
# ============================================
# MauEkspor Local Setup Script
# ============================================
# Ini akan menginstalasi semua dependencies untuk local development
# ============================================

set -e

echo "╔══════════════════════════════════════════════════╗"
echo "║  🚀 MauEkspor - Local Development Setup        ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Step 1: Check prerequisites
echo "📋 Checking prerequisites..."
echo ""

check_command() {
    if ! command -v "$1" &> /dev/null; then
        error "$1 not found! Please install it first."
    fi
}

check_command docker
check_command git

info "✅ Docker installed"
info "✅ Git installed"

# Optional checks
if ! command -v pnpm &> /dev/null; then
    warn "pnpm not found. You can install with: npm install -g pnpm"
else
    info "✅ pnpm installed"
fi

if ! command -v node &> /dev/null; then
    warn "Node.js not found"
else
    info "✅ Node.js installed: $(node --version)"
fi

echo ""
echo "🐳 Checking Docker Compose..."
if docker compose version &> /dev/null; then
    info "✅ Docker Compose installed"
else
    error "Docker Compose not installed!"
fi

# Step 2: Create environment file
echo ""
echo "📝 Creating .env.local configuration..."
if [ ! -f ".env.local" ]; then
    cp .env.local.example .env.local 2>/dev/null || true
    if [ ! -f ".env.local" ]; then
        cat > .env.local << 'EOF'
# MauEkspor Local Development Configuration
POSTGRES_USER=mauekspor
POSTGRES_PASSWORD=mauekspor
POSTGRES_DB=mauekspor
BACKEND_PORT=8016
FRONTEND_PORT=5188
DB_PORT=5447
MAUEKSPOR_SECRET_KEY=dev-secret-key-change-in-production
MAUEKSPOR_AI_MODE=remote
MAUEKSPOR_AI_API_KEY=sk-dede08aea594e222-upk4p8-5bfa2c54
MAUEKSPOR_AI_BASE_URL=http://localhost:20128/v1
MAUEKSPOR_AI_MODEL=qd/dmodel
MAUEKSPOR_CORS_ORIGINS='["http://localhost:5188","http://127.0.0.1:5188"]'
MAUEKSPOR_ENABLE_CSRF=0
MAUEKSPOR_COOKIE_SECURE=0
EOF
        info "Created .env.local from template"
    fi
fi

if [ -f ".env.local" ]; then
    info "✅ .env.local exists"
    grep "^POSTGRES_PASSWORD=" .env.local | cut -d= -f2-
fi

# Step 3: Verify AI service is running
echo ""
echo "🤖 Checking AI service (localhost:20128)..."
if curl -s http://localhost:20128/v1/models > /dev/null 2>&1; then
    info "✅ AI service is running at localhost:20128"
else
    warn "⚠️  AI service not responding at localhost:20128"
    echo ""
    echo "To run AI service, make sure your provider is running on port 20128"
    echo "Example commands depend on your AI provider:"
    echo "  ollama serve"
    echo "  llama.cpp server"
    echo "  or other AI inference server"
fi

# Step 4: Verify Makefiles exist
echo ""
echo "📄 Checking Makefiles..."
if [ -f "Makefile.dev" ]; then
    info "✅ Makefile.dev exists"
else
    warn "Makefile.dev not found"
fi

if [ -f "docker-compose.dev.yml" ]; then
    info "✅ docker-compose.dev.yml exists"
else
    warn "docker-compose.dev.yml not found"
fi

# Step 5: Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ SETUP COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo ""
echo "  1. Start everything:"
echo "     make dev-up"
echo ""
echo "  2. Access application:"
echo "     Frontend: http://localhost:5188"
echo "     Backend:  http://localhost:8016/api/v1"
echo ""
echo "  3. Login credentials:"
echo "     Email: admin@mauekspor.example"
echo "     Password: admin123"
echo ""
echo "  4. Check status:"
echo "     make dev-status"
echo ""
echo "  5. View logs:"
echo "     make dev-backend-logs"
echo ""
echo "See LOCAL_SETUP.md for detailed documentation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
