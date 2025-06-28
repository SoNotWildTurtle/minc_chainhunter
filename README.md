# MINC ChainHunter

MINC ChainHunter is an experimental security toolkit featuring a CLI interface and modular architecture. Modules are loaded dynamically from `recon_modules/` and `vuln_modules/`.

## Usage

```
python3 cli/main.py                # interactive mode
python3 cli/main.py list           # list available modules
python3 cli/main.py run <module> [args]
```

Example modules include:

- `ping_sweep` – performs a simple ICMP ping to the supplied host.
- `sqli_scanner` – placeholder that always reports no vulnerabilities.
- `subfinder_scan` – enumerate subdomains using subfinder.
- `hakrawler_scan` – crawl a target site for links.
- `dirsearch_scan` – brute-force directories on a web server.
- `nuclei_scan` – run nuclei against a target.
- `ssrfmap_scan` – test for SSRF issues.
- `gitleaks_scan` – scan a repository for secrets.

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
- **subfinder** – subdomain enumeration
- **hakrawler** – site crawling and link discovery

Feel free to add additional tools by editing the script.

## Database and report generation

When a module returns a structured result, ChainHunter sends it over the IPC bus
to the sandboxed analysis database. Results are written to JSON files and, if an
OpenAI API key is configured, processed by ChatGPT for tagging and a short
summary. Reports are stored in `db_data/results.json`.

To generate a consolidated markdown report of all stored results, either run the
CLI command `python3 cli/main.py report` or send the `report` alias over the IPC
bus. Reports are written to the `reports/` directory by default.

You can launch the analysis database server with `scripts/setup_ipc_bus.sh`,
which starts the IPC service at the path specified by the `MINC_DB_SOCKET`
environment variable.

## Manager scripts

Each major directory includes a small manager script to list or run its components. For example:

```bash
python3 recon_modules/manager.py --list
python3 vuln_modules/manager.py run nuclei_scan https://example.com
```

These helpers make it easy to automate tasks with minimal commands.

## Developer notes

Development notes are stored in a compressed format inside `DEV_NOTES.dat`.
Use `dev_notes/notes_manager.py` to append or read entries. Every note
contains JSON metadata including an ID, timestamp, tags, personal flag,
compression algorithm and optional `context` reference IDs. Older notes are
automatically recompressed at higher levels (levels 8+ switch to LZMA for
better space usage). Viewing a note adjusts compression for all entries and
also decompresses any context notes so they are easy to read. Notes can be
filtered by tag.

```bash
python3 dev_notes/notes_manager.py --add "Reminder to revisit sandbox perms"
python3 dev_notes/notes_manager.py --add "personal thoughts" --tags personal
python3 dev_notes/notes_manager.py --add "follow up" --context 1 2
python3 dev_notes/notes_manager.py --show 3
python3 dev_notes/notes_manager.py --view 0 --radius 1
python3 dev_notes/notes_manager.py --show 5 --tag personal
```
Set `DEV_NOTES_PATH` to override the default notes file location when testing.
