#!/bin/bash
# Wrapper for sullo/nikto
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="${SCRIPT_DIR}/src"

if [ ! -d "${REPO_DIR}/.git" ]; then
    echo "[+] Cloning nikto repository"
    git clone https://github.com/sullo/nikto.git "${REPO_DIR}"
fi

perl "${REPO_DIR}/program/nikto.pl" "$@"
