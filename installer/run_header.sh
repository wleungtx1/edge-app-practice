#!/usr/bin/env bash
# EdgeApp-practice @VERSION@ — stand-in self-extracting installer.
# Usage: ./EdgeApp-practice-@VERSION@.run [TARGET_DIR]
# The gzipped tar payload starts on the line after the __PAYLOAD_BELOW__ marker.
set -euo pipefail

target="${1:-./edge-app-practice}"
mkdir -p "$target"
line="$(awk '/^__PAYLOAD_BELOW__$/ { print NR + 1; exit 0 }' "$0")"
tail -n +"$line" "$0" | tar -xz -C "$target"
echo "EdgeApp-practice @VERSION@ extracted to $target"
exit 0
# shellcheck disable=SC2317  # marker line, never executed; the payload follows it
__PAYLOAD_BELOW__
