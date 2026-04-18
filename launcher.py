#!/usr/bin/env python3
"""
Launcher untuk Jurnal Saham IHSG
Simple & Robust - No restart loops!
"""

import os
import sys
import time
import subprocess
import webbrowser
import signal
from pathlib import Path

# Global process
PROCESS = None

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global PROCESS
    print("\n\n👋 Shutting down...")
    if PROCESS:
        try:
            PROCESS.terminate()
            PROCESS.wait(timeout=2)
        except:
            try:
                PROCESS.kill()
            except:
                pass
    sys.exit(0)

def get_app_dir():
    """Get application directory"""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return str(Path(__file__).parent)

def start_streamlit_server():
    """Start Streamlit server"""
    app_dir = get_app_dir()
    app_file = os.path.join(app_dir, 'app.py')
    
    cmd = [
        sys.executable, '-m', 'streamlit', 'run',
        app_file,
        '--server.port=8503',
        '--server.address=localhost',
        '--logger.level=warning',
        '--client.showErrorDetails=false'
    ]
    
    return subprocess.Popen(cmd, cwd=app_dir)

def wait_for_server(max_retries=30):
    """Wait for server to be ready"""
    import socket
    
    for i in range(max_retries):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', 8503))
            sock.close()
            if result == 0:
                return True
        except:
            pass
        
        print(f"⏳ Waiting... ({i+1}/{max_retries})")
        time.sleep(1)
    
    return False

def main():
    """Main launcher - NO RESTART LOOP"""
    global PROCESS
    
    print("=" * 60)
    print("📊 Jurnal Saham IHSG")
    print("=" * 60)
    
    # Ctrl+C handler
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        print("\n🚀 Starting...")
        PROCESS = start_streamlit_server()
        
        if not wait_for_server():
            print("❌ Failed to start!")
            sys.exit(1)
        
        time.sleep(1)
        print("🌐 Opening browser...")
        webbrowser.open('http://localhost:8503')
        
        print("\n✨ Ready! http://localhost:8503")
        print("⚠️  Press Ctrl+C to stop\n")
        
        # Wait forever - NO RESTART!!
        PROCESS.wait()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

