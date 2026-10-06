#!/bin/bash
set -euo pipefail
ROOT="${1:-/Users/andresblitz/Documents/sigspace}"
SRC="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$ROOT/device-reach/drivers"
cp "$SRC/app.py" "$SRC/requirements.txt" "$SRC/README.md" "$SRC/reach_nodes.example.json" "$ROOT/device-reach/"
cp "$SRC/.gitignore" "$ROOT/device-reach/.gitignore" 2>/dev/null || true
cp "$SRC/drivers/"*.py "$ROOT/device-reach/drivers/"
[ -f "$SRC/../NOTICE-device-reach.md" ] && cp "$SRC/../NOTICE-device-reach.md" "$ROOT/" || true
python3 -m pip install -q -r "$ROOT/device-reach/requirements.txt"
echo "installed device-reach into $ROOT/device-reach (starts DISARMED; arm with POST /api/arm)"
