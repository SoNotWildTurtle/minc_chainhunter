#!/bin/bash
# Wrapper for WPScan
if [ "$SKIP_CLONE" = "1" ]; then
    echo "Skipping wpscan execution"
    exit 0
fi
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="${SCRIPT_DIR}/src"
BIN="${REPO_DIR}/wpscan.rb"

if [ ! -d "${REPO_DIR}/.git" ]; then
    echo "[+] Cloning wpscan repository"
    git clone https://github.com/wpscanteam/wpscan.git "${REPO_DIR}"
fi

if [ ! -f "${BIN}" ]; then
    echo "[+] Installing wpscan dependencies"
    (cd "${REPO_DIR}" && bundle install) || exit 1
fi

ruby "${BIN}" "$@"
