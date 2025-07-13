#!/bin/bash
# Wrapper for owasp-amass/amass
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="${SCRIPT_DIR}/src"
BIN="${REPO_DIR}/amass"

if [ ! -d "${REPO_DIR}/.git" ]; then
    echo "[+] Cloning amass repository"
    git clone https://github.com/owasp-amass/amass.git "${REPO_DIR}"
fi

if [ ! -x "${BIN}" ]; then
    (cd "${REPO_DIR}" && go build -o amass ./cmd/amass)
fi

"${BIN}" "$@"
