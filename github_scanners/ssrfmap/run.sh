#!/bin/bash
# MINC - bin/github_scanners/ssrfmap/run.sh
# Entrypoint script for SSRFMap bug bounty scanner

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="${SCRIPT_DIR}/venv"
TOOL_SCRIPT="${SCRIPT_DIR}/ssrfmap.py"

# Setup Python venv if needed
if [ ! -d "${VENV_DIR}" ]; then
    python3 -m venv "${VENV_DIR}"
    "${VENV_DIR}/bin/pip" install -U pip wheel
    "${VENV_DIR}/bin/pip" install -r "${SCRIPT_DIR}/requirements.txt"
fi

# Run SSRFMap with passed arguments
source "${VENV_DIR}/bin/activate"
python3 "${TOOL_SCRIPT}" "$@"
deactivate
