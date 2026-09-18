# 🚀 MauEkspor - Complete Ngrok Installation Guide

## ❌ Current Problem
```bash
❌ ngrok not found in PATH
❌ pip3 not available
❌ make ngrok-prod failed
```

---

## ✅ Solution 1: Automated Installer (EASIEST!) ⭐

### Step 1: Run Auto-Installer Script
```bash
cd ~/programming/python/mauekspor
bash install-ngrok.sh
```

This script will:
- ✅ Download ngrok automatically
- ✅ Extract it
- ✅ Install to /usr/local/bin or ~/bin
- ✅ Verify installation worked
- ✅ Show you how to use it

**Result:** Ngrok installed and ready to use!

---

### Step 2: Use Makefile Commands
```bash
make ngrok-prod     # Production mode
make ngrok-local    # Local development mode
```

---

## ✅ Solution 2: Manual Installation (If Auto Fails)

### Option A: Using curl/wget (Linux)

```bash
# Step 1: Download
cd /tmp
curl -LO https://bin.equinox.io/c/bNyj1mQVAI4d/ngrok-stable-linux-amd64.tgz
# OR
wget https://bin.equinox.io/c/bNyj1mQVAI4d/ngrok-stable-linux-amd64.tgz

# Step 2: Extract
tar xzf ngrok-stable-linux-amd64.tgz

# Step 3: Install to system (requires sudo)
sudo mv ngrok /usr/local/bin/
chmod +x /usr/local/bin/ngrok

# Step 4: Verify
ngrok version
```

---

### Option B: Install to Home Directory (No sudo needed)

```bash
# Step 1: Create bin directory
mkdir -p ~/bin

# Step 2: Download and extract
cd /tmp
tar xzf ngrok-stable-linux-amd64.tgz

# Step 3: Copy to home
cp ngrok ~/bin/
chmod +x ~/bin/ngrok

# Step 4: Add to PATH (in ~/.bashrc)
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Step 5: Verify
ngrok version
```

---

## ✅ Solution 3: Alternative Python Method (Only if pip works)

### Check if pip is available:
```bash
python3 -c "import pip; print('pip available')"
```

### If pip exists:
```bash
# Install pyngrok
pip3 install --break-system-packages pyngrok

# Now use make commands
make ngrok-prod
```

### If pip doesn't exist:
- Try installing python3-pip package manager first
- Or use Solution 1 or 2 (binary method)

---

## 🔧 After Installation

### Test Ngrok Works:

```bash
# Test command
ngrok http 8016 --log stdout
```

This should show:
- Connection established
- Public URL generated (like https://abc123.ngrok-free.app)
- Forwarding information

Press Ctrl+C to stop.

---

### Use with MauEkspor:

```bash
cd ~/programming/python/mauekspor

# Start your services first
make local          # Backend & Frontend on localhost

# In another terminal, start ngrok
make ngrok-prod     # Gets public URLs
```

You'll see output like:
```
✅ Tunnel active!
   Public URL: https://abc123.ngrok-free.app
   Local URL:  http://localhost:8016
```

---

## 💡 Recommended Installation Order

1. **First:** Try automated installer
   ```bash
   bash install-ngrok.sh
   ```

2. **If fails:** Try manual download (Solution 2)

3. **Alternative:** Install pip first, then use pyngrok (Solution 3)

---

## 📋 What Gets Installed

After successful installation, you'll have:
- ✅ ngrok binary executable
- ✅ Authentication token configured
- ✅ Ready to use with Makefile commands

**Ngrok Token Already Set:**
```
3IGWSdWwxcOQkQcxP0BcRkfHa5m_3nMcbXKdN93eUqsM1Hxjf
```

---

## 🎯 Quick Reference

| Command | Purpose |
|---------|---------|
| `bash install-ngrok.sh` | Auto-install ngrok |
| `make ngrok-prod` | Production deployment |
| `make ngrok-local` | Local dev with tunnels |
| `make ngrok-stop` | Kill all tunnels |

---

## ⚠️ Important Notes

1. **Requires Network Access:** Must be able to download from bin.equinox.io

2. **Sudo May Be Needed:** For system-wide installation (/usr/local/bin)

3. **Free Tier Limitations:** 
   - URLs change every restart
   - Reconnects every 24 hours
   - Bandwidth limits apply

4. **Token is Configured:** The provided token is already set in scripts

---

## ✨ Success Checklist

After installation, verify:

- [ ] `ngrok version` shows output
- [ ] `which ngrok` returns path
- [ ] Can run: `ngrok http 8016` without errors
- [ ] `make ngrok-prod` runs without "ngrok not found" error

If all checked: **CONGRATULATIONS!** 🎉

Your ngrok is installed and ready to go!

---

## 🆘 Troubleshooting

### Problem: "Permission denied" when moving ngrok
```bash
# Solution: Use home directory instead
cp ngrok ~/bin/
export PATH="$HOME/bin:$PATH"
```

### Problem: Download fails
```bash
# Check internet connection
ping -c 3 bin.equinox.io

# Try alternative mirror or manual download
# Visit: https://ngrok.com/download
```

### Problem: "command not found" after installation
```bash
# Source your shell config
source ~/.bashrc

# Or close and reopen terminal
```

---

## 🎉 You're All Set!

Once ngrok is installed, just run:

```bash
cd ~/programming/python/mauekspor
make ngrok-prod
```

And get your public deployment URLs instantly! 🚀
