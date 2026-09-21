#!/bin/bash
# scripts/tunnel-stop.sh — Hentikan semua tunnel (ngrok + cloudflared)
pkill -f "ngrok http"   2>/dev/null && echo "✅ ngrok dihentikan" || echo "ℹ️  ngrok tidak berjalan"
pkill -f "ngrok start"  2>/dev/null || true
pkill -f "cloudflared"  2>/dev/null && echo "✅ cloudflared (AI tunnel) dihentikan" || true
pkill -f "tunnel-monitor" 2>/dev/null || true
exit 0
