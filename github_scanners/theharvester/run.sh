#!/bin/bash
# Wrapper for laramies/theHarvester
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="${SCRIPT_DIR}/src"
VENV_DIR="${SCRIPT_DIR}/venv"
TOOL_SCRIPT="${REPO_DIR}/theHarvester.py"
REQ_FILE="${REPO_DIR}/requirements/base.txt"

if [ ! -f "${TOOL_SCRIPT}" ]; then
    echo "[+] Cloning theHarvester repository"
    git clone https://github.com/laramies/theHarvester.git "${REPO_DIR}"
fi

if [ ! -d "${VENV_DIR}" ]; then
    python3 -m venv "${VENV_DIR}"
    "${VENV_DIR}/bin/pip" install -U pip wheel
    if [ -f "${REQ_FILE}" ]; then
        "${VENV_DIR}/bin/pip" install -r "${REQ_FILE}"
    fi
fi

source "${VENV_DIR}/bin/activate"
python3 "${TOOL_SCRIPT}" "$@"
deactivate
