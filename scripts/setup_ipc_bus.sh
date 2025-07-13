#!/bin/bash
# Simple helper to launch the analysis DB IPC server
set -e
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/.. && pwd )"
SOCKET="${MINC_DB_SOCKET:-/tmp/minc_db.sock}"
PYTHON="python3"
while [[ $# -gt 0 ]]; do
  case "$1" in
    -Socket)
      SOCKET="$2"; shift 2;;
    -Python)
      PYTHON="$2"; shift 2;;
    *) shift;;
  esac
done
DB_DIR="${BASE_DIR}/db_data"
mkdir -p "$DB_DIR"
"$PYTHON" -m analysis_db.db_init --db_dir "$DB_DIR" --socket "$SOCKET"
