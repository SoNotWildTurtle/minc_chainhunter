#!/bin/bash
# MINC - bin/github_scanners/gitleaks/run.sh
# Entrypoint script for Gitleaks git secret scanner

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TOOL_BIN="${SCRIPT_DIR}/gitleaks"
REPO_DIR="${SCRIPT_DIR}/src"

# Clone Gitleaks repository if missing
if [ ! -d "${REPO_DIR}/.git" ]; then
    echo "[+] Cloning gitleaks repository"
    git clone https://github.com/gitleaks/gitleaks.git "${REPO_DIR}"
fi

# Download latest Gitleaks binary if not present
if [ ! -x "${TOOL_BIN}" ]; then
    echo "[+] Gitleaks not found, downloading latest release..."
    # You can pin a version if you want, or always get latest
    curl -sL https://github.com/gitleaks/gitleaks/releases/latest/download/gitleaks-linux-amd64 -o "${TOOL_BIN}"
    chmod +x "${TOOL_BIN}"
fi

# Pass through all arguments (repo path, scan options, etc)
"${TOOL_BIN}" "$@"
