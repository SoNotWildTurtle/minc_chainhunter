#!/bin/bash
# Wrapper script for THC Hydra
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${SCRIPT_DIR}/src"
if [ ! -d "${REPO_DIR}/.git" ]; then
    if [ -n "$SKIP_CLONE" ]; then
        mkdir -p "${REPO_DIR}"
    else
        git clone https://github.com/vanhauser-thc/thc-hydra.git "${REPO_DIR}"
    fi
fi
if command -v hydra >/dev/null 2>&1; then
    BIN=$(command -v hydra)
else
    BIN="${REPO_DIR}/hydra"
    if [ ! -x "$BIN" ]; then
        echo "[!] hydra binary not found" >&2
        exit 1
    fi
fi
"$BIN" "$@"
