#!/bin/bash
# Utility to run common maintenance scripts
DIR="$(cd "$(dirname "$0")" && pwd)"

case "$1" in
  install)
    "$DIR/install_scanner_repos.sh" ;;
  setup_ipc)
    "$DIR/setup_ipc_bus.sh" ;;
  *)
    echo "Usage: $0 {install|setup_ipc}"
    exit 1
    ;;
esac
