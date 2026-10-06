#!/bin/bash
# Deploy device-reach into the runtime dir (~/.sigspace-reach by default) and install deps.
set -euo pipefail
DEST="${1:-$HOME/.sigspace-reach}"
SRC="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$DEST/drivers" "$DEST/data"
cp "$SRC/app.py" "$SRC/requirements.txt" "$SRC/README.md" "$SRC/panel.html" "$SRC/reach_nodes.example.json" "$DEST/"
cp "$SRC/.gitignore" "$DEST/.gitignore" 2>/dev/null || true
cp "$SRC/drivers/"*.py "$DEST/drivers/"
cp "$SRC/data/"*.json "$DEST/data/" 2>/dev/null || true
[ -d "$DEST/.venv" ] || python3 -m venv "$DEST/.venv"
"$DEST/.venv/bin/pip" install -q -r "$DEST/requirements.txt"
echo "deployed device-reach -> $DEST (DISARMED; passive scan on). Reload launchd to apply."
