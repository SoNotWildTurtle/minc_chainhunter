#!/bin/bash
# Wrapper for git-dumper
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="${SCRIPT_DIR}/src"
TOOL="${REPO_DIR}/git-dumper.py"

if [ ! -f "${TOOL}" ]; then
    echo "[+] Cloning git-dumper repository"
    git clone https://github.com/arthaud/git-dumper.git "${REPO_DIR}"
fi

python3 "${TOOL}" "$@"
