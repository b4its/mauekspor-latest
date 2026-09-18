#!/usr/bin/env python3
"""
MauEkspor Ngrok Tunnel Runner
Quick start script for deploying MauEkspor via ngrok

Port mapping: old + 16
- Backend: 8016 (8000 + 16)
- Frontend Dev: 5189 (5173 + 16)
- Frontend Prod: 3016 (3000 + 16)
"""

import subprocess
import sys
import time
from threading import Thread

# Your ngrok authentication token
NGROK_TOKEN = "3IGWSdWwxcOQkQcxP0BcRkfHa5m_3nMcbXKdN93eUqsM1Hxjf"

# Services and their ports (old + 16)
SERVICES = {
    "Backend API": 8016,
    "Frontend Development": 5189,
    "Frontend Production": 3016,
}

def check_ngrok_installed():
    """Check if pyngrok is installed"""
    try:
        import ngrok
        return True
    except ImportError:
        return False

def check_ngrok_binary():
    """Check if ngrok binary exists"""
    result = subprocess.run(
        ['which', 'ngrok'],
        capture_output=True,
        text=True
    )
    return result.returncode == 0

def install_pyngrok():
    """Install pyngrok package"""
    print(f"\n📦 Installing pyngrok...")
    
    # Try with --break-system-packages flag
    cmd = [sys.executable, '-m', 'pip', 'install', '--quiet', 
           '--break-system-packages', 'pyngrok']
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"⚠️  Warning: pip installation failed")
        print(f"   Error: {result.stderr}")
        return False
    
    print("✅ pyngrok installed successfully")
    return True

def main():
    print("=" * 70)
    print("🌍 MauEkspor Deployment - Ngrok Tunnels")
    print("=" * 70)
    print(f"\nAuthentication Token: {NGROK_TOKEN[:24]}...")
    print(f"\nPorts being tunneled:")
    
    for service, port in SERVICES.items():
        print(f"  • {service:<25} localhost:{port}")
    
    print("\n" + "=" * 70)
    print("Starting all tunnels...")
    print("=" * 70 + "\n")
    
    # Check if pyngrok is already installed
    if not check_ngrok_installed():
        print("⚠️  pyngrok not found, installing...")
        if not install_pyngrok():
            print("\n❌ Failed to install pyngrok!")
            print("   Please run: pip3 install --break-system-packages pyngrok")
            print("   Or use: make ngrok-install-manual")
            sys.exit(1)
    
    # Import after installation
    try:
        from pyngrok import ngrok
    except ImportError as e:
        print(f"\n❌ Cannot import ngrok module: {e}")
        print("   Make sure pyngrok is properly installed")
        sys.exit(1)
    
    # Setup ngrok
    ngrok.set_auth_token(NGROK_TOKEN)
    
    tunnels = {}
    
    # Start each tunnel
    for service, port in SERVICES.items():
        try:
            print(f"\n🚀 Starting tunnel for {service} on port {port}...")
            
            # Create tunnel
            public_url = ngrok.connect(port)
            
            tunnels[service] = {"url": public_url, "port": port}
            print(f"✅ Tunnel active!")
            print(f"   Public URL: {public_url}")
            print(f"   Local URL:  http://localhost:{port}")
            
        except Exception as e:
            print(f"\n❌ Error starting {service}: {e}")
            continue
        
        # Small delay between starts
        time.sleep(0.5)
    
    # Print summary
    print("\n" + "=" * 70)
    print("📋 Summary - Your Public URLs")
    print("=" * 70)
    
    for service, info in tunnels.items():
        status = "✅" if info["url"] else "❌"
        print(f"\n{status} {service}:")
        print(f"   🔗 Public: {info['url']}")
        print(f"   🔧 Local:  http://localhost:{info['port']}")
    
    print("\n" + "=" * 70)
    print("⚡ Next Steps:")
    print("=" * 70)
    print("\n1. Start your application backend/frontend")
    print("2. Update frontend config to use ngrok URLs")
    print("3. Test your deployment")
    
    print("\n" + "=" * 70)
    print("👉 Press Ctrl+C to stop all tunnels")
    print("=" * 70)
    
    # Keep script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down tunnels...")
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
