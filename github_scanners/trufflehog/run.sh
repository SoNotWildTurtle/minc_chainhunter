#!/bin/bash
# Wrapper for truffleHog
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${SCRIPT_DIR}/src"

if [ ! -d "${REPO_DIR}/.git" ]; then
    echo "[+] Cloning truffleHog repository"
    git clone https://github.com/trufflesecurity/trufflehog "${REPO_DIR}"
fi

TRUFFLE="${REPO_DIR}/trufflehog"

if [ ! -x "${TRUFFLE}" ]; then
    (cd "${REPO_DIR}" && pip install .)
    TRUFFLE="$(which trufflehog)"
fi

"${TRUFFLE}" "$@"
