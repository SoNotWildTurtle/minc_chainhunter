#!/bin/bash
set -euo pipefail
REPO="https://github.com/its-a-feature/Mythic.git"
DIR="$(dirname "$0")/src"
ACTION="${1:-install}"
if [ "$ACTION" = "install" ]; then
  if [ ! -d "$DIR/.git" ]; then
    git clone --depth 1 "$REPO" "$DIR"
  else
    echo "[*] Mythic already installed"
  fi
  echo "Mythic cloned to $DIR"
  exit 0
fi
if [ ! -d "$DIR" ]; then
  echo "Mythic not installed. Run with 'install' first." >&2
  exit 1
fi
case "$ACTION" in
  start)
    echo "Start Mythic manually in $DIR with 'docker compose up -d'" ;;
  stop)
    echo "Stop Mythic with 'docker compose down' in $DIR" ;;
  *)
    echo "Unknown action" >&2; exit 1 ;;
esac
