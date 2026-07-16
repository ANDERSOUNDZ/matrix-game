#!/usr/bin/env bash
# download-vendor.sh — Descarga dependencias frontend para offline total
set -euo pipefail

VENDOR_DIR="frontend/vendor"
MP_DIR="$VENDOR_DIR/mediapipe"
WASM_DIR="$MP_DIR/wasm"

mkdir -p "$VENDOR_DIR"/three \
         "$VENDOR_DIR"/socket.io \
         "$MP_DIR" \
         "$WASM_DIR"

log()  { echo "[$1/$TOTAL] $2"; }
curl_() { curl -sL --fail --retry 3 "$1" -o "$2"; }

TOTAL=9

# 1. Three.js 0.128.0
log 1 "Three.js 0.128.0"
curl_ "https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js" \
      "$VENDOR_DIR/three/three.min.js"

# 2. Socket.IO client 4.7.5
log 2 "Socket.IO client 4.7.5"
curl_ "https://cdn.socket.io/4.7.5/socket.io.min.js" \
      "$VENDOR_DIR/socket.io/socket.io.min.js"

# 3. MediaPipe Tasks Vision ESM
log 3 "MediaPipe Tasks Vision ESM"
curl_ "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.35/vision_bundle.mjs" \
      "$MP_DIR/vision_bundle.mjs"

# 4-5. MediaPipe Tasks Vision WASM
for f in vision_wasm_internal.js vision_wasm_internal.wasm; do
    case "$f" in
        *.js)   log 4 "MediaPipe WASM: $f" ;;
        *.wasm) log 5 "MediaPipe WASM: $f" ;;
    esac
    curl_ "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.35/wasm/$f" \
          "$WASM_DIR/$f"
done

# 6. Hand Landmarker model (~12 MB)
log 6 "Hand Landmarker model (~12 MB)"
curl_ "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task" \
      "$MP_DIR/hand_landmarker.task"

# 7-9. Google Fonts: Press Start 2P (usada en algunos estilos Matrix)
log 7 "Google Fonts CSS"
FONT_API="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap"
curl_ "$FONT_API" "/tmp/fonts-google.css"

log 8 "Google Fonts: descargando archivos"
urls=$(grep -oP 'url\(\K[^)]+' /tmp/fonts-google.css | sort -u || true)
for url in $urls; do
    filename=$(basename "$url" | sed 's/\?.*//')
    echo "  Font: $filename"
    curl_ "$url" "$VENDOR_DIR/fonts/$filename"
done

log 9 "Google Fonts: reescribiendo CSS con rutas locales"
mkdir -p "$VENDOR_DIR/fonts"
sed -E 's|url\(https://fonts\.gstatic\.com[^)]+/([^/)]+)\)|url(/vendor/fonts/\1)|g' \
    /tmp/fonts-google.css > "$VENDOR_DIR/fonts/fonts.css"

echo ""
echo "=== Descarga completa ==="
find "$VENDOR_DIR" -type f -exec ls -lh {} \; 2>/dev/null | awk '{print "  " $5 "  " $NF}' || true
