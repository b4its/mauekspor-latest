# 🚀 MauEkspor - Quick Ngrok Setup (EASY GUIDE!)

## ⏱️ Time: 5 minutes | Difficulty: Easy ⭐⭐

---

## 📋 What You Need to Do:

### Step 1: Download ngrok (2 minutes) 🔽

```bash
1. Open your web browser
2. Go to: https://ngrok.com/download
3. Click "Download" for Linux
4. Save file to ~/Downloads/
   (File name: ngrok-stable-linux-amd64.zip)
```

✅ Check download size should be ~3-7 MB

---

### Step 2: Install ngrok (1 minute) 🔧

Open terminal and run these commands:

```bash
cd ~/Downloads

# Extract the zip
unzip ngrok*.zip

# Install system-wide (requires sudo password)
sudo mv ngrok /usr/local/bin/

# Verify installation
ngrok version
```

Expected output:
```
Ngrok
Version: 4.x.x
...
```

If you see version info → **SUCCESS!** ✅

---

### Step 3: Deploy MauEkspor (2 minutes) 🎯

Open TWO terminals:

**Terminal 1:** Start local services
```bash
cd ~/programming/python/mauekspor
make local
```

**Terminal 2:** Expose to internet
```bash
cd ~/programming/python/mauekspor
bash start-ngrok-deploy.sh
```

Or use Makefile command:
```bash
make ngrok-prod
```

That's it! You'll get public URLs like:
```
Backend API: https://abc123.ngrok-free.app/api/v1
Frontend:    https://def456.ngrok-free.app
```

---

## 📁 Files Created For You

All in `/home/xmitsu/programming/python/mauekspor/`:

1. ✅ `INSTALL_NGROK_BROWSERS.md` - Complete manual install guide
2. ✅ `start-ngrok-deploy.sh` - One-click deployment script
3. ✅ All other scripts from earlier

Just follow the steps above!

---

## 💡 Pro Tips

### If you don't have `unzip`:
```bash
sudo apt-get update && sudo apt-get install -y unzip
```

### If sudo fails permission error:
Use home directory instead:
```bash
mkdir -p ~/bin
cp ngrok ~/bin/
chmod +x ~/bin/ngrok
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Want Cloudflare Tunnel instead?
```bash
sudo apt-get install cloudflared
cloudflared tunnel --url http://localhost:8015
```

Free public URL without downloading ngrok!

---

## ✨ Success Checklist

After installation, verify:

- [ ] File downloaded (~5-7 MB zip)
- [ ] Unzipped successfully
- [ ] `ngrok version` shows output
- [ ] Can run test: `ngrok http 8016 --log stdout`

If all checked → **YOU'RE READY!** 🎉

---

## 🆘 Common Issues

| Problem | Solution |
|---------|----------|
| Browser auto-downloads HTML | Use "Save Link As" option |
| unzip not found | Install: `sudo apt install unzip` |
| Permission denied | Try: `sudo mv ngrok /usr/local/bin/` |
| Command not found | Run: `source ~/.bashrc` |
| Download too small (<1MB) | Retry from different browser |

---

## 🎯 TL;DR Summary

```bash
# 1. Download from browser: https://ngrok.com/download
# 2. Install: 
cd ~/Downloads && \
unzip ngrok*.zip && \
sudo mv ngrok /usr/local/bin/

# 3. Test:
ngrok version

# 4. Deploy:
cd ~/programming/python/mauekspor && \
make local & make ngrok-prod
```

Done! Public URLs ready in seconds! 🚀
