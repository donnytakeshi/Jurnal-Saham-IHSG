#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/install_and_test.sh /path/to/app.apk com.example.package [device_serial]
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 /path/to/app.apk com.example.package [device_serial]" >&2
  exit 1
fi

APK_PATH="$1"
PKG_NAME="${2:-}"
DEVICE_ID="${3:-}"

ADB=adb
if [ -n "$DEVICE_ID" ]; then
  ADB="adb -s $DEVICE_ID"
fi

if [ ! -f "$APK_PATH" ]; then
  echo "APK not found: $APK_PATH"
  exit 2
fi

echo "Installing $APK_PATH to ${DEVICE_ID:-default device}..."
$ADB install -r "$APK_PATH"

if [ -n "$PKG_NAME" ]; then
  echo "Launching $PKG_NAME"
  $ADB shell monkey -p "$PKG_NAME" -c android.intent.category.LAUNCHER 1 || true
else
  echo "No package name provided; skipping launch step."
fi

LOGFILE="device_log_$(date +%Y%m%d_%H%M%S).log"
echo "Capturing logcat for 20s to $LOGFILE"
$ADB logcat -c || true
$ADB logcat -v time > "$LOGFILE" &
LOGPID=$!
sleep 20
kill "$LOGPID" || true
echo "Log saved: $LOGFILE"

echo "Done."
