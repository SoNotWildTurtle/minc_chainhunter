#!/bin/bash
# Wrapper for dirsearch
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="${SCRIPT_DIR}/src"
VENV_DIR="${SCRIPT_DIR}/venv"
TOOL_SCRIPT="${REPO_DIR}/dirsearch.py"

if [ ! -f "${TOOL_SCRIPT}" ]; then
    echo "[+] Cloning dirsearch repository"
    git clone https://github.com/maurosoria/dirsearch.git "${REPO_DIR}"
fi

if [ ! -d "${VENV_DIR}" ]; then
    python3 -m venv "${VENV_DIR}"
    "${VENV_DIR}/bin/pip" install -U pip
    if [ -f "${REPO_DIR}/requirements.txt" ]; then
        "${VENV_DIR}/bin/pip" install -r "${REPO_DIR}/requirements.txt"
    fi
fi

source "${VENV_DIR}/bin/activate"
python3 "${TOOL_SCRIPT}" "$@"
deactivate
