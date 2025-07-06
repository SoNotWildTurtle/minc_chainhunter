#!/bin/bash
# MINC - sandbox/db_env/run_db.sh
# Launch MongoDB mimic in an isolated namespace/container, restrict all network access except secure IPC.

DB_DIR="/opt/minc_chainhunter/db_data"
SOCKET_PATH="/opt/minc_chainhunter/sandbox/db_env/secure_ipc.sock"
DB_EXEC="/opt/minc_chainhunter/analysis_db/db_init.py"
DB_USER="nobody"
NET_NS="minc_db_ns"
CHROOT_DIR="${MINC_DB_CHROOT:-}"

# Ensure DB directory exists
mkdir -p "${DB_DIR}"

# Create isolated network namespace if not already present
if ! ip netns list | grep -q "${NET_NS}"; then
  ip netns add "${NET_NS}"
fi

# Bring up loopback only in the namespace
ip netns exec "${NET_NS}" ip link set lo up

# Clean up any pre-existing socket
[ -e "${SOCKET_PATH}" ] && rm -f "${SOCKET_PATH}"

# Launch DB mimic in the network namespace, accessible only by secure UNIX socket
CMD=(python3 "${DB_EXEC}" --db_dir "${DB_DIR}" --socket "${SOCKET_PATH}" --user "${DB_USER}")
if [ -n "${CHROOT_DIR}" ]; then
  CMD+=(--chroot "${CHROOT_DIR}")
  mkdir -p "${CHROOT_DIR}"
fi
ip netns exec "${NET_NS}" "${CMD[@]}" &

echo "MongoDB mimic launched in sandboxed netns (${NET_NS}) with IPC at ${SOCKET_PATH}"
