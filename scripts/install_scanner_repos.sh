#!/bin/bash
# Install GitHub-based scanners required by ChainHunter
set -e
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/.. && pwd )"
SCANNER_DIR="${BASE_DIR}/github_scanners"

install_repo() {
    local name="$1"
    local url="$2"
    local dest="${SCANNER_DIR}/${name}/src"
    if [ ! -d "$dest/.git" ]; then
        echo "[+] Cloning $name from $url"
        git clone "$url" "$dest"
    else
        echo "[*] $name already installed"
    fi
}

install_repo gitleaks https://github.com/gitleaks/gitleaks.git
install_repo ssrfmap https://github.com/swisskyrepo/SSRFmap.git
install_repo nuclei https://github.com/projectdiscovery/nuclei.git
install_repo dirsearch https://github.com/maurosoria/dirsearch.git
install_repo subfinder https://github.com/projectdiscovery/subfinder.git
install_repo hakrawler https://github.com/hakluke/hakrawler.git
install_repo trufflehog https://github.com/trufflesecurity/trufflehog.git

echo "[+] Scanner repositories installed"
