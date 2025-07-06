#!/bin/bash
# Wrapper for projectdiscovery/subfinder
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="${SCRIPT_DIR}/src"
BIN="${REPO_DIR}/subfinder"

if [ ! -d "${REPO_DIR}/.git" ]; then
    echo "[+] Cloning subfinder repository"
    git clone https://github.com/projectdiscovery/subfinder.git "${REPO_DIR}"
fi

if [ ! -x "${BIN}" ]; then
    (cd "${REPO_DIR}" && go build -o subfinder ./cmd/subfinder)
fi

"${BIN}" "$@"
