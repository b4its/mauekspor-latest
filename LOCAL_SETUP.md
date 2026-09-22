# MauEkspor Local Development Setup Guide
# ============================================
# Cara menjalankan aplikasi secara lokal dengan REAL AI
# ============================================

## 🎯 PREREQUISITES

Pastikan kamu sudah install:
- Docker & Docker Compose
- Python 3.12+
- Node.js 20+ (untuk frontend)
- pnpm (`npm install -g pnpm`)
- AI Service running di localhost:20128

## 🚀 QUICK START (Complete Local Setup)

### 1️⃣ Step 1: Setup Environment Variables

```bash
# Copy environment template (jika belum ada)
cp .env.local .env.local
```

File `.env.local` sudah berisi konfigurasi default yang aman untuk development.

### 2️⃣ Step 2: Start Semua Services

```bash
# Mulai database, backend, dan frontend
make dev-up
```

Ini akan:
- ✅ Pull Docker images yang dibutuhkan
- ✅ Build backend & frontend containers
- ✅ Start PostgreSQL database
- ✅ Start backend API di port 8016
- ✅ Start frontend dev server di port 5188
- ✅ Auto seed database dengan admin account

### 3️⃣ Step 3: Access Aplikasi

Buka browser dan akses:

**Frontend:** http://localhost:5188  
**Backend API:** http://localhost:8016/api/v1  
**Database:** localhost:5447

**Login credentials:**
- Email: `admin@mauekspor.example`
- Password: `admin123`

## 📊 STATUS & MONITORING

### Check Status
```bash
make dev-status
```

### View Logs
```bash
# Backend logs only
make dev-backend-logs

# Frontend logs only
make dev-frontend-logs

# Database logs
make dev-db-logs
```

### Health Check Manual
```bash
# Backend health
curl http://localhost:8016/api/v1/health

# AI connectivity check
curl http://localhost:20128/v1/models
```

## 🔧 INDIVIDUAL SERVICES

### Start/Stop Specific Services

```bash
# Database
make dev-db-start      # Start only database
make dev-db-stop       # Stop database
make dev-db-seed       # Reset & seed database

# Backend API
make dev-backend-start     # Start backend
make dev-backend-stop      # Stop backend
make dev-backend-shell     # Open shell in backend container

# Frontend
make dev-frontend-start    # Start frontend
make dev-frontend-stop     # Stop frontend
```

### Restart All
```bash
make dev-restart
```

## 🧪 TESTING

### Run Tests
```bash
# Backend tests
make test-backend

# Frontend tests
make test-frontend

# All tests
make test
```

## ⚡ DEVELOPMENT WORKFLOW

### Hot Reload (Docker Volumes)

File changes akan auto-reload berkat volume mounting:
- Backend: `./backend:/app:delegated`
- Frontend: `./frontend:/app:delegated`

### AI Service Integration

Aplikasi menggunakan REAL AI service via:
- URL: `http://localhost:20128/v1`
- Model: `qd/dmodel`
- Mode: `remote` (bukan mock!)

Pastikan AI service running di localhost:20128:
```bash
make check-ai
```

### Database Operations

Reset database (HAPUS SEMUA DATA):
```bash
make dev-db-reset
make dev-up          # Akan rebuild fresh database
```

Seed ulang data:
```bash
make dev-db-seed
```

## 🛠️ TROUBLESHOOTING

### Port Conflicts

Jika ada error "port already in use":
```bash
# Find process using port
lsof -i :8016
lsof -i :5188
lsof -i :5447

# Kill process
kill -9 <PID>

# Or use different ports in .env.local
BACKEND_PORT=8017
FRONTEND_PORT=5189
DB_PORT=5448
```

### Container Won't Start

Check logs:
```bash
docker compose -p mauekspor-dev -f docker-compose.dev.yml ps
docker logs mauekspor-dev-backend-dev
docker logs mauekspor-dev-frontend-dev
```

Rebuild from scratch:
```bash
make dev-down
make clean
make dev-up --build
```

### AI Not Working

Test AI connectivity:
```bash
curl http://localhost:20128/v1/models \
  -H "Authorization: Bearer sk-dede08aea594e222-upk4p8-5bfa2c54"
```

If AI service is down:
1. Check if AI service is running at localhost:20128
2. Restart your AI provider service
3. Verify API key in `.env.local`

### CORS Issues

Add new origin to `MAUEKSPOR_CORS_ORIGINS` in `.env.local`:
```bash
MAUEKSPOR_CORS_ORIGINS='["http://localhost:5188","http://localhost:3000", ...]'
```

Then restart backend:
```bash
make dev-restart
```

## 📝 FILE STRUCTURE

```
~/programming/mauekspor/
├── .env.local              # Local development config (gitignore)
├── docker-compose.dev.yml  # Local dev Docker Compose
├── Makefile.dev           # Local development commands
├── backend/
│   ├── Dockerfile.dev     # Backend Dockerfile (local mode)
│   └── app/               # FastAPI application
├── frontend/
│   ├── Dockerfile.dev     # Frontend Dockerfile (local mode)
│   └── src/              # SvelteKit application
└── scripts/             # Helper scripts
```

## 🔄 MIGRATION TO PRODUCTION

When ready to deploy to production:

```bash
# Stop local dev
make dev-down

# Build production images
make ngrok-prod-build

# Start production stack
make ngrok-prod-up
```

See `README.md` or `NGROK_GUIDE.md` for production setup details.

## 💡 TIPS

1. **Use .env.local not .env** - Keep production secrets safe
2. **Hot reload works!** - Edit code and refresh browser
3. **AI requires authentication** - Use valid API key in .env.local
4. **Default admin user** - auto-created on first startup
5. **Data persistence** - DB stored in Docker volume, won't be deleted

## 🆘 COMMON ISSUES

### Issue: Backend won't connect to database
**Solution:** Wait until DB shows "healthy" status, then restart backend

### Issue: Frontend shows "Cannot GET /"
**Solution:** Make sure frontend dev server is running, check logs

### Issue: AI responses are slow
**Solution:** This depends on your AI service performance locally

### Issue: Database connection refused
**Solution:** 
```bash
make dev-db-start
sleep 10  # Wait for database to be ready
```

## 🎉 SUCCESS CHECKLIST

✅ `make dev-up` completed without errors  
✅ Frontend accessible at http://localhost:5188  
✅ Backend responding at http://localhost:8016/api/v1/health  
✅ Database healthy on port 5447  
✅ Can login with admin credentials  
✅ AI service responding at localhost:20128  

Selamat mengembangkan aplikasi! 🚀
