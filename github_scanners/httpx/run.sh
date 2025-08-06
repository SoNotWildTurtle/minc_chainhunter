#!/bin/bash
# Wrapper for projectdiscovery/httpx
if [ "$SKIP_CLONE" = "1" ]; then
    echo "Skipping httpx execution"
    exit 0
fi
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="${SCRIPT_DIR}/src"
BIN="${REPO_DIR}/httpx"

if [ ! -d "${REPO_DIR}/.git" ]; then
    echo "[+] Cloning httpx repository"
    git clone https://github.com/projectdiscovery/httpx.git "${REPO_DIR}"
fi

if [ ! -x "${BIN}" ]; then
    echo "[+] Building httpx"
    (cd "${REPO_DIR}" && go build -o httpx ./cmd/httpx) || exit 1
fi

"${BIN}" "$@"
