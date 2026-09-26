#!/usr/bin/env bash
# Creates (or updates) the Prism Launcher instance "keel-and-cloud-dev". It syncs itself from the local
# manifest on every launch, so `packwiz serve` must be running (test/serve.sh) when the game starts.
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
PRISM="$HOME/Library/Application Support/PrismLauncher"
INST="$PRISM/instances/keel-and-cloud-dev"
MC=$(sed -n 's/^minecraft = "\(.*\)"/\1/p' "$ROOT/pack/pack.toml")
NEOFORGE=$(sed -n 's/^neoforge = "\(.*\)"/\1/p' "$ROOT/pack/pack.toml")
JAVA=$(/usr/libexec/java_home -v 21)/bin/java

mkdir -p "$INST/minecraft" "$ROOT/build/cache"
[ -f "$ROOT/build/cache/packwiz-installer-bootstrap.jar" ] || curl -fsSL -o "$ROOT/build/cache/packwiz-installer-bootstrap.jar" \
  https://github.com/packwiz/packwiz-installer-bootstrap/releases/latest/download/packwiz-installer-bootstrap.jar
cp "$ROOT/build/cache/packwiz-installer-bootstrap.jar" "$INST/minecraft/"

cat > "$INST/mmc-pack.json" <<EOF
{
  "components": [
    { "uid": "net.minecraft", "version": "$MC", "important": true },
    { "uid": "net.neoforged", "version": "$NEOFORGE" }
  ],
  "formatVersion": 1
}
EOF

# Only the keys this instance needs; Prism fills in defaults for the rest.
cat > "$INST/instance.cfg" <<EOF
InstanceType=OneSix
name=Keel & Cloud (dev)
OverrideJavaLocation=true
JavaPath=$JAVA
OverrideMemory=true
MinMemAlloc=2048
MaxMemAlloc=6144
OverrideCommands=true
PreLaunchCommand="\$INST_JAVA" -jar packwiz-installer-bootstrap.jar -g http://127.0.0.1:8765/pack.toml
LogPrePostOutput=true
EOF
echo "Prism instance ready: $INST"
