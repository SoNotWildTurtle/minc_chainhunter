#!/bin/bash
# Wrapper for hakluke/hakrawler
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="${SCRIPT_DIR}/src"
BIN="${REPO_DIR}/hakrawler"

if [ ! -d "${REPO_DIR}/.git" ]; then
    echo "[+] Cloning hakrawler repository"
    git clone https://github.com/hakluke/hakrawler.git "${REPO_DIR}"
fi

if [ ! -x "${BIN}" ]; then
    (cd "${REPO_DIR}" && go build -o hakrawler .)
fi

"${BIN}" "$@"
