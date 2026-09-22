# 🚀 MauEkspor - Run Locally dengan REAL AI

## Quick Start (30 seconds)

```bash
# 1. Clone repo (sudah kamu lakukan)
cd ~/programming/mauekspor

# 2. Setup environment (jika belum ada)
./scripts/setup-local.sh

# 3. Run everything!
make dev-up
```

Done! Aplikasi sudah running di lokal dengan REAL AI! 🎉

---

## URLs Setelah `make dev-up`

- **Frontend:** http://localhost:5188
- **Backend API:** http://localhost:8016/api/v1  
- **Database:** localhost:5447

## Login Credentials

- Email: `admin@mauekspor.example`
- Password: `admin123`

---

## Commands Lengkap

### Start & Stop
```bash
make dev-up          # Start semua services
make dev-down        # Stop semua services
make dev-restart     # Restart semua
```

### Status Check
```bash
make dev-status      # Lihat status semua containers
make check-ai        # Test AI connectivity
```

### Individual Services
```bash
# Database
make dev-db-start    # Start database saja
make dev-db-stop     # Stop database
make dev-db-seed     # Seed ulang database
make dev-db-reset    # Reset complete database

# Backend
make dev-backend-start   # Start backend API
make dev-backend-stop    # Stop backend
make dev-backend-logs    # View logs
make dev-backend-shell   # Open shell in container

# Frontend
make dev-frontend-start  # Start frontend dev server
make dev-frontend-stop   # Stop frontend
make dev-frontend-logs   # View logs
```

### Testing
```bash
make test-backend    # Run backend tests
make test-frontend   # Run frontend tests
make test            # All tests
```

### Cleanup
```bash
make clean           # Remove all containers and volumes
```

---

## Development Workflow

### Edit Code
File changes auto-reload karena volume mounting:
- ✅ Backend code changes → auto restart
- ✅ Frontend code changes → hot reload (Vite)

### Debug Backend
```bash
# Open bash in backend container
make dev-backend-shell

# Or just edit files directly
vi backend/app/main.py
# Then reload: make dev-restart
```

### Debug Frontend  
```bash
# Just open browser at http://localhost:5188
# Hot reload will work automatically
```

### Database Operations
```bash
# Reset database (WARNING: HAPUS DATA!)
make dev-db-reset

# Rebuild from scratch
make dev-down
make clean
make dev-up

# Manual SQL access
docker exec -it mauekspor-dev-db-dev psql -U mauekspor -d mauekspor
```

---

## Troubleshooting

### Port Already in Use
```bash
# Find what's using port 8016
lsof -i :8016

# Kill the process
kill -9 <PID>

# Or change port in .env.local
BACKEND_PORT=8017
```

### Container Won't Start
```bash
# Check logs
docker logs mauekspor-dev-backend-dev

# Rebuild
docker compose -p mauekspor-dev -f docker-compose.dev.yml build --no-cache
make dev-up
```

### AI Not Working
```bash
# Check if AI service is running
curl http://localhost:20128/v1/models

# If not running, start your AI provider first
# Example for Ollama:
ollama serve
```

### CORS Errors
Add new origin to `.env.local`:
```bash
MAUEKSPOR_CORS_ORIGINS='["http://localhost:5188", "http://localhost:3000", ...]'
```

Then: `make dev-restart`

---

## Architecture Overview

```
┌─────────────┐
│   Browser   │ ←── http://localhost:5188
└──────┬──────┘
       │
┌──────▼─────────┐
│   Nginx /      │ ←── Reverse proxy (optional)
│   Proxy Server │
└──────┬─────────┘
       │
┌──────▼──────────────────────────┐
│   Frontend (SvelteKit)          │
│   └── Runs on port 5188         │
│   └── Vite Dev Server           │
└──────┬──────────────────────────┘
       │
       │ API Calls
       │
┌──────▼──────────────────────────┐
│   Backend (FastAPI)             │
│   └── Runs on port 8016         │
│   └── Accesses DB via network   │
│   └── Accesses AI via host.docker.internal:20128
└──────┬──────────────────────────┘
       │
┌──────▼──────────────────────────┐
│   PostgreSQL                    │
│   └── Runs on port 5447         │
│   └── Data persisted in volume  │
└──────────────────────────────────┘
       
┌──────────────────────────────────┐
│   AI Service (Local)             │
│   └── Runs on port 20128         │
│   └── Accessed by backend        │
│   └── Real AI inference engine   │
└──────────────────────────────────┘
```

---

## Environment Variables

See `.env.local` for complete list. Key variables:

```bash
POSTGRES_USER=mauekspor
POSTGRES_PASSWORD=mauekspor
DB_PORT=5447          # Database port

BACKEND_PORT=8016     # Backend API port
FRONTEND_PORT=5188    # Frontend dev port

MAUEKSPOR_AI_MODE=remote       # Use real AI (not mock)
MAUEKSPOR_AI_BASE_URL=http://localhost:20128/v1
MAUEKSPOR_AI_API_KEY=sk-dede08aea594e222-upk4p8-5bfa2c54
```

Change any of these in `.env.local` then run `make dev-restart`.

---

## Production Deployment

When ready to deploy to production:

```bash
# Build production images
make ngrok-prod-build

# Start production stack
make ngrok-prod-up

# Or use full setup with AI tunnel
make ngrok-with-ai
```

---

## Additional Resources

- **Full Documentation:** See `LOCAL_SETUP.md`
- **Production Guide:** See `README.md` or `NGROK_GUIDE.md`
- **AI Integration:** See `AI_INTEGRATION_SUMMARY.md`

---

## Support

If you encounter issues:

1. Check `make dev-status` for health checks
2. Review logs: `make dev-backend-logs`
3. Try rebuilding: `make clean && make dev-up`
4. Consult `LOCAL_SETUP.md` troubleshooting section

---

Happy coding! 🎨🚀
