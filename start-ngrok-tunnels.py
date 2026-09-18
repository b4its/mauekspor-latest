#!/usr/bin/env python3
"""
MauEkspor Ngrok Tunnel Runner
Quick start script for deploying MauEkspor via ngrok

Port mapping: old + 15 + 1 = new port
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

def start_ngrok_tunnel(service_name, port):
    """Start an ngrok tunnel in background"""
    
    # Check if pyngrok is installed
    try:
        import ngrok
    except ImportError:
        print(f"\n❌ Installing pyngrok...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "pyngrok"])
        import ngrok
    
    # Setup ngrok
    ngrok.set_auth_token(NGROK_TOKEN)
    
    print(f"\n🚀 Starting tunnel for {service_name} on port {port}...")
    
    # Create tunnel
    public_url = ngrok.connect(port)
    
    print(f"✅ Tunnel active!")
    print(f"   Public URL: {public_url}")
    print(f"   Local URL:  http://localhost:{port}")
    
    return public_url, port

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
    
    tunnels = {}
    
    # Start each tunnel
    for service, port in SERVICES.items():
        try:
            url, local_port = start_ngrok_tunnel(service, port)
            tunnels[service] = {"url": url, "port": local_port}
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
    
    print("\nExample frontend configuration (.env):")
    if "Backend API" in tunnels and "Frontend Development" in tunnels:
        bg_url = tunnels["Backend API"]["url"].replace("http://", "https://")
        print(f"   VITE_API_BASE_URL={bg_url}/api/v1")
    
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
