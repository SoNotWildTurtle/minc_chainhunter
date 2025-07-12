#!/bin/bash
set -euo pipefail
REPO="https://github.com/sqlmapproject/sqlmap.git"
DIR="$(dirname "$0")/src"
if [ ! -d "$DIR" ]; then
  git clone --depth 1 "$REPO" "$DIR"
fi
python3 "$DIR/sqlmap.py" "$@"
