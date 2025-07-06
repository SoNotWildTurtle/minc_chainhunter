# MINC ChainHunter

MINC ChainHunter is an experimental security toolkit featuring a CLI interface and modular architecture. Modules are loaded dynamically from `recon_modules/` and `vuln_modules/`.

## Dependencies

Install the following Python packages:

- `numpy` and `scikit-learn` for the neural analyzer
- `cryptography` if you enable database encryption

```
pip install numpy scikit-learn cryptography
```


## Usage

```
python3 cli/main.py                # interactive mode
python3 cli/main.py list           # list available modules
python3 cli/main.py run <module> [args]
```

Example modules include:

- `ping_sweep` – performs a simple ICMP ping to the supplied host.
 - `sqli_scanner` – performs a basic SQL injection test using an HTTP request.
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
- `aquatone_scan` – screenshot discovered hosts with aquatone.
- `git_dumper_scan` – dump exposed `.git` directories.
 - `xxe_scan` – sends an XML payload to detect XXE vulnerabilities.
- `xsstrike_scan` – detect reflected XSS vulnerabilities using XSStrike.
- `bug_hunt` – run a simple pipeline combining `ping_sweep` and `sqli_scanner`
  with results saved through the CLI.
- `extended_hunt` – run several scanners (subfinder, hakrawler, dirsearch,
  nuclei, gitleaks, trufflehog) in sequence for deeper analysis.
- `repo_hunt` – scan a repository with gitleaks and trufflehog to uncover
  secrets.
- Modules automatically log results to the analysis database whenever the
  `MINC_DB_SOCKET` environment variable is set, so pipeline steps are stored
  alongside their summaries.
- Each stored entry also records a `vuln_count` value representing the total
  number of vulnerabilities found in that pipeline run.

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
- **git-dumper** – dump exposed git repositories
- **aquatone** – screenshotting tool for discovered hosts
- **XSStrike** – advanced XSS detection tool

Feel free to add additional tools by editing the script.

## Database and report generation

When a module returns a structured result, ChainHunter sends it over the IPC bus
to the sandboxed analysis database. Results are written to JSON files and, if an
OpenAI API key is configured, processed by ChatGPT for tagging and a short
summary. Reports are stored in `db_data/results.json`.
Set `MINC_IPC_SECRET` to require a shared secret for all IPC requests. Clients
automatically include this value and the server rejects requests with an
incorrect secret. You can also set `MINC_ENCRYPT_KEY` to a Fernet key to store
the database encrypted on disk. Generate a key with
`python -m cryptography.fernet.Fernet.generate_key`.
Modules run outside the CLI also perform this logging automatically whenever
`MINC_DB_SOCKET` is defined. Results are transparently decrypted when accessed
through the CLI or report generator.

To filter by tag, run `python3 cli/main.py results --tag <label>`.

To generate a consolidated markdown report of all stored results, either run the
CLI command `python3 cli/main.py report` or send the `report` alias over the IPC
bus. Reports are written to the `reports/` directory by default. Use
`python3 cli/main.py results` to quickly display stored entries.
Run `python3 cli/main.py purge --limit 50` to keep only the most recent 50
results if the database grows large.

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

`smart_hunt` automatically chooses the best pipeline based on past results using
the neural analyzer. It runs the recommended pipeline and logs the combined
output:

```bash
python3 cli/main.py run smart_hunt example.com
```

Set the `MINC_OVERRIDE_PIPELINE` environment variable to force a specific
pipeline when testing.

When the environment variable `MINC_AUTO_REPORT` is set, the CLI automatically
requests a report from the analysis database after any module finishes
executing. Use `MINC_AUTO_REPORT_DIR` to change the output directory (defaults to
`reports`).


## Self-update

Running `python3 cli/main.py update` performs a `git pull` in the ChainHunter
repository to fetch the latest changes. Pass `--force` to always pull even when
the local commit matches the remote. If the repository has no configured
upstream, the command exits without changes.

## Self-evolution

Use the `self-evolve` command to trigger Codex based upgrades. The command
reads the current goals and attempts to run Codex using your `OPENAI_API_KEY`.
If the key is missing, it simply reports that self-evolution was skipped.

```bash
python3 cli/main.py self-evolve [--target <host>] [--heal]
```

When invoked, ChainHunter runs a quick `bug_hunt` scan against the chosen
target. Use `--heal` to reinstall local scanner repositories and execute the
test suite for a self-healing security upgrade.

### Self-healing only

Run the dedicated self-healing routine without invoking Codex:

```bash
python3 cli/main.py self-heal
```

This command reinstalls scanner repositories (with `SKIP_CLONE=1`) and runs the
test suite to verify database integrity and module functionality.

## Developer notes

Development notes are stored in a compressed format inside `DEV_NOTES.dat`.
Use the CLI command `python3 cli/main.py notes` or the helper script
`dev_notes/notes_manager.py` to append or read entries. Every note
contains JSON metadata including an ID, timestamp, tags, personal flag,
compression algorithm and optional `context` reference IDs. Older notes are
automatically recompressed at higher levels using an algorithmic RLE+zlib
scheme that scales with the distance from the viewed entry. Viewing a note
adjusts compression for all entries and also decompresses any context notes
so they are easy to read. Each stored entry is preceded by a `# NOTE` line
listing its ID, timestamp and tags for quick reference. Notes can be filtered
by tag.

```bash
python3 cli/main.py notes add "Reminder to revisit sandbox perms"
python3 cli/main.py notes add "personal thoughts" --tags personal
python3 cli/main.py notes add "follow up" --context 1 2
python3 cli/main.py notes show -n 3
python3 cli/main.py notes view 0 --radius 1
python3 cli/main.py notes show -n 5 --tag personal
```
Set `DEV_NOTES_PATH` to override the default notes file location when testing.

## Version analysis utility

Use `version_analyzer.py` to compare recent git commits and recommend the best version based on test count and total lines of code.

```bash
python3 version_analyzer.py --count 4
```

The script prints a summary for each commit analyzed and suggests the most feature-rich version.

## Neural pipeline suggestion

`analysis_db/neural_analyzer.py` contains a neural network that learns from
stored results. It now looks at port counts, vulnerability totals and tags in
addition to severity levels. The network starts with synthetic data but
re-trains every time new pipeline results are logged, gradually improving its
recommendation of whether to run the `bug_hunt`, `extended_hunt` or
`repo_hunt` pipeline.
The trained model is saved to `analysis_db/model.pkl` each time new results are
incorporated so suggestions persist across runs.

```python
from analysis_db.neural_analyzer import suggest_pipeline

pipeline = suggest_pipeline([
    {"ports": [80], "vulnerabilities": []},
    {
        "ports": [22, 8080],
        "severity": "high",
        "vulnerabilities": [{"id": 1}],
        "tags": ["critical"],
    },
])
print(pipeline)
```

You can also let ChainHunter analyze recent results stored in the database and
print a recommended pipeline directly. The command updates the neural model
using the fetched results before printing the suggestion:

```bash
python3 cli/main.py suggest -n 5
```

### Chat with your results

You can ask ChatGPT questions about previous scans. The database server will
provide recent results as context and return an answer:

```bash
python3 cli/main.py chat "How severe are the latest findings?" -n 3
```

Set `OPENAI_API_KEY` to enable this feature.

## Auto-start service

Run `scripts/install_service.sh` to install a systemd user service that keeps ChainHunter running in an `xterm` window. The script creates a Python virtual environment under `venv` and installs the service and hourly timer in `~/.config/systemd/user`.

```bash
./scripts/install_service.sh
```

The service restarts automatically and the timer checks every hour to ensure it remains active.
