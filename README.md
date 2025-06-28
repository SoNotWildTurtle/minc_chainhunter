# MINC ChainHunter

MINC ChainHunter is an experimental security toolkit featuring a CLI interface and modular architecture. Modules are loaded dynamically from `recon_modules/` and `vuln_modules/`.

## Usage

```
python3 cli/main.py                # interactive mode
python3 cli/main.py list           # list available modules
python3 cli/main.py run <module> [args]
```

Two sample modules are provided:

- `ping_sweep` – performs a simple ICMP ping to the supplied host.
- `sqli_scanner` – placeholder that always reports no vulnerabilities.

The IPC bus components are under development. `bus_integrity.py` includes helper functions to verify socket permissions and approved command aliases.

## Installing GitHub scanners

The repository does not ship the full source of third-party scanners. Run
`scripts/install_scanner_repos.sh` after cloning ChainHunter to download the
required GitHub projects locally:

```bash
./scripts/install_scanner_repos.sh
```

This script clones the latest versions of several scanners under
`github_scanners/*/src` so the wrapper scripts can execute them. Currently the
following upstream tools are fetched:

- **gitleaks** – secrets scanning
- **SSRFmap** – SSRF testing
- **nuclei** – generalized vulnerability scanner
- **dirsearch** – web directory brute forcing

Feel free to add additional tools by editing the script.

## Database and report generation

When a module returns a structured result, ChainHunter sends it over the IPC bus
to the sandboxed analysis database. Results are written to JSON files and, if an
OpenAI API key is configured, processed by ChatGPT for tagging and a short
summary. Reports are stored in `db_data/results.json`.
