# 🔧 Ngrok Troubleshooting Guide - MauEkspor

## ❌ Problem: pip not found / installation failed

### Error Message:
```
❌ Installing pyngrok...
/usr/bin/python3: No module named pip
```

---

## ✅ Solutions (Choose One)

### Solution A: Install ngrok Binary (Recommended!) 🚀

**Fastest way - no Python dependency:**

```bash
# 1. Download ngrok
cd /tmp
wget https://bin.equinox.io/c/bNyj1mQVAI4d/ngrok-stable-linux-amd64.tgz

# 2. Extract
tar xzf ngrok-stable-linux-amd64.tgz

# 3. Move to PATH
sudo mv ngrok /usr/local/bin/

# 4. Verify
ngrok version
```

Then use it with Makefile:
```bash
make ngrok-prod
```

It will automatically detect and use the binary! ✅

---

### Solution B: Install pip then pyngrok

```bash
# 1. Install pip (breaks system packages - only for development)
python3 -m pip install --break-system-packages pip

# 2. Install pyngrok
pip3 install --break-system-packages pyngrok

# 3. Test
python3 -c "import ngrok; print('✅ ngrok ready')"
```

Then run:
```bash
make ngrok-prod
```

---

### Solution C: Use Virtual Environment (Best Practice)

```bash
# 1. Create venv
python3 -m venv ~/.venv-ngrok

# 2. Activate
source ~/.venv-ngrok/bin/activate

# 3. Install pip and ngrok
pip install pyngrok

# 4. Now run make with venv activated
source ~/.venv-ngrok/bin/activate && cd ~/programming/python/mauekspor && make ngrok-prod
```

---

### Solution D: Use Simple Shell Script (No Dependencies!)

Created a simple bash script that uses ngrok directly:

```bash
# Run this instead
bash start-ngrok-simple.sh
```

This script:
- ✅ Uses ngrok binary directly (no Python needed)
- ✅ Auto-installs if ngrok is available in PATH
- ✅ Multiple tunnels in one command

---

## 🎯 Quick Fix Right Now

If you want to get running immediately:

### Option 1: Install ngrok binary (5 minutes)
```bash
cd /tmp
wget https://bin.equinox.io/c/bNyj1mQVAI4d/ngrok-stable-linux-amd64.tgz
tar xzf ngrok-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

# Then use make normally
cd ~/programming/python/mauekspor
make ngrok-prod
```

### Option 2: Manual ngrok commands

```bash
# Terminal 1 - Backend
ngrok http 8016 --authtoken 3IGWSdWwxcOQkQcxP0BcRkfHa5m_3nMcbXKdN93eUqsM1Hxjf

# Terminal 2 - Frontend Dev
ngrok http 5189 --authtoken 3IGWSdWwxcOQkQcxP0BcRkfHa5m_3nMcbXKdN93eUqsM1Hxjf

# Terminal 3 - Frontend Prod  
ngrok http 3016 --authtoken 3IGWSdWwxcOQkQcxP0BcRkfHa5m_3nMcbXKdN93eUqsM1Hxjf
```

Each terminal will show you the public URL!

---

## 🔍 How Makefile Works Now

The Makefile now has multiple fallback options:

```makefile
# Priority order:
# 1. pyngrok Python module
# 2. ngrok binary (if available)
# 3. start-ngrok-simple.sh (fallback shell script)
```

When you run:
```bash
make ngrok-prod
```

It will:
1. Check if `pyngrok` Python module exists
2. If not, check if `ngrok` binary exists in PATH
3. If not, fall back to `start-ngrok-simple.sh`

---

## 💡 Recommendation

**Use Solution A** - Install ngrok binary because:
- ✅ No Python dependencies
- ✅ Works everywhere
- ✅ Faster startup
- ✅ More reliable than Python wrapper
- ✅ Easy to update later

---

## 📋 Command Reference

After installing ngrok:

| Command | What It Does |
|---------|-------------|
| `make ngrok-local` | Local dev + ngrok tunnels |
| `make ngrok-prod` | Production + ngrok tunnels |
| `make ngrok-all` | All tunnels at once |
| `make ngrok-stop` | Kill all ngrok processes |
| `bash start-ngrok-simple.sh` | Manual simple script |

---

## 🆘 Still Not Working?

Check these:

1. **Is ngrok installed?**
   ```bash
   which ngrok
   # Should show: /usr/local/bin/ngrok
   ```

2. **Is ngrok binary executable?**
   ```bash
   chmod +x $(which ngrok)
   ```

3. **Can you ping internet?**
   ```bash
   curl https://ngrok.com
   ```

4. **Is your token correct?**
   ```
   Token: 3IGWSdWwxcOQkQcxP0BcRkfHa5m_3nMcbXKdN93eUqsM1Hxjf
   ```

---

## ✨ You're Fixed!

After installing ngrok, just run:

```bash
cd ~/programming/python/mauekspor
make ngrok-prod
```

And you'll see your public URLs! 🎉
