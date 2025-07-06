#!/bin/bash
# Simple helper to launch the analysis DB IPC server
set -e
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/.. && pwd )"
SOCKET="${MINC_DB_SOCKET:-/tmp/minc_db.sock}"
DB_DIR="${BASE_DIR}/db_data"
mkdir -p "$DB_DIR"
python3 -m analysis_db.db_init --db_dir "$DB_DIR" --socket "$SOCKET"
