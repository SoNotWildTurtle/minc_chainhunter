#!/bin/bash
# Wrapper for masscan
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="${SCRIPT_DIR}/src"
BIN="${REPO_DIR}/bin/masscan"

if [ ! -d "${REPO_DIR}/.git" ]; then
    echo "[+] Cloning masscan repository"
    git clone https://github.com/robertdavidgraham/masscan.git "${REPO_DIR}"
fi

if [ ! -x "${BIN}" ]; then
    echo "[+] Building masscan"
    (cd "${REPO_DIR}" && make) || exit 1
fi

"${BIN}" "$@"
