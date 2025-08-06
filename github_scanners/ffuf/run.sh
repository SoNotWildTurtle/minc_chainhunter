#!/bin/bash
# Wrapper script for ffuf web fuzzer
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${SCRIPT_DIR}/src"
if [ ! -d "${REPO_DIR}/.git" ]; then
    if [ -n "$SKIP_CLONE" ]; then
        mkdir -p "${REPO_DIR}"
    else
        git clone https://github.com/ffuf/ffuf.git "${REPO_DIR}"
    fi
fi
if command -v ffuf >/dev/null 2>&1; then
    BIN=$(command -v ffuf)
else
    BIN="${REPO_DIR}/ffuf"
    if [ ! -x "$BIN" ]; then
        echo "[!] ffuf binary not found" >&2
        exit 1
    fi
fi
"$BIN" "$@"
