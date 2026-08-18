#!/usr/bin/env bash
# Pick which Ultimate64 subsequent `make` invocations target. Persists in a
# gitignored statefile until changed again (sticky across shells/tabs).
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOSTS_FILE="$DIR/u64-hosts.txt"
STATE_FILE="$DIR/../.ultimate_host"

usage() {
    echo "Usage: $(basename "$0") <name|ip>" >&2
    echo "Known devices:" >&2
    sed 's/^/  /' "$HOSTS_FILE" >&2
    exit 1
}

[ $# -eq 1 ] || usage
arg="$1"

if ip="$(grep "^${arg}=" "$HOSTS_FILE" 2>/dev/null | cut -d= -f2)" && [ -n "$ip" ]; then
    :
else
    ip="$arg"
fi

echo "$ip" > "$STATE_FILE"
echo "Selected Ultimate64: $arg -> $ip (saved to $STATE_FILE)"
