#!/bin/bash
set -euo pipefail
REPO="https://github.com/BishopFox/sliver.git"
DIR="$(dirname "$0")/src"
ACTION="${1:-install}"
if [ "$ACTION" = "install" ]; then
  if [ ! -d "$DIR/.git" ]; then
    git clone --depth 1 "$REPO" "$DIR"
  else
    echo "[*] sliver already installed"
  fi
  echo "sliver cloned to $DIR"
  exit 0
fi
if [ ! -d "$DIR" ]; then
  echo "sliver not installed. Run with 'install' first." >&2
  exit 1
fi
case "$ACTION" in
  server)
    echo "Start sliver server manually in $DIR" ;;
  client)
    echo "Run sliver client in $DIR" ;;
  *)
    echo "Unknown action" >&2; exit 1 ;;
esac
