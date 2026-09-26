#!/usr/bin/env bash
# Serves pack/ on http://127.0.0.1:8765/pack.toml for the dev client instance and the test server.
set -euo pipefail
cd "$(dirname "$0")/../pack"
PACKWIZ=${PACKWIZ:-$(command -v packwiz || echo "$HOME/.local/share/mise/installs/go/1.26.7/bin/packwiz")}
"$PACKWIZ" refresh
exec "$PACKWIZ" serve --port 8765
