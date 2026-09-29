#!/data/data/com.termux/files/usr/bin/bash
URL="http://127.0.0.1:8765/index.html?build=3200"
if command -v am >/dev/null 2>&1; then
  am start -a android.intent.action.VIEW -d "$URL" com.android.chrome >/dev/null 2>&1 && exit 0
fi
if command -v termux-open-url >/dev/null 2>&1; then
  termux-open-url "$URL"
else
  echo "Ouvre dans Chrome : $URL"
fi
