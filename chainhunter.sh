#!/bin/bash
# Entry point for ChainHunter on Linux
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$SCRIPT_DIR/venv"
PY="$VENV/bin/python"
if [ ! -x "$PY" ]; then
  python3 -m venv "$VENV"
  "$SCRIPT_DIR/scripts/install_scanner_repos.sh"
fi
"$PY" "$SCRIPT_DIR/scripts/install_requirements.py"
SOCKET="${MINC_DB_SOCKET:-/tmp/minc_db.sock}"
bash "$SCRIPT_DIR/scripts/setup_ipc_bus.sh" -Socket "$SOCKET" -Python "$PY" &
BUS_PID=$!
trap "kill $BUS_PID" EXIT
sleep 1
"$PY" "$SCRIPT_DIR/cli/main.py" "$@"
