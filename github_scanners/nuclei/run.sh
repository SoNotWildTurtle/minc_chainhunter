#!/bin/bash
# Wrapper for projectdiscovery/nuclei
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="${SCRIPT_DIR}/src"
NUCLEI_BIN="${REPO_DIR}/nuclei"

if [ ! -d "${REPO_DIR}/.git" ]; then
    echo "[+] Cloning nuclei repository"
    git clone https://github.com/projectdiscovery/nuclei.git "${REPO_DIR}"
fi

if [ ! -x "${NUCLEI_BIN}" ]; then
    (cd "${REPO_DIR}" && go build -o nuclei ./cmd/nuclei)
fi

"${NUCLEI_BIN}" "$@"
