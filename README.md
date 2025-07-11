# MINC ChainHunter

MINC ChainHunter is an experimental security toolkit featuring a CLI interface and modular architecture. Modules are loaded dynamically from `recon_modules/` and `vuln_modules/`.

## Goals tracking

Development objectives are listed in `GOALS.txt`. Each short‑term item is
prefixed with `[GXX]` and long‑term goals use `[LXX]` so developer notes can
reference them with `goal:GXX` tags.

## Dependencies

Install the following Python packages:

- `numpy` and `scikit-learn` for the neural analyzer
- `cryptography` if you enable database encryption
- `fpdf` if you want PDF report generation
- `colorama` for colorful terminal output

```
pip install numpy scikit-learn cryptography fpdf
```
Run `python3 scripts/install_requirements.py` to install these packages and any requirements from cloned scanners.



## Usage

```
python3 cli/main.py                # interactive mode
python3 cli/main.py list           # list available modules
python3 cli/main.py run <module> [args]
python3 cli/main.py run <module> --targets host1 host2  # run concurrently
```

Use `--workers` to control the number of concurrent threads when running multiple targets.

The interactive mode now displays a colorful banner titled **ChainHunter Bug Hunting Utility** when run in a real terminal. Pipeline steps announce themselves and pause for confirmation when the session is interactive.

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
- `masscan_scan` – fast port scanning with masscan (ports are parsed for analysis).
- `nmap_scan` – service enumeration using nmap (open ports extracted).
- `aquatone_scan` – screenshot discovered hosts with aquatone.
- `git_dumper_scan` – dump exposed `.git` directories.
 - `xxe_scan` – sends an XML payload to detect XXE vulnerabilities.
- `xsstrike_scan` – detect reflected XSS vulnerabilities using XSStrike.
- `mythic_control` – manage the Mythic C2 framework (offensive).
- `sqlmap_scan` – run sqlmap for automated SQL injection exploitation.
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
  When possible, modules include a `raw` field capturing request and response
  data for deeper analysis.

The IPC bus components are under development. `bus_integrity.py` includes helper functions to verify socket permissions and approved command aliases.

## Installing GitHub scanners

The repository does not ship the full source of third-party scanners. Run
`scripts/install_scanner_repos.sh` after cloning ChainHunter to download the
required GitHub projects locally:

```bash
./scripts/install_scanner_repos.sh
```
Run `python3 scripts/install_requirements.py` to install Python dependencies.

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
- **Mythic** – command-and-control framework for offensive testing

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

To generate a consolidated report of all stored results, either run the
CLI command `python3 cli/main.py report` or send the `report` alias over the IPC
bus. Reports are written to the `reports/` directory by default. Use
`--format json` or `--format pdf` to export other formats. Use
`python3 cli/main.py results` to quickly display stored entries.
Run `python3 cli/main.py purge --limit 50` to keep only the most recent 50
results if the database grows large.

You can launch the analysis database server with `scripts/setup_ipc_bus.sh`,
which starts the IPC service at the path specified by the `MINC_DB_SOCKET`
environment variable. The server now drops privileges to the `nobody` user by
default when started through the sandbox scripts, ensuring results are written
with secure permissions.

### Sandbox helpers

The `sandbox/db_env/run_db.sh` script launches the database in an isolated
network namespace. Set `MINC_DB_CHROOT` to a directory and the server will
chroot into that path for extra protection. Use `sandbox/main_app/run_main.sh`
to start the CLI, optionally dropping privileges by setting `MINC_CLI_USER`.

## Manager scripts

Each major directory includes a small manager script to list or run its components. For example:

```bash
python3 recon_modules/manager.py --list
python3 vuln_modules/manager.py run nuclei_scan https://example.com
```

These helpers make it easy to automate tasks with minimal commands.

## Offensive modules

Offensive pentesting tools such as Mythic are placed in `offensive_modules/`.
They require manual supervision and should be run in coordination with
ChainHunter through interactive prompts. Use the manager script to list or run
them:

```bash
python3 offensive_modules/manager.py --list
python3 offensive_modules/manager.py run mythic_control install
```

ChainHunter will log results to the database, but it is expected that a human
operator reviews each step when using these modules.

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

`MINC_SELF_RATIO` controls how much processing power is dedicated to the
self‑evolution routine. The default value `0.2` uses roughly 20% of available
CPU cores when running self-evolve.


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
python3 cli/main.py self-evolve [--target <host>] [--heal] [--patch SCRIPT]
```

When invoked, ChainHunter loads recent results from the analysis database and
uses the neural analyzer to choose the best pipeline for self-evolution. The
pipeline runs with a worker count derived from `MINC_SELF_RATIO` (default `0.2`)
to limit CPU usage. Use `--heal` to reinstall local scanner repositories and
execute the test suite for a self-healing security upgrade. Provide `--patch`
with a Python script to apply changes after the script passes sandbox tests.

### Self-healing only

Run the dedicated self-healing routine without invoking Codex:

```bash
python3 cli/main.py self-heal
```

This command reinstalls scanner repositories (with `SKIP_CLONE=1`) and runs the
test suite to verify database integrity and module functionality.

### Sandboxed debugging

Use the built-in debugger to test evolution scripts in an isolated copy of the
repository. The helper copies the entire project to a temporary directory,
executes the provided script, and optionally runs the test suite.

```bash
python3 sandbox/debugger.py my_patch.py
```

The script runs inside the sandbox so existing code remains untouched. Only if
tests pass should you apply changes back to the main repository, optionally
using the memory patcher described below.

### Memory patching

After debugging, files can be modified directly via `mmap` using the memory
patcher utility. A backup is created automatically so changes can be rolled
back if something goes wrong:

```bash
python3 sandbox/memory_patcher.py path/to/file.py 10 "newtext"
```

To restore the backup, run:

```bash
python3 sandbox/memory_patcher.py path/to/file.py --rollback
```

This writes bytes to the chosen offset without reopening the file and saves the
original as `path/to/file.py.bak`. Combine this with the debugger to safely
update code after several test rounds.

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
`repo_hunt` pipeline. The analysis database server automatically updates the
model whenever a new result is saved. The trained model is stored at
`analysis_db/model.pkl` so suggestions persist across runs.

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

### Module recommendations

After enough results are logged, the neural analyzer can also suggest the most
useful modules to run next. It trains on each stored result and predicts which
modules are likely to discover additional vulnerabilities.

```bash
python3 cli/main.py suggest-mods -n 5
```

The command prints a ranked list of module names.

### Chat with your results

You can ask ChatGPT questions about previous scans. The database server will
provide recent results as context and return an answer:

```bash
python3 cli/main.py chat "How severe are the latest findings?" -n 3
```

Set `OPENAI_API_KEY` to enable this feature.

### Chat-driven pipeline planning

Ask ChatGPT which pipeline to run next based on recent results:

```bash
python3 cli/main.py plan -n 3
```

ChatGPT will analyze the stored results and suggest a pipeline such as
`bug_hunt`, `extended_hunt`, or `repo_hunt`.

### Manually retrain the neural model

You can trigger a retraining cycle for the neural analyzer using stored results:

```bash
python3 cli/main.py train
```

### Run scheduled scans

You can automate recurring scans by listing tasks in a JSON file and running the
scheduler:

```bash
python3 cli/main.py schedule --file tasks.json
```

Each task entry should include `args` for the CLI and an optional `interval` in
seconds before the next task runs.

## Auto-start service

Run `scripts/install_service.sh` to install a systemd user service that keeps ChainHunter running in an `xterm` window. The script creates a Python virtual environment under `venv` and installs the service and hourly timer in `~/.config/systemd/user`.

```bash
./scripts/install_service.sh
```

The service restarts automatically and the timer checks every hour to ensure it remains active.

## Plugin manager

Third-party modules can be installed using the plugin manager. Plugins are stored under `plugins/installed` by default and are automatically discovered by the CLI.

```bash
python3 plugins/plugin_manager.py list
python3 plugins/plugin_manager.py install /path/to/plugin
```

Set `CHAINHUNTER_PLUGIN_DIR` to override the default plugin directory.

