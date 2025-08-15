#!/bin/bash
# MINC - sandbox/db_env/run_db.sh
# Launch MongoDB mimic in an isolated namespace/container, restrict all network access except secure IPC.

DB_DIR="${MINC_DB_DIR:-/opt/minc_chainhunter/db_data}"
SOCKET_PATH="${MINC_DB_SOCKET:-/opt/minc_chainhunter/sandbox/db_env/secure_ipc.sock}"
DB_EXEC="/opt/minc_chainhunter/analysis_db/db_init.py"
DB_USER="${MINC_DB_USER:-nobody}"
NET_NS="minc_db_ns"
CHROOT_DIR="${MINC_DB_CHROOT:-}"
SKIP_NS="${MINC_SKIP_NS:-0}"

if [ -n "${CHROOT_DIR}" ]; then
  DB_DIR_HOST="${CHROOT_DIR}${DB_DIR}"
  SOCKET_HOST="${CHROOT_DIR}${SOCKET_PATH}"
else
  DB_DIR_HOST="${DB_DIR}"
  SOCKET_HOST="${SOCKET_PATH}"
fi

# Ensure DB directory exists
mkdir -p "${DB_DIR_HOST}"
mkdir -p "$(dirname "${SOCKET_HOST}")"

# Create isolated network namespace if not already present
if [ "${SKIP_NS}" -ne 1 ]; then
  if ! ip netns list | grep -q "${NET_NS}"; then
    ip netns add "${NET_NS}"
  fi

  # Bring up loopback only in the namespace
  ip netns exec "${NET_NS}" ip link set lo up
fi

# Clean up any pre-existing socket
[ -e "${SOCKET_HOST}" ] && rm -f "${SOCKET_HOST}"

# Launch DB mimic, optionally inside the network namespace
CMD=(python3 "${DB_EXEC}" --db_dir "${DB_DIR}" --socket "${SOCKET_PATH}" --user "${DB_USER}")
if [ -n "${CHROOT_DIR}" ]; then
  CMD+=(--chroot "${CHROOT_DIR}")
fi

if [ "${SKIP_NS}" -ne 1 ]; then
  ip netns exec "${NET_NS}" "${CMD[@]}" &
else
  "${CMD[@]}" &
fi
PID=$!
echo "$PID" > "${DB_DIR_HOST}/db.pid"

echo "MongoDB mimic launched at ${SOCKET_PATH} (pid ${PID})"
