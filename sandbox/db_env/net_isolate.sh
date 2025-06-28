#!/bin/bash
# MINC - sandbox/db_env/net_isolate.sh
# Hard-locks the DB netns to loopback only. Run after launching DB netns.

NET_NS="minc_db_ns"

# Drop all non-loopback interfaces/routes in the namespace
ip netns exec "${NET_NS}" ip link | grep -v "lo:" | awk -F: '{print $2}' | while read -r iface; do
  if [[ -n "$iface" ]]; then
    ip netns exec "${NET_NS}" ip link set "$iface" down
    ip netns exec "${NET_NS}" ip link delete "$iface" 2>/dev/null
  fi
done

# Remove all non-loopback routes
ip netns exec "${NET_NS}" ip route | grep -v "lo" | awk '{print $1}' | while read -r route; do
  ip netns exec "${NET_NS}" ip route del "$route" 2>/dev/null
done

echo "All external network interfaces and routes removed from ${NET_NS}. Only loopback remains."
