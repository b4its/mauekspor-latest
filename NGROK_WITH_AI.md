# Ngrok with AI Service - Complete Setup Guide

## 🎯 Purpose

This guide helps you expose **both** your MauEkspor application AND the AI service to the public internet via ngrok, so that all users can access real AI responses (not mock data).

## ⚡ Quick Start

```bash
make ngrok-with-ai
```

This single command:
1. Starts production backend & frontend in Docker
2. Exposes AI service through ngrok tunnel
3. Configures everything automatically

## 📊 What You Get

### Before (Mock Responses Only)
```json
{
  "data": {"messages": [...]},
  "meta": {
    "ai_mode": "remote",
    "ai_health": "unhealthy/unreachable",
    "ai_fallback": true  ← Using MOCK responses
  }
}
```

### After (Real AI Responses)
```json
{
  "data": {"messages": [...real_generated_content...]},
  "meta": {
    "ai_mode": "remote",
    "ai_health": "healthy",
    "ai_fallback": false  ← REAL AI working!
  }
}
```

## 🔗 URLs

After running `make ngrok-with-ai`, you'll get two URLs:

| Service | URL | Purpose |
|---------|-----|---------|
| **App Frontend** | `https://YOUR-TUNNEL.ngrok-free.dev` | Access MauEkspor UI |
| **AI Public** | `https://AI-YOUR-TUNNEL.ngrok-free.dev` | Direct AI API access |

## 🧪 Testing

### Test AI Endpoint
```bash
curl https://YOUR-AI-TUNNEL.ngrok-free.dev/v1/models
```

Expected: List of available models ✅

### Test Chat
```bash
# Login
TOKEN=$(curl -s -X POST https://YOUR-TUNNEL.ngrok-free.dev/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@mauekspor.example","password":"admin123"}' \
  | jq -r '.meta.access_token')

# Send message to AI
curl -s -X POST https://YOUR-TUNNEL.ngrok-free.dev/api/v1/chat/test-message/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"Test AI response"}' | jq '.'
```

Expected: Real generated content ✅

## 🔧 How It Works

1. **Production Stack** (`ngrok-tunnel-start`)
   - Backend: Port 8015 (Docker) → nginx
   - Frontend: Port 3015 (Docker) → nginx
   - Nginx: Port 8080 → exposed via ngrok

2. **AI Tunnel** (new)
   - AI Service: localhost:20128 → exposed via separate ngrok tunnel
   - Gets different subdomain (e.g., `ai-yourtunnel.ngrok-free.dev`)

3. **Backend Configuration**
   - Detects AI public URL from environment
   - Routes AI requests to ngrok-exposed endpoint
   - No Docker networking issues!

## 🛠️ Manual Alternative

If you prefer manual setup:

```bash
# Terminal 1: Production stack
make ngrok-prod-up
make ngrok-tunnel-start

# Terminal 2: AI tunnel
ngrok http 20128 --authtoken YOUR_TOKEN --region ap

# Copy AI public URL and update .env
export MAUEKSPOR_AI_PUBLIC_URL=https://ai-your-url.ngrok-free.dev

# Restart backend to pick up new config
docker restart mauekspor-backend-prod
```

## ⚠️ Important Notes

### Free Tier Limitations
- Ngrok free tier expires after ~1-2 hours
- Session must be restarted manually
- Consider upgrading for stable URLs

### Rate Limits
- Free ngrok has connection limits
- Test before relying on it

### Security
- Never commit actual ngrok URLs to git
- Use `.env` override instead

## 🐛 Troubleshooting

### "AI unreachable" despite running ai tunnel

Check if AI service is accessible locally first:
```bash
curl http://localhost:20128/v1/models
```

If this fails → start your AI service (LocalAI, Ollama, etc.)

### Wrong URLs showing

Clear old tunnels:
```bash
pkill -f "ngrok"
make ngrok-prod-down
make ngrok-with-ai
```

### Backend still using mock

Verify environment variable:
```bash
docker exec mauekspor-backend-prod env | grep AI_BASE
```

Should show: `MAUEKSPOR_AI_BASE_URL=<your-ngrok-url>`

## 📝 Summary

**Use this when:**
- Developing with production deployment
- Need real AI access from any location
- Testing full-stack remotely

**Don't use this when:**
- Just developing locally (use `make backend-local`)
- Deploying to paid ngrok/tunnel service
- Production environments need guaranteed uptime

---

Last updated: 2026-08-24
