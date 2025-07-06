#!/bin/bash
# Wrapper to run XSStrike
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ ! -f "$BASE_DIR/src/xsstrike.py" ]; then
    echo "[+] Cloning XSStrike"
    git clone https://github.com/s0md3v/XSStrike "$BASE_DIR/src"
fi
python3 "$BASE_DIR/src/xsstrike.py" "$@"
