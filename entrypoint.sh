#!/bin/busybox sh

start_wechat() {
    # Start WeChat in the background
    DISPLAY=:0 wechat --no-sandbox &
}

vncserver :0 -SecurityTypes None --localhost no -geometry 2560x1440 -depth 32 -dpi 192 --I-KNOW-THIS-IS-INSECURE
cd /app/
start_wechat
DISPLAY=:0 pdm run ./src/main.py &

while true; do
    # Check if WeChat is running
    if ! busybox ps -o comm | busybox grep -q "wechat" > /dev/null; then
      echo "WeChat is not running, starting WeChat..."
      start_wechat
    fi
    sleep 1
done