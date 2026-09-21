#!/bin/bash
# scripts/tunnel-stop.sh — Hentikan ngrok tunnel
pkill -f "ngrok http" 2>/dev/null && echo "✅ Ngrok dihentikan" || echo "✅ Tidak ada ngrok yang berjalan"
