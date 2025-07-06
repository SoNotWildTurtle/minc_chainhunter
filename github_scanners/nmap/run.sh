#!/bin/bash
# Wrapper for nmap
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="${SCRIPT_DIR}/src"
BIN="${REPO_DIR}/nmap"

if [ ! -d "${REPO_DIR}/.git" ]; then
    echo "[+] Cloning nmap repository"
    git clone https://github.com/nmap/nmap.git "${REPO_DIR}"
fi

if [ ! -x "${BIN}" ]; then
    echo "[+] Building nmap"
    (cd "${REPO_DIR}" && ./configure && make) || exit 1
fi

"${BIN}" "$@"
