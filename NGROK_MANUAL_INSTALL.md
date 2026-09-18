# 🚀 MauEkspor - Manual Ngrok Installation (Alternative)

## ❌ Why Automated Script Failed?

```bash
❌ Download URL returned wrong file format
❌ Not a valid gzip/zip archive
✅ This happens when:
   - Network issue during download
   - CDN redirect failed
   - Firewall blocked download
```

---

## ✅ Solution: Manual Installation Steps

### Option 1: Direct Browser Download (Easiest!) 🌐

**Step 1: Download via Browser**

1. Go to: https://ngrok.com/download
2. Click "Download" for **Linux x86-64**
3. Save to Downloads folder

**Step 2: Extract & Install**

```bash
cd ~/Downloads

# Extract (usually downloads as .zip or .tar.gz)
unzip ngrok-*-linux-amd64.zip
# OR
tar xzf ngrok-*-linux-amd64.tar.gz

# Move to PATH
sudo mv ngrok /usr/local/bin/

# Verify
ngrok version
```

That's it! Done in 2 minutes! ⚡

---

### Option 2: Command Line Download (More Control)

#### Method A: Using Official S3 Bucket

```bash
# Create temp directory
mkdir -p ~/tmp-ngrok && cd ~/tmp-ngrok

# Download from AWS S3 (more reliable)
curl -L -o ngrok.zip https://ngrok-agent.s3.amazonaws.com/ngrok.zip

# Extract
unzip ngrok.zip

# Install
sudo mv ngrok /usr/local/bin/
chmod +x /usr/local/bin/ngrok

# Verify
ngrok version

# Clean up
rm -rf ~/tmp-ngrok
```

#### Method B: Using GitHub Releases (If S3 fails)

```bash
# Create temp directory
mkdir -p ~/tmp-ngrok && cd ~/tmp-ngrok

# Download from GitHub mirror
wget https://github.com/grantustin/ngrok/releases/download/v4.2.1/ngrok-v4.2.1-linux-amd64.zip

# Extract
unzip ngrok-v4.2.1-linux-amd64.zip

# Install
sudo mv ngrok /usr/local/bin/
chmod +x /usr/local/bin/ngrok

# Verify
ngrok version

# Clean up
rm -rf ~/tmp-ngrok
```

---

### Option 3: Without sudo (User-only Installation)

```bash
# Create bin directory if it doesn't exist
mkdir -p ~/bin

# Download and extract to ~/bin
cd ~/Downloads
unzip ngrok*.zip -d ~/bin/

# Add to PATH in ~/.bashrc
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify
ngrok version
```

---

## 🔧 After Installation

### Test Ngrok Works:

```bash
# Quick test
ngrok http 8080 --log stdout

# Should show connection established and public URL
# Press Ctrl+C to stop
```

### Use with MauEkspor:

```bash
# Start your services first (in Terminal 1)
cd ~/programming/python/mauekspor
make local

# Start ngrok tunnels (in Terminal 2)
make ngrok-prod
```

You'll see output like:
```
✅ Tunnel active!
   Public URL: https://abc123.ngrok-free.app
   Local URL:  http://localhost:8016
```

---

## 💡 Alternative: Use ngrok Binary Without Makefile

If you want full control, use ngrok directly:

```bash
# Terminal 1 - Backend API
ngrok http 8016 \
  --authtoken 3IGWSdWwxcOQkQcxP0BcRkfHa5m_3nMcbXKdN93eUqsM1Hxjf

# Terminal 2 - Frontend Dev
ngrok http 5189 \
  --authtoken 3IGWSdWwxcOQkQcxP0BcRkfHa5m_3nMcbXKdN93eUqsM1Hxjf

# Terminal 3 - Frontend Prod  
ngrok http 3016 \
  --authtoken 3IGWSdWwxcOQkQcxP0BcRkfHa5m_3nMcbXKdN93eUqsM1Hxjf
```

Each terminal will show you the public URL immediately!

---

## ⚠️ Troubleshooting

### Problem: No permissions to install
```bash
# Instead of /usr/local/bin, use ~/bin
mkdir -p ~/bin
cp ngrok ~/bin/
chmod +x ~/bin/ngrok
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Problem: Cannot connect to download server
```bash
# Try alternative mirrors
# Official: https://ngrok.com/download
# GitHub mirror: https://github.com/grantustin/ngrok/releases
```

### Problem: File already exists error
```bash
# Remove old file first
sudo rm /usr/local/bin/ngrok

# Or move to different location
sudo mv ngrok /usr/local/bin/ngrok-v4
```

---

## 📊 Summary of Options

| Method | Difficulty | Time | Sudo Needed |
|--------|-----------|------|-------------|
| Browser download | Easy | 2 min | Yes |
| curl (AWS S3) | Medium | 3 min | Yes |
| wget (GitHub) | Medium | 3 min | Yes |
| User install only | Easy | 4 min | No |
| Manual ngrok | Flexible | 5+ min | Depends |

---

## ✨ Recommended Approach

**For most users:** Use **Option 1** (Browser download)
- Simplest
- Fastest
- Most reliable

**For developers/automation:** Use **Method A** (curl AWS S3)
- Scriptable
- Consistent
- Reliable

---

## 🎯 Success Checklist

After installing, verify:

- [ ] `ngrok version` shows output
- [ ] Can run: `ngrok http 8016 --log stdout`
- [ ] Get public URL without errors
- [ ] `make ngrok-prod` works

If all checked: **CONGRATULATIONS!** 🎉

Your ngrok is ready to deploy MauEkspor publicly!

---

## 🆘 Still Having Issues?

Try these:

1. **Check internet connection:**
   ```bash
   ping -c 3 ngrok.com
   ```

2. **Check firewall:**
   ```bash
   # May need to allow outbound connections to ngrok.com
   ```

3. **Use Python pyngrok instead:**
   ```bash
   pip3 install pyngrok  # If pip available
   python3 start-ngrok-tunnels.py
   ```

4. **Contact support:**
   - Visit: https://ngrok.com/support
   - Check: https://ngrok.com/docs

---

Choose the method that works best for your environment! 🚀
