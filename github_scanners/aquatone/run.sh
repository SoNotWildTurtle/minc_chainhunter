#!/bin/bash
# Wrapper for aquatone
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="${SCRIPT_DIR}/src"
BIN="${SCRIPT_DIR}/aquatone"

if [ ! -d "${REPO_DIR}/.git" ]; then
    echo "[+] Cloning aquatone repository"
    git clone https://github.com/michenriksen/aquatone.git "${REPO_DIR}"
fi

if [ ! -x "${BIN}" ]; then
    if command -v go >/dev/null 2>&1; then
        echo "[+] Building aquatone"
        pushd "${REPO_DIR}" >/dev/null
        go build -o "${BIN}"
        popd >/dev/null
    else
        echo "[-] Go not installed; cannot build aquatone" >&2
        exit 1
    fi
fi

DOMAIN="$1"
OUTDIR="$2"
if [ -z "$OUTDIR" ]; then
    OUTDIR="aquatone_out"
fi

echo "$DOMAIN" | "$BIN" -out "$OUTDIR"
