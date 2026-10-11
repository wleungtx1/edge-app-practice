#!/usr/bin/env bash
# Build the stand-in Linux installer: a self-extracting EdgeApp-practice-<version>.run plus its
# .sha256. The real repo builds its .run here; this one only packs app/ and requirements.txt.
#
# Usage: installer/build_run.sh VERSION [OUTDIR]
set -euo pipefail

version="${1:?usage: build_run.sh VERSION [OUTDIR]}"
outdir="${2:-dist}"
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
name="EdgeApp-practice-${version}.run"

mkdir -p "$outdir"
payload="$(mktemp)"
trap 'rm -f "$payload"' EXIT

tar -czf "$payload" -C "$root" --exclude='__pycache__' app templates requirements.txt
sed "s/@VERSION@/${version}/" "$root/installer/run_header.sh" > "$outdir/$name"
cat "$payload" >> "$outdir/$name"
chmod +x "$outdir/$name"

(cd "$outdir" && sha256sum "$name" > "$name.sha256")
echo "Built $outdir/$name"
cat "$outdir/$name.sha256"
