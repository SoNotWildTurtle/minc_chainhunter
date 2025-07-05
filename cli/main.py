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
import glob
import argparse
import logging
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

# Configuration
MODULE_DIRS = ["../recon_modules", "../vuln_modules", "../pipelines"]
MODULES: Dict[str, str] = {}
VERSION = "1.0.0"

def setup_argparse() -> argparse.ArgumentParser:
    """Set up the argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        description="MINC ChainHunter - Advanced Security Assessment Tool",
        epilog="Use 'minc <command> -h' for help on specific commands"
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
    run_parser.add_argument('args', nargs=argparse.REMAINDER, help='Module arguments')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available modules')
    list_parser.add_argument(
        '-t', '--type',
        choices=['all', 'recon', 'vuln'],
        default='all',
        help='Filter modules by type'
    )
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show module information')
    info_parser.add_argument('module', help='Name of the module to get info about')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update MINC ChainHunter')
    update_parser.add_argument(
        '--force',
        action='store_true',
        help='Force update even if already up to date'
    )

    # Report command
    report_parser = subparsers.add_parser('report', help='Generate markdown report')
    report_parser.add_argument('--out_dir', default='reports', help='Output directory')

    # Results command
    results_parser = subparsers.add_parser('results', help='Show stored scan results')
    results_parser.add_argument('-n', type=int, default=0, metavar='N', help='Show only the last N results')

    # Suggest command
    suggest_parser = subparsers.add_parser('suggest', help='Suggest pipeline using neural analyzer')
    suggest_parser.add_argument('-n', type=int, default=5, metavar='N', help='Analyze the last N results')

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
            py_files = glob.glob(os.path.join(abs_dir, "*.py"))
            for pf in py_files:
                if pf.endswith("__init__.py"):
                    continue
                name = os.path.splitext(os.path.basename(pf))[0]
                modules[name] = {
                    'path': pf,
                    'type': 'recon' if 'recon_modules' in pf else 'vuln',
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
                from analysis_db.db_api import log_scan_result
                sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
                payload = {"module": name, **result}
                log_scan_result(sock, payload)
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

def show_interactive_menu() -> None:
    """Show the interactive menu for module selection."""
    print(f"\n=== MINC ChainHunter v{VERSION} ===")
    print("Available modules:")
    
    # Group modules by type
    recon_modules = [m for m, data in MODULES.items() if data['type'] == 'recon']
    vuln_modules = [m for m, data in MODULES.items() if data['type'] == 'vuln']
    
    if recon_modules:
        print("\nReconnaissance:")
        for i, mod in enumerate(sorted(recon_modules), 1):
            print(f"  [{i}] {mod}")
    
    if vuln_modules:
        print("\nVulnerability Assessment:")
        start_idx = len(recon_modules) + 1
        for i, mod in enumerate(sorted(vuln_modules), start_idx):
            print(f"  [{i}] {mod}")
    
    print("\n  [u] Update/upgrade MINC ChainHunter")
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
                print("\n[+] Exiting MINC ChainHunter. Stay secure!")
                break
                
            if choice == 'u':
                update_minc()
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
                    print(f"\n[*] Running module: {module_name}")
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
            global MODULES
            MODULES = discover_modules()
            success = run_module(args.module, args.args)
            return 0 if success else 1
            
        elif args.command == 'list':
            MODULES = discover_modules()
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
                
        elif args.command == 'update':
            success = update_minc(args.force)
            return 0 if success else 1

        elif args.command == 'report':
            from analysis_db.db_api import generate_report
            sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
            resp = generate_report(sock, args.out_dir)
            if resp.get("status") == "ok":
                print(f"[+] Report written to {resp.get('path')}")
                return 0
            print("[!] Failed to generate report")
            return 1
        elif args.command == 'results':
            from analysis_db.db_api import get_results
            sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
            resp = get_results(sock, args.n)
            if resp.get("status") == "ok":
                print(json.dumps(resp.get("results", []), indent=2))
                return 0
            print("[!] Failed to fetch results")
            return 1
        elif args.command == 'suggest':
            from analysis_db.db_api import get_results
            from analysis_db.neural_analyzer import suggest_pipeline
            sock = os.environ.get("MINC_DB_SOCKET", "/tmp/minc_db.sock")
            resp = get_results(sock, args.n)
            if resp.get("status") == "ok":
                pipeline = suggest_pipeline(resp.get("results", []))
                print(pipeline)
                return 0
            print("[!] Failed to fetch results")
            return 1
            
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
