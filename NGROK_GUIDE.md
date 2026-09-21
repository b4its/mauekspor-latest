# Ngrok Tunnel Management Guide

## 🚨 Masalah ERR_NGROK_3200

**Error:** `ERR_NGROK_3200: The endpoint ... is offline`

**Root Cause:** Ngrok free tier sessions bersifat ephemeral - mereka mati otomatis setelah ~1-2 jam atau ketika proses ngrok mati karena alasan apapun (OOM, timeout, signal).

## 📐 Port Layout (Anti-Tabrakan)

| Service | Port | Keterangan |
|---------|------|-----------|
| `mauekspor-db-prod` | **5447** | PostgreSQL Docker |
| `mauekspor-backend-prod` | **8015** | FastAPI Docker |
| `mauekspor-frontend-prod` | **3015** | SvelteKit node Docker |
| `mauekspor-nginx-prod` | **8080** | Nginx reverse proxy → ngrok target |
| Dev backend (local) | **8016** | uvicorn `--port 8016` |
| Dev frontend (local) | **5188** | vite dev `--port 5188` → proxy ke 8016 |

## 🚀 Quick Start

### 1. Start Production Stack (sekali)
```bash
make ngrok-prod-up
```

Ini akan:
- Stop semua process dev lokal yang mungkin konflik port
- Start PostgreSQL, backend, frontend, nginx di Docker
- Verifikasi semua service healthy

### 2. Start Tunnel (pilih salah satu)

#### Option A: Simple Tunnel (mati setelah ~1-2 jam)
```bash
make ngrok-tunnel-start
```
- Ngrok jalan di background
- Auto-test frontend & API
- **⚠️ Akan mati otomatis setelah 1-2 jam**

#### Option B: Auto-Restart Watchdog (recommended)
```bash
make tunnel-keep-alive
```
- Watchdog jalan di terminal (Ctrl+C untuk stop)
- Cek tunnel setiap 30 detik
- **Auto-restart kalau tunnel mati**
- Survive shell disconnection (pakai setsid)

## 🛠️ Commands

### Production
```bash
make ngrok-prod-up      # Start production stack
make ngrok-prod-down    # Stop production stack
make ngrok-prod-status  # Lihat status containers
make ngrok-prod-logs    # Tail logs
make ngrok-prod-reseed  # Reset & reseed database
```

### Tunnel
```bash
make ngrok-tunnel-start   # Start tunnel (simple, mati 1-2 jam)
make tunnel-keep-alive    # Start watchdog (auto-restart)
make ngrok-tunnel-stop    # Stop tunnel & watchdog
make ngrok-show-urls      # Lihat public URL
```

### Development
```bash
make dev-backend    # Start backend di port 8016
make dev-frontend   # Start frontend di port 5188 (proxy ke 8016)
make dev-down       # Stop semua dev processes
```

### Testing
```bash
make test-backend   # Run backend pytest
make test-frontend  # Run frontend vitest
make test           # Run semua tests
```

## 🔧 Scripts

| Script | Fungsi |
|--------|--------|
| `scripts/prod-up.sh` | Start production stack dengan proper error handling |
| `scripts/tunnel-start.sh` | Start ngrok tunnel (simple, 1x run) |
| `scripts/tunnel-monitor.sh` | **Watchdog**: auto-restart kalau mati |
| `scripts/tunnel-stop.sh` | Stop ngrok safely |
| `scripts/dev.sh` | Start dev backend di port 8016 |

## 🧪 Testing Tunnel

```bash
# Test health endpoint
curl https://YOUR-TUNNEL.ngrok-free.dev/api/v1/health

# Test login
curl -X POST https://YOUR-TUNNEL.ngrok-free.dev/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@mauekspor.example","password":"admin123"}'

# Test API (butuh token)
TOKEN=$(curl -s -X POST https://YOUR-TUNNEL.ngrok-free.dev/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@mauekspor.example","password":"admin123"}' \
  | jq -r '.meta.access_token')

curl -H "Authorization: Bearer $TOKEN" \
  https://YOUR-TUNNEL.ngrok-free.dev/api/v1/products/
```

## 🐛 Troubleshooting

### ERR_NGROK_3200: Endpoint is offline

**Penyebab:** Tunnel sudah mati (ngrok process tidak jalan lagi)

**Solusi:**
```bash
# Option 1: Restart tunnel (simple)
make ngrok-tunnel-start

# Option 2: Restart dengan watchdog (recommended)
make tunnel-keep-alive
```

### Tunnel sering mati

**Penyebab:** Ngrok free tier punya limit session (~1-2 jam)

**Solusi:** Pakai watchdog:
```bash
make tunnel-keep-alive
```

Watchdog akan:
- Cek tunnel setiap 30 detik
- Auto-restart kalau mati
- Log semua aktivitas ke `/tmp/tunnel-monitor.log`

### Port 8015 already in use

**Penyebab:** Backend lokal masih jalan

**Solusi:**
```bash
# Kill backend lokal
make dev-down

# Atau manual
pkill -f "uvicorn.*app.main"

# Lalu start production
make ngrok-prod-up
```

### Docker container unhealthy

**Penyebab:** Backend/frontend tidak ready dalam waktu yang ditentukan

**Solusi:**
```bash
# Lihat logs container
docker logs mauekspor-backend-prod
docker logs mauekspor-frontend-prod

# Restart production stack
make ngrok-prod-down
make ngrok-prod-up
```

### Nginx 502 Bad Gateway

**Penyebab:** Backend container belum ready atau crash

**Solusi:**
```bash
# Cek backend status
make ngrok-prod-status

# Lihat backend logs
docker logs -f mauekspor-backend-prod

# Restart backend saja
docker restart mauekspor-backend-prod
```

## 📊 Monitoring

### Cek Tunnel Status
```bash
# Ngrok web UI
open http://localhost:4040

# Atau via API
curl http://127.0.0.1:4040/api/tunnels | jq

# Atau via make
make ngrok-show-urls
```

### Cek Watchdog Logs
```bash
# Real-time
tail -f /tmp/tunnel-monitor.log

# Last 50 lines
tail -50 /tmp/tunnel-monitor.log

# Search errors
grep -i error /tmp/tunnel-monitor.log
```

### Cek Production Logs
```bash
# Semua containers
make ngrok-prod-logs

# Specific container
docker logs -f mauekspor-backend-prod
docker logs -f mauekspor-frontend-prod
docker logs -f mauekspor-nginx-prod
```

## 🔄 Workflow Harian

### Development
```bash
# 1. Start production stack (kalau belum)
make ngrok-prod-up

# 2. Start tunnel dengan watchdog
make tunnel-keep-alive
# (tunnel akan auto-restart kalau mati)

# 3. Develop di terminal lain
# ...

# 4. Test via tunnel URL
# (URL ditampilkan saat tunnel-start)

# 5. Stop kalau selesai
# Ctrl+C di terminal tunnel-keep-alive
make ngrok-prod-down
```

### Production Deploy
```bash
# 1. Build images
make ngrok-prod-build

# 2. Start stack
make ngrok-prod-up

# 3. Start tunnel dengan watchdog
make tunnel-keep-alive
# (jalankan di tmux/screen agar survive logout)

# 4. Share tunnel URL ke client
make ngrok-show-urls
```

## 📝 Notes

- **Free Tier Limitations:**
  - Session mati otomatis setelah ~1-2 jam
  - URL berubah setiap restart (random subdomain)
  - Rate limited (5 connections/minute)
  - Ada ngrok splash screen di browser

- **Watchdog Benefits:**
  - Auto-restart saat tunnel mati
  - Survive shell disconnection (setsid)
  - Log semua restart attempts
  - Health check setiap 30 detik

- **Upgrade ke Paid Tier:**
  - Stable URL (custom subdomain)
  - Unlimited sessions
  - Higher rate limits
  - No splash screen
  - TCP/UDP tunneling (bukan cuma HTTP)

## 🔗 Resources

- [Ngrok Documentation](https://ngrok.com/docs)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

---

**Last Updated:** 2026-08-24  
**Maintainer:** b4its <exynosfam@gmail.com>
