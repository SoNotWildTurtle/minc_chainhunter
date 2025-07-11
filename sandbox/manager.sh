#!/bin/bash
# Helper to run sandbox components
DIR="$(cd "$(dirname "$0")" && pwd)"

case "$1" in
  run_db)
    "$DIR/db_env/run_db.sh" ;;
  run_main)
    "$DIR/main_app/run_main.sh" ;;
  debug)
    python3 "$DIR/debugger.py" "${@:2}" ;;
  *)
    echo "Usage: $0 {run_db|run_main|debug <script>}"
    exit 1
    ;;
esac
