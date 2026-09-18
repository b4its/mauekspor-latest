# 🚀 MauEkspor Quick Start Guide - Separated Docker

## ✅ What Changed

### Before ❌
```bash
docker-compose.yml        # ONE file for everything
docker compose up         # Might conflict with local services
```

### Now ✅
```bash
docker-compose.local.yml  # For local development
docker-compose.prod.yml   # For production (Docker containers)
```

---

## 🎯 Choose Your Mode

### 1️⃣ Local Development Mode
```bash
# Everything runs on your localhost (no containers)
make local

# Backend API: http://localhost:8016
# Frontend Dev: http://localhost:5188
```

**Best for:** Development with hot reload, debugging

---

### 2️⃣ Production Mode
```bash
# Everything runs in Docker containers
make prod

# Backend API: http://localhost:8016
# Frontend Prod: http://localhost:3015
```

**Best for:** Testing, deployment, staging

---

## 📋 Complete Command Reference

### Startup Commands

```bash
# LOCAL MODE (Development)
make local              # Backend + Frontend on localhost
START_DB=true make local   # + Database container

# PRODUCTION MODE (Docker)
make docker-build       # Build Docker images first
make prod               # Start all containers
make docker-down        # Stop containers
```

---

### Ngrok Tunnels

```bash
# With LOCAL mode
make ngrok-local    # Exposes localhost services to internet

# With PRODUCTION mode  
make ngrok-prod     # Exposes containerized services

# Stop tunnels
make ngrok-stop
```

---

### Database Operations

```bash
make seed           # Initial data setup
make reseed         # Reset & re-seed (asks confirmation)
make db-clean       # Remove database file
```

---

## 🔍 Status & Monitoring

```bash
make status         # Check what's running (local & docker)
make logs           # View production container logs
make logs-backend   # Backend only
make logs-frontend  # Frontend only
```

---

## 💡 Common Workflows

### Workflow A: Fresh Development
```bash
make setup          # Install dependencies + seed database
make local          # Start development server
# Open browser → http://localhost:5188
```

---

### Workflow B: Code Changes
```bash
make stop           # Stop servers
# Edit code...
make local          # Restart (hot reload works in frontend)
```

---

### Workflow C: Production Testing
```bash
make docker-build   # Build fresh images
make prod           # Start containers
make ngrok-prod     # Get public URLs
# Share URL or test from different device
```

---

### Workflow D: Full Reset
```bash
make distclean      # Remove everything
make setup          # Fresh install
make local          # Start development
```

---

## ⚠️ IMPORTANT: Don't Mix Modes!

### ❌ WRONG - Will cause conflicts:
```bash
# This tries to run BOTH local AND production at once!
docker compose -f docker-compose.local.yml up
docker compose -f docker-compose.prod.yml up
# Result: PORT CONFLICTS! 🚫
```

### ✅ CORRECT - Use one mode at a time:

**For Development:**
```bash
# Option 1: Pure local (recommended)
make local

# Option 2: Local + DB in container
START_DB=true make local

# Option 3: Add ngrok
make local && make ngrok-local
```

**For Production:**
```bash
# Full stack in containers
make prod

# Or with public URL
make prod && make ngrok-prod
```

---

## 🐳 Docker Files Explained

### docker-compose.local.yml
```yaml
Purpose: Optional database ONLY
Runs: Database container (optional)
Does NOT run: Backend, Frontend (you run them locally)

Usage:
  START_DB=true make local    # Starts DB container
  docker compose -f docker-compose.local.yml --profile local up -d db
```

**Why separate?**
- Local backend/frontend need direct file access for hot reload
- Database can be in container if needed
- No port conflicts with existing host services

---

### docker-compose.prod.yml
```yaml
Purpose: Full production environment
Runs: Database + Backend + Frontend (all containers)
Uses: network_mode: host for backend

Usage:
  make prod
  docker compose -f docker-compose.prod.yml --profile production up -d
```

**Why containerized?**
- Complete isolation
- Consistent across environments
- Easier deployment to production

---

## 🎛️ Port Configuration Summary

All ports updated to **(old_port + 15)**:

| Service | Local Port | Production Port | Description |
|---------|-----------|----------------|-------------|
| Backend API | 8016 | 8016 | FastAPI backend |
| Frontend Dev | 5188 | N/A | Vite dev server |
| Frontend Prod | N/A | 3015 | Production build |
| PostgreSQL | Optional 5447 | 5447 | Database |

**Ngrok Public URLs:** Generated dynamically when you run `make ngrok-*`

---

## 🔧 Troubleshooting

### "Port 8016 already in use"
```bash
pkill -f uvicorn
make local
```

### "Port 5188 already in use"
```bash
pkill -f pnpm
make local
```

### "Container won't start"
```bash
make docker-down          # Stop old containers
make docker-build         # Rebuild images
make prod                 # Start fresh
```

### "Can't connect to database"
```bash
# Check if DB is running
make status

# If not, start it:
docker compose -f docker-compose.local.yml --profile local up -d db
# OR
docker compose -f docker-compose.prod.yml --profile production up -d db
```

---

## 📁 File Structure

```
/home/xmitsu/programming/python/mauekspor/
├── docker-compose.local.yml   ← NEW! Local dev config
├── docker-compose.prod.yml    ← NEW! Production config
├── docker-compose.yml         ← Original (kept for reference)
├── Makefile                   ← UPDATED
└── [other project files]
```

---

## ✨ You're Ready!

Just pick your workflow and go:

```bash
# DEVELOPMENT
make setup
make local

# OR PRODUCTION
make docker-build
make prod
```

Everything is now properly separated with NO port conflicts! 🎉
