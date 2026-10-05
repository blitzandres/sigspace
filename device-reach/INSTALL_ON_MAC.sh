#!/bin/bash
set -euo pipefail
ROOT="${1:-/Users/andresblitz/Documents/sigspace}"
SRC="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$ROOT/device-reach/drivers"
cp "$SRC/app.py" "$SRC/requirements.txt" "$SRC/README.md" "$ROOT/device-reach/"
cp "$SRC/drivers/"*.py "$ROOT/device-reach/drivers/"
python3 -m pip install -q -r "$ROOT/device-reach/requirements.txt"
echo "installed device-reach into $ROOT/device-reach"
