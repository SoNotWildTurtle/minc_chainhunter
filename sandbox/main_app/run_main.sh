#!/bin/bash
# MINC - sandbox/main_app/run_main.sh
# Launch the ChainHunter CLI with optional privilege drop

DIR="$(cd "$(dirname "$0")"/../.. && pwd)"
USER_NAME="${MINC_CLI_USER:-}"

if [ -n "$USER_NAME" ] && [ "$(id -u)" -eq 0 ]; then
  exec su "$USER_NAME" -s /bin/bash -c "python3 \"$DIR/cli/main.py\" "$@""
else
  exec python3 "$DIR/cli/main.py" "$@"
fi

