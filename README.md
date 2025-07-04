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
- `dirsearch_scan` – brute-force directories on a web server. Supports `--wordlist`,
  `--threads`, and `--extensions` to customize scans.
- `nuclei_scan` – run nuclei against a target. Accepts `--templates` and
  `--severity` filters.
- `ssrfmap_scan` – test for SSRF issues with adjustable parameter name via
  `--param` and optional POST data.
- `gitleaks_scan` – scan a repository for secrets with `--redact` and custom
  configuration via `--config`.
- `trufflehog_scan` – run truffleHog to detect secrets in repositories.
- `dns_lookup` – resolve DNS records for a domain.
- `theharvester_scan` – gather emails and subdomains with theHarvester.
- `amass_scan` – perform subdomain enumeration using Amass.
- `masscan_scan` – fast port scanning with masscan.
- `nmap_scan` – service enumeration using nmap.
- `xxe_scan` – placeholder XXE scanner using a custom payload.
- `bug_hunt` – run a simple pipeline combining `ping_sweep` and `sqli_scanner`
  with results saved through the CLI.
- `extended_hunt` – run several scanners (subfinder, hakrawler, dirsearch,
  nuclei, gitleaks, trufflehog) in sequence for deeper analysis.
- `repo_hunt` – scan a repository with gitleaks and trufflehog to uncover
  secrets.
- Modules automatically log results to the analysis database whenever the
  `MINC_DB_SOCKET` environment variable is set, so pipeline steps are stored
  alongside their summaries.

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
- **trufflehog** – secrets scanning via truffleHog
- **theHarvester** – OSINT gathering tool for emails and subdomains
- **amass** – advanced subdomain enumeration framework
- **masscan** – lightning-fast port scanner
- **nmap** – network scanner with scripting engine

Feel free to add additional tools by editing the script.

## Database and report generation

When a module returns a structured result, ChainHunter sends it over the IPC bus
to the sandboxed analysis database. Results are written to JSON files and, if an
OpenAI API key is configured, processed by ChatGPT for tagging and a short
summary. Reports are stored in `db_data/results.json`.
Modules run outside the CLI also perform this logging automatically whenever
`MINC_DB_SOCKET` is defined.

To generate a consolidated markdown report of all stored results, either run the
CLI command `python3 cli/main.py report` or send the `report` alias over the IPC
bus. Reports are written to the `reports/` directory by default. Use
`python3 cli/main.py results` to quickly display stored entries.

You can launch the analysis database server with `scripts/setup_ipc_bus.sh`,
which starts the IPC service at the path specified by the `MINC_DB_SOCKET`
environment variable. The server now drops privileges to the `nobody` user by
default when started through the sandbox scripts, ensuring results are written
with secure permissions.

## Manager scripts

Each major directory includes a small manager script to list or run its components. For example:

```bash
python3 recon_modules/manager.py --list
python3 vuln_modules/manager.py run nuclei_scan https://example.com
```

These helpers make it easy to automate tasks with minimal commands.

## Bug hunting pipelines

The `bug_hunt` pipeline demonstrates basic automation by running
`ping_sweep` followed by `sqli_scanner` and storing the aggregated result in the
analysis database:

```bash
python3 cli/main.py run bug_hunt 127.0.0.1
```

Use the normal `results` and `report` commands to view pipeline output.

`extended_hunt` chains a larger set of modules for deeper bug hunting:

```bash
python3 cli/main.py run extended_hunt https://example.com
```

This sequence performs subdomain discovery, crawling, directory brute force,
generic vulnerability scanning and secret detection before saving combined
results.

`repo_hunt` focuses on repository secrets detection using gitleaks and
trufflehog:

```bash
python3 cli/main.py run repo_hunt path/to/repo
```


## Self-update

Running `python3 cli/main.py update` performs a `git pull` in the ChainHunter
repository to fetch the latest changes. Pass `--force` to always pull even when
the local commit matches the remote. If the repository has no configured
upstream, the command exits without changes.

## Developer notes

Development notes are stored in a compressed format inside `DEV_NOTES.dat`.
Use `dev_notes/notes_manager.py` to append or read entries. Every note
contains JSON metadata including an ID, timestamp, tags, personal flag,
compression algorithm and optional `context` reference IDs. Older notes are
automatically recompressed at higher levels using an algorithmic RLE+zlib
scheme that scales with the distance from the viewed entry. Viewing a note
adjusts compression for all entries and
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
