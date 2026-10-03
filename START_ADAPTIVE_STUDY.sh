#!/data/data/com.termux/files/usr/bin/bash
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
APPDIR=""
if [ -f "$HERE/local_instance/app/index.html" ]; then APPDIR="$HERE/local_instance/app"; elif [ -f "$HERE/app/index.html" ]; then APPDIR="$HERE/app"; fi
if [ -z "$APPDIR" ]; then echo "ERREUR : app/index.html introuvable."; exit 2; fi
if ! command -v python >/dev/null 2>&1; then pkg update -y && pkg install -y python; fi
echo "=== Adaptive Study v3.25.2 — serveur local ==="
echo "Application : $APPDIR"
echo "http://127.0.0.1:8765/index.html?build=3252"
cd "$APPDIR" && python -m http.server 8765 --bind 127.0.0.1