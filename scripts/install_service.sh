#!/bin/bash
# Install systemd user service for ChainHunter

REPO_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
VENV_DIR="$REPO_DIR/venv"
UNIT_DIR="${SYSTEMD_USER_DIR:-$HOME/.config/systemd/user}"

mkdir -p "$UNIT_DIR"

# create venv if missing and install deps
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --quiet numpy scikit-learn
fi

SERVICE_FILE="$UNIT_DIR/chainhunter.service"
TIMER_FILE="$UNIT_DIR/chainhunter.timer"

cat > "$SERVICE_FILE" <<SERVICE
[Unit]
Description=ChainHunter security service
After=network.target

[Service]
Type=simple
WorkingDirectory=$REPO_DIR
ExecStart=/usr/bin/xterm -hold -e "$VENV_DIR/bin/python $REPO_DIR/cli/main.py"
Restart=always
RestartSec=60

[Install]
WantedBy=default.target
SERVICE

cat > "$TIMER_FILE" <<TIMER
[Unit]
Description=Ensure ChainHunter stays active

[Timer]
OnBootSec=1min
OnUnitActiveSec=1h
Unit=chainhunter.service

[Install]
WantedBy=default.target
TIMER

if [ -z "$NO_SYSTEMCTL" ]; then
    systemctl --user daemon-reload
    systemctl --user enable --now chainhunter.service chainhunter.timer
fi
