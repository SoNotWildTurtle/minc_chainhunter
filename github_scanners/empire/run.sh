#!/bin/bash
set -euo pipefail
REPO="https://github.com/BC-SECURITY/Empire.git"
DIR="$(dirname "$0")/src"
ACTION="${1:-install}"
if [ "$ACTION" = "install" ]; then
  if [ ! -d "$DIR/.git" ]; then
    git clone --depth 1 "$REPO" "$DIR"
  else
    echo "[*] Empire already installed"
  fi
  echo "Empire cloned to $DIR"
  exit 0
fi
if [ ! -d "$DIR" ]; then
  echo "Empire not installed. Run with 'install' first." >&2
  exit 1
fi
case "$ACTION" in
  server)
    echo "Start Empire server manually in $DIR" ;;
  client)
    echo "Use Empire client from $DIR" ;;
  *)
    echo "Unknown action" >&2; exit 1 ;;
esac
