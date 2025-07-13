#!/bin/bash
set -euo pipefail
REPO="https://github.com/cobbr/Covenant.git"
DIR="$(dirname "$0")/src"
ACTION="${1:-install}"
if [ "$ACTION" = "install" ]; then
  if [ ! -d "$DIR/.git" ]; then
    git clone --depth 1 "$REPO" "$DIR"
  else
    echo "[*] Covenant already installed"
  fi
  echo "Covenant cloned to $DIR"
  exit 0
fi
if [ ! -d "$DIR" ]; then
  echo "Covenant not installed. Run with 'install' first." >&2
  exit 1
fi
case "$ACTION" in
  start)
    echo "Start Covenant manually in $DIR" ;;
  stop)
    echo "Stop Covenant manually" ;;
  *)
    echo "Unknown action" >&2; exit 1 ;;
esac
