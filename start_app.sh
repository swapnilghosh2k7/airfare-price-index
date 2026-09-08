#!/usr/bin/env bash
# AirFareX 1-Click Launcher for macOS / Linux

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "================================================================="
echo "   AIRFAREX — REAL-TIME AIRFARE PRICE INDEX FOR INDIA (APIx)"
echo "              MAC / LINUX LAUNCHER"
echo "================================================================="
echo ""

python3 start_app.py
