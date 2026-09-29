#!/data/data/com.termux/files/usr/bin/bash
set -e

HERE="$(cd "$(dirname "$0")" && pwd)"

echo "=== Adaptive Study v3.20.0-original-pdfs — serveur local ==="
echo "Dossier détecté : $HERE"

# Locate the app folder robustly.
APPDIR=""
if [ -f "$HERE/local_instance/app/index.html" ]; then
  APPDIR="$HERE/local_instance/app"
elif [ -f "$HERE/app/index.html" ]; then
  APPDIR="$HERE/app"
elif [ -f "$HERE/AdaptiveStudyInstall/app/index.html" ]; then
  APPDIR="$HERE/AdaptiveStudyInstall/app"
else
  FOUND="$(find "$HERE" -maxdepth 3 -type f -path '*/app/index.html' 2>/dev/null | head -n 1 || true)"
  if [ -n "$FOUND" ]; then
    APPDIR="$(dirname "$FOUND")"
  fi
fi

if [ -z "$APPDIR" ]; then
  echo ""
  echo "ERREUR : impossible de trouver app/index.html."
  echo "Le ZIP doit être entièrement décompressé, pas seulement START_ADAPTIVE_STUDY.sh."
  echo ""
  echo "Contenu du dossier actuel :"
  ls -la "$HERE"
  exit 2
fi

if ! command -v python >/dev/null 2>&1; then
  echo ""
  echo "Python n'est pas installé. Installation..."
  pkg update -y
  pkg install -y python
fi

echo ""
echo "Application trouvée : $APPDIR"
echo "Serveur local : http://127.0.0.1:8765/index.html?build=3200"
echo "Build attendu : v3.20.0-original-pdfs"
echo ""
echo "Dans Chrome :"
echo "  1. Ouvre http://127.0.0.1:8765/"
echo "  2. Attends que le mode hors ligne soit prêt."
echo "  3. Menu ⋮ > Installer l'application."
echo ""
echo "Laisse Termux ouvert jusqu'à la fin de la première installation."
echo "Ctrl+C arrête le serveur."
echo ""

cd "$APPDIR"
python -m http.server 8765 --bind 127.0.0.1
