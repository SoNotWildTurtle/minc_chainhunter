#!/bin/bash
# MINC - bin/github_scanners/ssrfmap/run.sh
# Entrypoint script for SSRFMap bug bounty scanner

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="${SCRIPT_DIR}/src"
VENV_DIR="${SCRIPT_DIR}/venv"
TOOL_SCRIPT="${REPO_DIR}/ssrfmap.py"
REQ_FILE="${REPO_DIR}/requirements.txt"

# Clone SSRFmap repository if missing
if [ ! -f "${TOOL_SCRIPT}" ]; then
    echo "[+] Cloning SSRFmap repository"
    git clone https://github.com/swisskyrepo/SSRFmap.git "${REPO_DIR}"
fi

# Setup Python venv if needed
if [ ! -d "${VENV_DIR}" ]; then
    python3 -m venv "${VENV_DIR}"
    "${VENV_DIR}/bin/pip" install -U pip wheel
    if [ -f "${REQ_FILE}" ]; then
        "${VENV_DIR}/bin/pip" install -r "${REQ_FILE}"
    fi
fi

# Run SSRFMap with passed arguments
source "${VENV_DIR}/bin/activate"
python3 "${TOOL_SCRIPT}" "$@"
deactivate
