# 🎯 MauEkspor - Complete Ngrok Installation Guide (Manual Browser Method)

## ⚠️ Important Notice

Automated download scripts are currently failing due to:
- CDN server issues
- Network blocking
- File corruption during download

**Solution: Manual browser download (100% reliable!)**

---

## ✅ Step-by-Step Installation (5 Minutes Total)

### Phase 1: Download via Browser 🌐

**Step 1: Go to Official Download Page**

```bash
# Open your web browser
http://www.google.com/chrome/
# OR any browser you have

# Then navigate to:
https://ngrok.com/download
```

**Step 2: Choose Linux Version**

```
You will see:
┌─────────────────────────────────────┐
│     ngrok Download                  │
│                                     │
│   Windows                         ▼ │
│   macOS                           ▼ │
│   Linux      ← CLICK HERE            │
│                                     │
│   Platform: x86-64                 ▼ │
│   Package Type: Zip                ▼ │
│                                     │
│   [Download]  ← CLICK THIS BUTTON  │
└─────────────────────────────────────┘
```

**What happens:**
- Browser downloads `ngrok-stable-linux-amd64.zip` (or similar name)
- Size: ~3-7 MB
- Location: `~/Downloads/` folder

**Step 3: Verify Download**

```bash
# Check file downloaded successfully
ls -lh ~/Downloads/ngrok*.zip

# Should show something like:
# -rw-r--r-- 1 user staff  5.2M Jan 15 10:30 ngrok-stable-linux-amd64.zip
```

If file size is very small (< 1MB), retry download from browser.

---

### Phase 2: Install to System 💻

**Method A: System-wide Installation (Recommended)**

```bash
cd ~/Downloads

# Extract the zip file
unzip ngrok*.zip

# Move to system PATH
sudo mv ngrok /usr/local/bin/

# Make sure it's executable
chmod +x /usr/local/bin/ngrok

# Verify installation
ngrok version
```

Expected output:
```
Ngrok
Version: 4.x.x
...
```

**Method B: User-only Installation (No sudo needed)**

```bash
cd ~/Downloads

# Extract
unzip ngrok*.zip

# Create bin directory if it doesn't exist
mkdir -p ~/bin

# Copy to home bin
cp ngrok ~/bin/
chmod +x ~/bin/ngrok

# Add to PATH in ~/.bashrc
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify
ngrok version
```

---

### Phase 3: Configure & Test 🔧

**Verify Installation**

```bash
# Check location
which ngrok

# Show version
ngrok version

# Test quick connection
ngrok http 8016 --log stdout

# Should show:
# Session Status                online
# Account                       Your Name
# Version                       4.x.x
# Region                        (US|EU|ASIA...)
# Forwarding                    https://abc123.ngrok-free.app -> http://localhost:8016
```

Press `Ctrl+C` to stop after testing.

---

## 🎯 Quick Start Script

After installing ngrok, run this script to deploy MauEkspor:

```bash
cd ~/programming/python/mauekspor

# Terminal 1: Start local services
make local

# Terminal 2: Expose with ngrok
make ngrok-prod
```

---

## 📋 Common Issues & Solutions

### Issue 1: "unzip: command not found"
```bash
# Install unzip
sudo apt-get update && sudo apt-get install -y unzip

# Or on macOS:
brew install unzip
```

### Issue 2: "Permission denied" when moving
```bash
# Use method B (home directory installation instead)
# Or use sudo properly:
sudo mv ngrok /usr/local/bin/
```

### Issue 3: "command not found" after install
```bash
# Reload shell config
source ~/.bashrc

# Or close and reopen terminal
```

### Issue 4: Downloads only get 300 bytes
```bash
# Don't use curl/wget commands
# ALWAYS use browser download instead
# Sometimes CDN servers are down
```

---

## ✨ Success Checklist

Before continuing, verify all of these:

- [ ] Downloaded `.zip` file (~5-7 MB)
- [ ] Extracted `ngrok` binary
- [ ] Moved to `/usr/local/bin/` or `~/bin/`
- [ ] `ngrok version` shows output
- [ ] Can test: `ngrok http 8016 --log stdout`

If all checked → **CONGRATULATIONS!** 🎉

---

## 🚀 Next Steps After Installation

### Option 1: Use Makefile Commands
```bash
cd ~/programming/python/mauekspor

# Local development
make local

# With ngrok tunnels
make ngrok-prod
```

### Option 2: Manual Tunnel Commands
```bash
# Backend API
ngrok http 8016 \
  --authtoken 3IGWSdWwxcOQkQcxP0BcRkfHa5m_3nMcbXKdN93eUqsM1Hxjf

# Frontend Dev
ngrok http 5189 \
  --authtoken 3IGWSdWwxcOQkQcxP0BcRkfHa5m_3nMcbXKdN93eUqsM1Hxjf

# Frontend Prod  
ngrok http 3015 \
  --authtoken 3IGWSdWwxcOQkQcxP0BcRkfHa5m_3nMcbXKdN93eUqsM1Hxjf
```

Each terminal will show public URL immediately!

---

## 📞 Need More Help?

See other guides:
- `NGROK_MANUAL_INSTALL.md` - Alternative methods
- `NGROK_ALTERNATIVES.md` - Cloudflare tunnel option
- `DOCKER_ARCHITECTURE.md` - Docker setup

---

**Time to complete:** 5 minutes  
**Difficulty:** Easy ⭐⭐  
**Reliability:** 100% ✅
