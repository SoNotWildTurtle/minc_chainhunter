# Install GitHub-based scanners for ChainHunter on Windows
param(
    [string]$RepoDir = (Join-Path $PSScriptRoot "..\github_scanners")
)
function Install-Repo($name, $url) {
    $dest = Join-Path $RepoDir "$name/src"
    if (-not (Test-Path "$dest/.git")) {
        if ($env:SKIP_CLONE) {
            Write-Host "[*] skipping clone $name"
            New-Item -ItemType Directory -Force -Path $dest | Out-Null
        } else {
            Write-Host "[+] Cloning $name from $url"
            git clone $url $dest
        }
    } else {
        Write-Host "[*] $name already installed"
    }
}

Install-Repo gitleaks https://github.com/gitleaks/gitleaks.git
Install-Repo ssrfmap https://github.com/swisskyrepo/SSRFmap.git
Install-Repo nuclei https://github.com/projectdiscovery/nuclei.git
Install-Repo dirsearch https://github.com/maurosoria/dirsearch.git
Install-Repo subfinder https://github.com/projectdiscovery/subfinder.git
Install-Repo hakrawler https://github.com/hakluke/hakrawler.git
Install-Repo trufflehog https://github.com/trufflesecurity/trufflehog.git
Install-Repo theharvester https://github.com/laramies/theHarvester.git
Install-Repo amass https://github.com/owasp-amass/amass.git
Install-Repo masscan https://github.com/robertdavidgraham/masscan.git
Install-Repo nmap https://github.com/nmap/nmap.git
Install-Repo git_dumper https://github.com/arthaud/git-dumper.git
Install-Repo aquatone https://github.com/michenriksen/aquatone.git
Install-Repo xsstrike https://github.com/s0md3v/XSStrike.git
Install-Repo wpscan https://github.com/wpscanteam/wpscan.git
Install-Repo sqlmap https://github.com/sqlmapproject/sqlmap.git
Install-Repo mythic https://github.com/its-a-feature/Mythic.git
Install-Repo sliver https://github.com/BishopFox/sliver.git
Install-Repo empire https://github.com/BC-SECURITY/Empire.git
Install-Repo covenant https://github.com/cobbr/Covenant.git
Write-Host "[+] Scanner repositories installed"
