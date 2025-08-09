#!/usr/bin/env python3
# MINC - cli/main.py
"""
MINC ChainHunter - Advanced Vulnerability Scanner and Attack Chain Analysis Tool

A comprehensive security toolkit that dynamically loads modules from recon_modules/ and vuln_modules/
to perform security assessments, vulnerability scanning, and attack chain analysis.

Features:
- Dynamic module loading and execution
- Self-evolving/auto-upgrading capability
- Comprehensive logging and reporting
- Support for both interactive and non-interactive modes
- Module documentation and help system
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import importlib
import inspect
import glob
import argparse
import logging
import signal
try:
    from colorama import init, Fore, Style
except Exception:  # pragma: no cover - optional dependency
    print("[!] Missing 'colorama'. Run install_requirements.py or install from requirements.txt")
    init = lambda *args, **kwargs: None
    class Dummy:
        RESET_ALL = ''
        GREEN = MAGENTA = ''
        BRIGHT = ''
    Fore = Style = Dummy()
import json
import subprocess
from typing import Dict, List, Optional, Any
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('minc_chainhunter.log')
    ]
)
logger = logging.getLogger(__name__)

# avoid broken pipe errors when piping output
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

# initialize colorama for pretty output when TTY is available
init(strip=not sys.stdout.isatty(), autoreset=True)

GREEN = Fore.GREEN + Style.BRIGHT
PURPLE = Fore.MAGENTA + Style.BRIGHT
RESET = Style.RESET_ALL
BANNER = r"""
   ____ _           _       _   _             _             
  / ___| |__   __ _| |_ ___| | | | __ _ _ __ | | _____ _ __ 
 | |   | '_ \ / _` | __/ _ \ |_| |/ _` | '_ \| |/ / _ \ '__|
 | |___| | | | (_| | ||  __/  _  | (_| | | | |   <  __/ |   
  \____|_| |_|\__,_|\__\___|_| |_|\__,_|_| |_|_|\_\___|_|   
"""

# Configuration
PLUGIN_DIR = os.environ.get(
    'CHAINHUNTER_PLUGIN_DIR',
    os.path.join(os.path.dirname(__file__), '..', 'plugins', 'installed')
)
MODULE_DIRS = [
    "../recon_modules",
    "../vuln_modules",
    "../offensive_modules",
    "../pipelines",
    PLUGIN_DIR,
]
MODULES: Dict[str, str] = {}
VERSION = "1.0.0"

def setup_argparse() -> argparse.ArgumentParser:
    """Set up the argument parser with subcommands."""
    epilog = (
        "Commands:\n"
        "  General: run, list, info, usage, update\n"
        "  Database: report, results, stats, purge, gather-poc\n"
        "  Suggestions: suggest, suggest-mods, suggest-params, explore\n"
        "  Chat: chat, plan\n"
        "  Training: train, train-cve, train-success\n"
        "  Maintenance: schedule, self-evolve, self-heal, self-test, notes\n\n"
        "Use 'minc <command> -h' for help on specific commands"
    )
    parser = argparse.ArgumentParser(
        description="MINC ChainHunter - Advanced Security Assessment Tool",
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Global arguments
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output (very verbose)'
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'MINC ChainHunter v{VERSION}',
        help='Show version and exit'
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Run command
    run_parser = subparsers.add_parser('run', help='Run a specific module')
    run_parser.add_argument('module', help='Name of the module to run')
    run_parser.add_argument('--targets', nargs='+', help='Targets for concurrent run')
    run_parser.add_argument('--workers', type=int, default=4, help='Number of worker threads')
    run_parser.add_argument('args', nargs=argparse.REMAINDER, help='Module arguments')

    # List command
    list_parser = subparsers.add_parser('list', help='List available modules')
    list_parser.add_argument(
        '-t', '--type',
        choices=['all', 'recon', 'vuln', 'offensive', 'pipeline'],
        default='all',
        help='Filter modules by type'
    )
    list_parser.add_argument(
        '--json',
        action='store_true',
        help='Output module list as JSON'
    )

    # Info command
    info_parser = subparsers.add_parser('info', help='Show module information')
    info_parser.add_argument('module', help='Name of the module to get info about')

    usage_parser = subparsers.add_parser('usage', help='Show module usage')
    usage_parser.add_argument('module', help='Module name')

    # Update command
    update_parser = subparsers.add_parser('update', help='Update MINC ChainHunter')
    update_parser.add_argument(
        '--force',
        action='store_true',
        help='Force update even if already up to date'
    )

    # Report command
    report_parser = subparsers.add_parser('report', help='Generate report from stored results')
    report_parser.add_argument('--out_dir', default='reports', help='Output directory')
    report_parser.add_argument('--format', choices=['md', 'json', 'pdf'], default='md',
                              help='Report format (md, json, pdf)')
    report_parser.add_argument('--template', help='Optional markdown template for entries')

    # Results command
    results_parser = subparsers.add_parser('results', help='Show stored scan results')
    results_parser.add_argument('-n', type=int, default=0, metavar='N', help='Show only the last N results')
    results_parser.add_argument('--tag', help='Filter results by tag')

    stats_parser = subparsers.add_parser('stats', help='Show result statistics')

    # Purge command
    purge_parser = subparsers.add_parser('purge', help='Remove old scan results')
    purge_parser.add_argument('--limit', type=int, required=True, metavar='N',
                              help='Keep only the latest N results')

    # Gather artifacts command
    gather_parser = subparsers.add_parser('gather-poc', help='Export raw scan data as proof-of-concept artifacts')
    gather_parser.add_argument('--out_dir', default='artifacts', help='Output directory')

    # Suggest command
    suggest_parser = subparsers.add_parser('suggest', help='Suggest pipeline using neural analyzer')
    suggest_parser.add_argument('-n', type=int, default=5, metavar='N', help='Analyze the last N results')

    modules_parser = subparsers.add_parser('suggest-mods', help='Recommend modules to run next')
    modules_parser.add_argument('-n', type=int, default=5, metavar='N', help='Analyze the last N results')
    modules_parser.add_argument('--after', help='Module to base follow-up suggestions on')

    params_parser = subparsers.add_parser('suggest-params', help='Recommend parameters for a module')
    params_parser.add_argument('module', help='Module name')
    params_parser.add_argument('-n', type=int, default=50, metavar='N', help='Analyze the last N results')

    explore_parser = subparsers.add_parser('explore', help='Suggest example commands for a module')
    explore_parser.add_argument('module', help='Module name')
    explore_parser.add_argument('-n', type=int, default=3, metavar='N', help='Number of commands to suggest')

    # Chat command
    chat_parser = subparsers.add_parser('chat', help='Ask ChatGPT about stored results')
    chat_parser.add_argument('question', help='Question to ask')
    chat_parser.add_argument('-n', type=int, default=5, metavar='N', help='Number of recent results to include')

    # Plan command
    plan_parser = subparsers.add_parser('plan', help='Get ChatGPT pipeline recommendation')
    plan_parser.add_argument('-n', type=int, default=5, metavar='N', help='Number of recent results to include')

    # Train command
    train_parser = subparsers.add_parser('train', help='Retrain neural model from DB results')

    train_cve_parser = subparsers.add_parser('train-cve', help='Train neural model using CVE dataset')
    train_cve_parser.add_argument('path', help='Path to CVE JSON file')

    train_success_parser = subparsers.add_parser('train-success', help='Reinforce neural model using successful cases')
    train_success_parser.add_argument('path', help='Path to success JSON file')

    # Schedule command
    sched_parser = subparsers.add_parser('schedule', help='Run scheduled tasks')
    sched_parser.add_argument('--file', default='tasks.json', help='Tasks JSON file')

    # Operator command
    op_parser = subparsers.add_parser('operator', help='Operator management commands')
    op_sub = op_parser.add_subparsers(dest='op_cmd', required=True)
    tune_p = op_sub.add_parser('tune', help='Set suggestion threshold')
    tune_p.add_argument('threshold', type=float)
    approve_p = op_sub.add_parser('approve', help='Approve finding ID')
    approve_p.add_argument('fid')
    pause_p = op_sub.add_parser('pause', help='Pause running jobs')
    pause_p.add_argument('job', help='Job ID')
    resume_p = op_sub.add_parser('resume', help='Resume paused jobs')
    resume_p.add_argument('job', help='Job ID')

    # Self-evolve command
    evolve_parser = subparsers.add_parser('self-evolve', help='Run Codex to upgrade ChainHunter')
    evolve_parser.add_argument('--target', default='127.0.0.1', help='Target for bug hunt')
    evolve_parser.add_argument('--heal', action='store_true', help='Run self-healing tests')
    evolve_parser.add_argument('--patch', help='Apply patch SCRIPT after sandbox test')
    evolve_parser.add_argument('--iter', type=int, default=1, help='Number of evolution cycles')

    # Self-heal command
    heal_parser = subparsers.add_parser('self-heal', help='Run self-healing routine')

    # Self-test command
    test_parser = subparsers.add_parser('self-test', help='Run built-in test suite')

    # Notes command
    notes_parser = subparsers.add_parser('notes', help='Manage developer notes')
    notes_sub = notes_parser.add_subparsers(dest='notes_cmd', required=True)

    add_p = notes_sub.add_parser('add', help='Add a note')
    add_p.add_argument('text', help='Note text')
    add_p.add_argument('--tags', nargs='*', default=[], help='Tags for the note')
    add_p.add_argument('--personal', action='store_true', help='Mark note as personal')
    add_p.add_argument('--context', nargs='*', type=int, default=[], metavar='ID',
                       help='IDs of related notes')

    show_p = notes_sub.add_parser('show', help='Show recent notes')
    show_p.add_argument('-n', type=int, default=5, metavar='N', help='Number of notes to display')
    show_p.add_argument('--tag', help='Filter by tag')

    view_p = notes_sub.add_parser('view', help='View notes around INDEX')
    view_p.add_argument('index', type=int, help='Center index to view')
    view_p.add_argument('--radius', type=int, default=0, metavar='N', help='Number of neighbouring notes')

    return parser

def discover_modules() -> Dict[str, str]:
    """Discover and load available modules from MODULE_DIRS."""
    modules = {}
    for mod_dir in MODULE_DIRS:
        try:
            abs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), mod_dir))
            if not os.path.exists(abs_dir):
                logger.warning(f"Module directory not found: {abs_dir}")
                continue

            # Find all Python files in the directory
            py_files = glob.glob(os.path.join(abs_dir, "**", "*.py"), recursive=True)
            for pf in py_files:
                if pf.endswith("__init__.py"):
                    continue
                name = os.path.splitext(os.path.basename(pf))[0]
                mod_type = 'recon'
                if 'pipelines' in pf or 'pipeline' in name:
                    mod_type = 'pipeline'
                elif 'offensive_modules' in pf or 'offensive' in name:
                    mod_type = 'offensive'
                elif 'vuln' in pf or 'vuln' in name:
                    mod_type = 'vuln'
                modules[name] = {
                    'path': pf,
                    'type': mod_type,
                    'module': None  # Will be lazy-loaded when needed
                }
                logger.debug(f"Discovered module: {name} at {pf}")
        except Exception as e:
            logger.error(f"Error discovering modules in {mod_dir}: {str(e)}")

    return modules

def load_module(name: str) -> Any:
    """Dynamically load a module by name."""
    if name not in MODULES:
        raise ValueError(f"Module not found: {name}")

    # Lazy load the module if not already loaded
    if MODULES[name]['module'] is None:
        try:
            module_dir = os.path.dirname(MODULES[name]['path'])
            if module_dir not in sys.path:
                sys.path.insert(0, module_dir)

            module_name = os.path.splitext(os.path.basename(MODULES[name]['path']))[0]
            MODULES[name]['module'] = importlib.import_module(module_name)
            logger.debug(f"Successfully loaded module: {name}")
        except Exception as e:
            logger.error(f"Failed to load module {name}: {str(e)}")
            raise

    return MODULES[name]['module']

def get_module_info(name: str) -> Dict[str, Any]:
    """Get information about a module."""
    try:
        mod = load_module(name)
        info = {
            'name': name,
            'type': MODULES[name]['type'],
            'path': MODULES[name]['path'],
            'doc': mod.__doc__ or 'No documentation available',
            'functions': [f for f in dir(mod) if callable(getattr(mod, f)) and not f.startswith('_')]
        }
        return info
    except Exception as e:
        logger.error(f"Error getting info for module {name}: {str(e)}")
        raise

def show_module_usage(name: str) -> None:
    """Display usage information for a module if supported."""
    try:
        mod = load_module(name)
        print('Usage:')
        print(mod.__doc__ or f'No documentation for {name}')
        funcs = [f for f in dir(mod) if callable(getattr(mod, f)) and not f.startswith('_')]
        if funcs:
            print('Available functions:', ', '.join(funcs))
    except Exception as exc:
        print(f'Error showing usage for {name}: {exc}')

def run_module(name: str, args: List[str]) -> bool:
    """Run a module with the given arguments."""
    try:
        mod = load_module(name)
        if not hasattr(mod, 'main'):
            logger.error(f"Module {name} has no 'main' function")
            return False

        # Save original args and replace with module args
        original_argv = sys.argv
        sys.argv = [name] + args

        logger.info(f"Running module: {name}")
        result = mod.main()

        # Restore original args
        sys.argv = original_argv

        # If module returns structured result, log to DB
        if isinstance(result, dict):
            try:
                from analysis_db.db_api import log_scan_result, generate_report
                sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
                payload = {"module": name, "params": args, **result}
                log_scan_result(sock, payload)
                if os.environ.get("MINC_AUTO_REPORT"):
                    out_dir = os.environ.get("MINC_AUTO_REPORT_DIR", "reports")
                    try:
                        generate_report(sock, out_dir)
                    except Exception as rep_err:
                        logger.error(f"Failed to auto-generate report: {rep_err}")
            except Exception as e:
                logger.error(f"Failed to log result: {e}")
            return True

        return result is not False
    except Exception as e:
        logger.error(f"Error running module {name}: {str(e)}")
        if '--debug' in sys.argv or '-v' in sys.argv:
            import traceback
            traceback.print_exc()
        return False


def run_module_multi(name: str, targets: List[str], args: List[str], workers: int = 4) -> bool:
    """Run a module concurrently for multiple targets."""
    from concurrent.futures import ThreadPoolExecutor

    def runner(tgt: str) -> bool:
        return run_module(name, [tgt] + args)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(runner, targets))
    return all(results)

def show_interactive_menu() -> None:
    """Show the interactive menu for module selection."""
    if sys.stdout.isatty():
        print(PURPLE + BANNER + RESET)
        print(GREEN + f"Version {VERSION}\n" + RESET)
        print(GREEN + "Available modules:" + RESET)
    else:
        print(f"\n=== MINC ChainHunter v{VERSION} ===")
        print("Available modules:")

    # Group modules by type
    recon_modules = [m for m, data in MODULES.items() if data['type'] == 'recon']
    vuln_modules = [m for m, data in MODULES.items() if data['type'] == 'vuln']
    off_modules = [m for m, data in MODULES.items() if data['type'] == 'offensive']
    pipeline_modules = [m for m, data in MODULES.items() if data['type'] == 'pipeline']

    if recon_modules:
        if sys.stdout.isatty():
            print(PURPLE + "\nReconnaissance:" + RESET)
        else:
            print("\nReconnaissance:")
        for i, mod in enumerate(sorted(recon_modules), 1):
            if sys.stdout.isatty():
                print(GREEN + f"  [{i}] {mod}" + RESET)
            else:
                print(f"  [{i}] {mod}")

    if vuln_modules:
        if sys.stdout.isatty():
            print(PURPLE + "\nVulnerability Assessment:" + RESET)
        else:
            print("\nVulnerability Assessment:")
        start_idx = len(recon_modules) + 1
        for i, mod in enumerate(sorted(vuln_modules), start_idx):
            if sys.stdout.isatty():
                print(GREEN + f"  [{i}] {mod}" + RESET)
            else:
                print(f"  [{i}] {mod}")

    if off_modules:
        if sys.stdout.isatty():
            print(PURPLE + "\nOffensive Pentesting:" + RESET)
        else:
            print("\nOffensive Pentesting:")
        start_idx = len(recon_modules) + len(vuln_modules) + 1
        for i, mod in enumerate(sorted(off_modules), start_idx):
            if sys.stdout.isatty():
                print(GREEN + f"  [{i}] {mod}" + RESET)
            else:
                print(f"  [{i}] {mod}")

    if pipeline_modules:
        if sys.stdout.isatty():
            print(PURPLE + "\nPipelines:" + RESET)
        else:
            print("\nPipelines:")
        start_idx = len(recon_modules) + len(vuln_modules) + len(off_modules) + 1
        for i, mod in enumerate(sorted(pipeline_modules), start_idx):
            if sys.stdout.isatty():
                print(GREEN + f"  [{i}] {mod}" + RESET)
            else:
                print(f"  [{i}] {mod}")

    if sys.stdout.isatty():
        print(PURPLE + "\nMaintenance:" + RESET)
        print(GREEN + "  [u] Update/upgrade MINC ChainHunter" + RESET)
        print(GREEN + "  [e] Self-evolve (automated upgrade)" + RESET)
        print(GREEN + "  [h] Self-heal (reinstall scanners & run tests)" + RESET)
        print(GREEN + "  [x] Self-test (run pytest suite)" + RESET)
        print(GREEN + "  [n] View developer notes" + RESET)

        print(PURPLE + "\nTraining:" + RESET)
        print(GREEN + "  [t] Retrain neural model" + RESET)
        print(GREEN + "  [v] Train with CVE data" + RESET)
        print(GREEN + "  [w] Reinforce from successes" + RESET)
        print(GREEN + "  [o] Operator actions" + RESET)

        print(PURPLE + "\nAnalysis:" + RESET)
        print(GREEN + "  [r] Show recent results" + RESET)
        print(GREEN + "  [s] Show statistics" + RESET)
        print(GREEN + "  [p] Plan next pipeline" + RESET)
        print(GREEN + "  [c] Chat about results" + RESET)
        print(GREEN + "  [a] Generate report" + RESET)
        print(GREEN + "  [g] Gather artifacts" + RESET)

        print(PURPLE + "\nUtilities:" + RESET)
        print(GREEN + "  [i] <module> Show module information" + RESET)
        print(GREEN + "  [q] Quit" + RESET)
    else:
        print("\nMaintenance:")
        print("  [u] Update/upgrade MINC ChainHunter")
        print("  [e] Self-evolve (automated upgrade)")
        print("  [h] Self-heal (reinstall scanners & run tests)")
        print("  [x] Self-test (run pytest suite)")
        print("  [n] View developer notes")

        print("\nTraining:")
        print("  [t] Retrain neural model")
        print("  [v] Train with CVE data")
        print("  [w] Reinforce from successes")
        print("  [o] Operator actions")

        print("\nAnalysis:")
        print("  [r] Show recent results")
        print("  [s] Show statistics")
        print("  [p] Plan next pipeline")
        print("  [c] Chat about results")
        print("  [a] Generate report")
        print("  [g] Gather artifacts")

        print("\nUtilities:")
        print("  [i] <module> Show module information")
        print("  [q] Quit")

def interactive_mode() -> None:
    """Run MINC ChainHunter in interactive mode."""
    global MODULES
    MODULES = discover_modules()

    if not MODULES:
        logger.error("No modules found. Please check your module directories.")
        return

    while True:
        try:
            show_interactive_menu()
            choice = input("\n> ").strip().lower()

            if not choice:
                continue

            if choice == 'q':
                if sys.stdout.isatty():
                    print(PURPLE + "\n[+] Exiting ChainHunter. Stay secure!" + RESET)
                else:
                    print("\n[+] Exiting MINC ChainHunter. Stay secure!")
                break

            if choice == 'u':
                update_minc()
                continue

            if choice == 'e':
                from scripts.self_evolve import run_self_evolve
                run_self_evolve()
                continue

            if choice == 'h':
                from scripts.self_heal import run_self_heal
                run_self_heal()
                continue

            if choice == 'x':
                from scripts.self_test import run_self_test
                run_self_test()
                continue

            if choice == 'n':
                from dev_notes import notes_manager as nm
                nm.show_notes(5)
                continue

            if choice == 't':
                from analysis_db.db_api import train_model
                sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
                resp = train_model(sock)
                print(resp.get("msg", resp.get("status")))
                continue

            if choice == 'v':
                from analysis_db.db_api import train_model_cve
                sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
                path = input("Path to CVE JSON: ").strip()
                resp = train_model_cve(sock, path)
                print(resp.get("msg", resp.get("status")))
                continue

            if choice == 'w':
                from analysis_db.db_api import train_model_success
                sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
                path = input("Path to success JSON: ").strip()
                resp = train_model_success(sock, path)
                print(resp.get("msg", resp.get("status")))
                continue

            if choice == 'o':
                from analysis_db.db_api import operator_action
                sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
                cmd = input(
                    "Operator action (tune <thr>|approve <id>|pause <job>|resume <job>): "
                ).strip().split()
                if cmd:
                    action = cmd[0]
                    value = cmd[1] if len(cmd) > 1 else None
                    resp = operator_action(sock, action, value)
                    print(resp.get("msg", resp.get("status")))
                continue

            if choice == 'r':
                from analysis_db.db_api import get_results
                sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
                resp = get_results(sock, 5)
                if resp.get("status") == "ok":
                    print(json.dumps(resp.get("results", []), indent=2))
                else:
                    print("[!] Failed to fetch results")
                continue

            if choice == 's':
                from analysis_db.db_api import get_stats
                sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
                resp = get_stats(sock)
                if resp.get("status") == "ok":
                    print(json.dumps(resp, indent=2))
                else:
                    print("[!] Failed to fetch stats")
                continue

            if choice == 'p':
                from analysis_db.db_api import plan_pipeline
                sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
                resp = plan_pipeline(sock, 5)
                if resp.get("status") == "ok":
                    print(resp.get("plan"))
                else:
                    print("[!] Failed to get plan")
                continue

            if choice == 'c':
                from analysis_db.db_api import ask_question
                sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
                question = input("Question: ").strip()
                resp = ask_question(sock, question, 5)
                if resp.get("status") == "ok":
                    print(resp.get("answer"))
                else:
                    print("[!] Failed to get answer")
                continue

            if choice == 'a':
                from analysis_db.db_api import generate_report
                sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
                out = input("Output directory [reports]: ").strip() or "reports"
                fmt = input("Format (md|pdf|json) [md]: ").strip() or "md"
                tmpl = input("Template file (optional): ").strip() or None
                resp = generate_report(sock, out, fmt, tmpl)
                if resp.get("status") == "ok":
                    print(f"[+] Report written to {resp.get('path')}")
                else:
                    print("[!] Failed to generate report")
                continue

            if choice == 'g':
                from scripts.gather_artifacts import gather_artifacts
                out = input("Output directory [artifacts]: ").strip() or "artifacts"
                gather_artifacts('db_data', out)
                print(f"[+] Artifacts saved to {out}")
                continue

            if choice.startswith('i '):
                module_name = choice[2:].strip()
                try:
                    info = get_module_info(module_name)
                    print(f"\n=== {module_name} ===")
                    print(f"Type: {info['type'].title()}")
                    print(f"Path: {info['path']}")
                    print("\nDocumentation:")
                    print(info['doc'])
                    print("\nAvailable functions:", ", ".join(info['functions']))
                except Exception as e:
                    logger.error(f"Error getting module info: {str(e)}")
                continue

            # Try to run a module by number
            try:
                idx = int(choice) - 1
                module_list = sorted(MODULES)
                if 0 <= idx < len(module_list):
                    module_name = module_list[idx]
                    info = get_module_info(module_name)
                    print(f"\n[*] Running module: {module_name}")
                    if info.get('doc'):
                        print(info['doc'])
                    show_module_usage(module_name)
                    print("    Enter module arguments (if any) or press Enter to continue:")
                    args = input("    >>> ").strip().split()
                    run_module(module_name, args)
                else:
                    print("[!] Invalid selection.")
            except ValueError:
                print("[!] Invalid input. Please enter a number, 'u' to update, or 'q' to quit.")

        except KeyboardInterrupt:
            print("\n[!] Operation cancelled by user.")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            if '--debug' in sys.argv or '-v' in sys.argv:
                import traceback
                traceback.print_exc()
            break

def update_minc(force: bool = False, repo_dir: str | None = None) -> bool:
    """Update MINC ChainHunter by pulling latest changes via git."""
    print("\n[*] Checking for updates...")
    repo_root = Path(repo_dir) if repo_dir else Path(__file__).resolve().parents[1]
    try:
        if not (repo_root / ".git").is_dir():
            print("  - No git repository found")
            return False

        print("  - Fetching updates from origin...")
        subprocess.run(["git", "fetch"], cwd=repo_root, check=False, stdout=subprocess.DEVNULL)
        # Determine local and remote HEAD
        local = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root).strip()
        remote = None
        try:
            remote = subprocess.check_output(["git", "rev-parse", "@{u}"], cwd=repo_root).strip()
        except subprocess.CalledProcessError:
            print("  - No upstream configured for this repo")
            return False

        if force or local != remote:
            print("  - Pulling latest changes...")
            subprocess.run(["git", "pull"], cwd=repo_root, check=False)
            print("\n[+] Update completed successfully!")
            return True

        print("  - MINC ChainHunter is up to date!")
        return True

    except Exception as e:
        logger.error(f"Update failed: {str(e)}")
        return False

def main() -> int:
    """Main entry point for MINC ChainHunter."""
    parser = setup_argparse()
    args = parser.parse_args()
    global MODULES

    # Set log level based on verbosity
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    logger.debug(f"Starting MINC ChainHunter v{VERSION}")

    # If no command is provided, start interactive mode
    if not args.command:
        interactive_mode()
        return 0

    # Handle commands
    try:
        if args.command == 'run':
            if not args.module:
                logger.error("No module specified")
                return 1
            MODULES = discover_modules()
            if args.targets:
                success = run_module_multi(args.module, args.targets, args.args, args.workers)
            else:
                success = run_module(args.module, args.args)
            return 0 if success else 1

        elif args.command == 'list':
            MODULES = discover_modules()
            if args.json:
                types = ['recon', 'vuln', 'offensive', 'pipeline'] if args.type == 'all' else [args.type]
                data = {}
                for t in types:
                    data[t] = sorted([m for m, d in MODULES.items() if d['type'] == t])
                print(json.dumps(data, indent=2))
                return 0

            if args.type == 'all':
                print("\nAvailable modules:")
                print("==================")

            if args.type in ['all', 'recon']:
                recon = [m for m, data in MODULES.items() if data['type'] == 'recon']
                if recon:
                    print("\nReconnaissance:" + " " * 30 + "(Type: recon)")
                    print("-" * 50)
                    for mod in sorted(recon):
                        print(f"  {mod}")


            if args.type in ['all', 'vuln']:
                vuln = [m for m, data in MODULES.items() if data['type'] == 'vuln']
                if vuln:
                    print("\nVulnerability Assessment:" + " " * 20 + "(Type: vuln)")
                    print("-" * 50)
                    for mod in sorted(vuln):
                        print(f"  {mod}")

            if args.type in ['all', 'offensive']:
                offensive = [m for m, data in MODULES.items() if data['type'] == 'offensive']
                if offensive:
                    print("\nOffensive Pentesting:" + " " * 23 + "(Type: offensive)")
                    print("-" * 50)
                    for mod in sorted(offensive):
                        print(f"  {mod}")

            if args.type in ['all', 'pipeline']:
                pipelines = [m for m, data in MODULES.items() if data['type'] == 'pipeline']
                if pipelines:
                    print("\nPipelines:" + " " * 34 + "(Type: pipeline)")
                    print("-" * 50)
                    for mod in sorted(pipelines):
                        print(f"  {mod}")

            print(f"\nTotal modules: {len(MODULES)}")
            return 0

        elif args.command == 'info':
            try:
                info = get_module_info(args.module)
                print(f"\n=== {args.module} ===")
                print(f"Type: {info['type'].title()}")
                print(f"Path: {info['path']}")
                print("\nDocumentation:")
                print(info['doc'])
                print("\nAvailable functions:", ", ".join(info['functions']))
                return 0
            except Exception as e:
                logger.error(f"Error: {str(e)}")
                return 1

        elif args.command == 'usage':
            MODULES = discover_modules()
            show_module_usage(args.module)
            return 0

        elif args.command == 'update':
            success = update_minc(args.force)
            return 0 if success else 1

        elif args.command == 'report':
            from analysis_db.db_api import generate_report
            sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
            resp = generate_report(sock, args.out_dir, args.format, args.template)
            if resp.get("status") == "ok":
                print(f"[+] Report written to {resp.get('path')}")
                return 0
            print("[!] Failed to generate report")
            return 1
        elif args.command == 'results':
            from analysis_db.db_api import get_results, search_results
            sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
            if args.tag:
                resp = search_results(sock, args.tag, args.n)
            else:
                resp = get_results(sock, args.n)
            if resp.get("status") == "ok":
                print(json.dumps(resp.get("results", []), indent=2))
                return 0
            print("[!] Failed to fetch results")
            return 1
        elif args.command == 'stats':
            from analysis_db.db_api import get_stats
            sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
            resp = get_stats(sock)
            if resp.get("status") == 'ok':
                print(json.dumps(resp, indent=2))
                return 0
            print("[!] Failed to fetch stats")
            return 1
        elif args.command == 'purge':
            from analysis_db.db_api import purge_results
            sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
            resp = purge_results(sock, args.limit)
            if resp.get("status") == "ok":
                print("[+] Database purged")
                return 0
            print("[!] Failed to purge results")
            return 1
        elif args.command == 'suggest':
            from analysis_db.db_api import get_results
            from analysis_db.neural_analyzer import (
                suggest_pipeline,
                update_model_from_results,
            )
            sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
            resp = get_results(sock, args.n)
            if resp.get("status") == "ok":
                results = resp.get("results", [])
                update_model_from_results(results)
                pipeline = suggest_pipeline(results)
                print(pipeline)
                return 0
            print("[!] Failed to fetch results")
            return 1
        elif args.command == 'suggest-mods':
            from analysis_db.db_api import suggest_modules_api
            sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
            resp = suggest_modules_api(sock, args.n, args.after)
            if resp.get("status") == 'ok':
                for m in resp.get('modules', []):
                    print(m)
                return 0
            print("[!] Failed to get recommendations")
            return 1
        elif args.command == 'suggest-params':
            from analysis_db.db_api import suggest_params_api
            sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
            resp = suggest_params_api(sock, args.module, args.n)
            if resp.get("status") == 'ok':
                for p in resp.get('params', []):
                    print(' '.join(p) if p else '(no params)')
                return 0
            print("[!] Failed to get parameter suggestions")
            return 1
        elif args.command == 'explore':
            from analysis_db.db_api import explore_module_api
            info = get_module_info(args.module)
            sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
            resp = explore_module_api(sock, args.module, info['doc'], args.n)
            if resp.get("status") == 'ok':
                for line in resp.get('commands', []):
                    print(line)
                return 0
            print("[!] Failed to explore module")
            return 1
        elif args.command == 'chat':
            from analysis_db.db_api import ask_question
            sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
            resp = ask_question(sock, args.question, args.n)
            if resp.get("status") == 'ok':
                print(resp.get('answer'))
                return 0
            print("[!] Failed to get answer")
            return 1
        elif args.command == 'plan':
            from analysis_db.db_api import plan_pipeline
            sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
            resp = plan_pipeline(sock, args.n)
            if resp.get("status") == 'ok':
                print(resp.get('plan'))
                return 0
            print("[!] Failed to get plan")
            return 1
        elif args.command == 'train':
            from analysis_db.db_api import train_model
            sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
            resp = train_model(sock)
            if resp.get("status") == 'ok':
                print("[+] Model retrained")
                return 0
            print("[!] Failed to retrain model")
            return 1
        elif args.command == 'train-cve':
            from analysis_db.db_api import train_model_cve
            sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
            resp = train_model_cve(sock, args.path)
            if resp.get("status") == 'ok':
                print("[+] Model trained with CVE data")
                return 0
            print("[!] Failed to train model from CVE data")
            return 1
        elif args.command == 'train-success':
            from analysis_db.db_api import train_model_success
            sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
            resp = train_model_success(sock, args.path)
            if resp.get("status") == 'ok':
                delta = resp.get('delta', 0.0)
                print(f"[+] Model reinforced with success data (\u0394={delta:.4f})")
                return 0
            print("[!] Failed to reinforce model")
            return 1
        elif args.command == 'schedule':
            from scripts.scheduler import run_schedule
            run_schedule(args.file)
            return 0
        elif args.command == 'notes':
            from dev_notes import notes_manager as nm
            if args.notes_cmd == 'add':
                nm.add_note(args.text, tags=args.tags, personal=args.personal,
                            context=args.context)
                print("[+] Note added")
                return 0
            if args.notes_cmd == 'show':
                nm.show_notes(args.n, tag=args.tag)
                return 0
            if args.notes_cmd == 'view':
                nm.view_notes(args.index, radius=args.radius)
                return 0
        elif args.command == 'operator':
            from analysis_db.db_api import operator_action
            sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
            if args.op_cmd == 'tune':
                resp = operator_action(sock, 'tune', args.threshold)
            elif args.op_cmd == 'approve':
                resp = operator_action(sock, 'approve', args.fid)
            elif args.op_cmd == 'pause':
                resp = operator_action(sock, 'pause', args.job)
            else:  # resume
                resp = operator_action(sock, 'resume', args.job)
            if resp.get('status') == 'ok':
                print('[+] Operator action executed')
                return 0
            print('[-] Operator action failed')
            return 1
        elif args.command == 'self-evolve':
            from scripts.self_evolve import run_self_evolve
            ok = run_self_evolve(target=args.target, heal=args.heal, patch_script=args.patch, iterations=args.iter)
            return 0 if ok else 1
        elif args.command == 'self-heal':
            from scripts.self_heal import run_self_heal
            ok = run_self_heal()
            return 0 if ok else 1
        elif args.command == 'self-test':
            from scripts.self_test import run_self_test
            ok = run_self_test()
            return 0 if ok else 1
        elif args.command == 'gather-poc':
            from scripts.gather_artifacts import gather_artifacts
            gather_artifacts('db_data', args.out_dir)
            print(f"[+] Artifacts saved to {args.out_dir}")
            return 0

    except KeyboardInterrupt:
        print("\n[!] Operation cancelled by user.")
        return 1
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
