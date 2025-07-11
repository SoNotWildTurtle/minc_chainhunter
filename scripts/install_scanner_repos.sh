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
        if [ -n "$SKIP_CLONE" ]; then
            echo "[*] skipping clone $name"
            mkdir -p "$dest"
        else
            echo "[+] Cloning $name from $url"
            git clone "$url" "$dest"
        fi
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
install_repo theharvester https://github.com/laramies/theHarvester.git
install_repo amass https://github.com/owasp-amass/amass.git
install_repo masscan https://github.com/robertdavidgraham/masscan.git
install_repo nmap https://github.com/nmap/nmap.git
install_repo git_dumper https://github.com/arthaud/git-dumper.git
install_repo aquatone https://github.com/michenriksen/aquatone.git
install_repo xsstrike https://github.com/s0md3v/XSStrike.git
install_repo wpscan https://github.com/wpscanteam/wpscan.git
install_repo sqlmap https://github.com/sqlmapproject/sqlmap.git
install_repo mythic https://github.com/its-a-feature/Mythic.git

echo "[+] Scanner repositories installed"
