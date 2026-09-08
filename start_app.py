#!/usr/bin/env python3
"""
AirFareX Universal Cross-Platform Launcher (Windows, macOS, Linux, Mobile LAN)
Detects local IP, initializes database & index, launches FastAPI backend and Vite frontend.
"""

import os
import sys
import socket
import subprocess
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

def get_local_ip():
    """Detects local LAN IP address for mobile/other device connectivity"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def print_banner(local_ip):
    print("=" * 70)
    print("    AIRFAREX — REAL-TIME AIRFARE PRICE INDEX FOR INDIA (APIx)")
    print("              UNIVERSAL MULTI-DEVICE LAUNCHER")
    print("=" * 70)
    print(f"  [+] Local Machine Access : http://localhost:5173")
    print(f"  [+] Mobile / Wi-Fi Access : http://{local_ip}:5173")
    print(f"  [+] REST API OpenAPI Docs: http://{local_ip}:8000/docs")
    print("-" * 70)
    print("  Connect any Mobile Phone, Tablet, or PC on your Wi-Fi network!")
    print("=" * 70 + "\n")

def initialize_data_if_needed():
    print("[AirFareX System Check] Verifying database & sample data...")
    db_file = PROJECT_ROOT / "airfarex.db"
    csv_file = PROJECT_ROOT / "data" / "sample" / "fare_quotes.csv"
    
    python_cmd = sys.executable

    if not csv_file.exists():
        print("[AirFareX System Check] Generating 30-day real-time dataset...")
        subprocess.run([python_cmd, "scripts/generate_demo_data.py", "--days", "30", "--seed", "42"], check=True)

    if not db_file.exists():
        print("[AirFareX System Check] Initializing SQLite database...")
        subprocess.run([python_cmd, "scripts/load_demo_data.py"], check=True)
        print("[AirFareX System Check] Building Airfare Price Index (APIX_v1)...")
        subprocess.run([python_cmd, "scripts/build_index.py"], check=True)

def main():
    local_ip = get_local_ip()
    print_banner(local_ip)
    
    initialize_data_if_needed()

    python_cmd = sys.executable
    frontend_dir = PROJECT_ROOT / "frontend"

    print("\n[AirFareX Startup] Launching FastAPI Backend on 0.0.0.0:8000...")
    backend_proc = subprocess.Popen([python_cmd, "backend/main.py"], cwd=PROJECT_ROOT)

    time.sleep(2)

    print("[AirFareX Startup] Launching Vite Frontend Server on 0.0.0.0:5173...")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    frontend_proc = subprocess.Popen([npm_cmd, "run", "dev", "--", "--host", "0.0.0.0"], cwd=frontend_dir)

    print("\n[AirFareX Active] All services running! Press CTRL+C to stop all servers.\n")

    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\n[AirFareX Shutdown] Stopping all server processes...")
        backend_proc.terminate()
        frontend_proc.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()
