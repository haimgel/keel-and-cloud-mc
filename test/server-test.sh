#!/usr/bin/env bash
# Installs the pack into build/server exactly as the real server will, boots it headless,
# and fails on crashes, unexpected log errors, or a missing datapack.
#   test/server-test.sh [--fresh-world] [--keep-running]
# --fresh-world is required after any worldgen change: worldgen datapacks only apply to new worlds.
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
SERVER=$ROOT/build/server
NEOFORGE=$(sed -n 's/^neoforge = "\(.*\)"/\1/p' "$ROOT/pack/pack.toml")
JAVA_HOME=${JAVA_HOME:-$(/usr/libexec/java_home -v 21)}
PACKWIZ=${PACKWIZ:-$(command -v packwiz || echo "$HOME/.local/share/mise/installs/go/1.26.7/bin/packwiz")}
PORT=8765
FRESH=0 KEEP=0
for a in "$@"; do
  case $a in
    --fresh-world) FRESH=1 ;;
    --keep-running) KEEP=1 ;;
    *) echo "unknown option: $a" >&2; exit 2 ;;
  esac
done

mkdir -p "$SERVER" "$ROOT/build/cache"
cd "$ROOT/build/cache"
[ -f packwiz-installer-bootstrap.jar ] || curl -fsSLO https://github.com/packwiz/packwiz-installer-bootstrap/releases/latest/download/packwiz-installer-bootstrap.jar
if [ ! -f "$SERVER/libraries/net/neoforged/neoforge/$NEOFORGE/unix_args.txt" ]; then
  curl -fsSL -o neoforge-installer.jar "https://maven.neoforged.net/releases/net/neoforged/neoforge/$NEOFORGE/neoforge-$NEOFORGE-installer.jar"
  (cd "$SERVER" && "$JAVA_HOME/bin/java" -jar "$ROOT/build/cache/neoforge-installer.jar" --install-server . >/dev/null)
fi

cd "$SERVER"
if [ -f .rcon-pass ] && python3 "$ROOT/test/rcon.py" -p .rcon-pass stop >/dev/null 2>&1; then
  echo "== stopping the previous test server"
  while pgrep -f "$SERVER" >/dev/null || pgrep -f "neoforge/$NEOFORGE/unix_args.txt" >/dev/null; do sleep 1; done
fi
if [ ! -f server.properties ]; then
  cp "$ROOT/test/server.properties" server.properties
  echo "rcon.password=$(openssl rand -hex 12)" >> server.properties
fi
sed -n 's/^rcon.password=//p' server.properties > .rcon-pass
echo 'eula=true' > eula.txt
printf -- '-Xms2G\n-Xmx6G\n' > user_jvm_args.txt
[ $FRESH = 1 ] && rm -rf world

# packwiz serve rather than a static file server: the installer fetches in parallel and
# python's http.server drops those connections.
(cd "$ROOT/pack" && "$PACKWIZ" refresh >/dev/null && exec "$PACKWIZ" serve --port $PORT >/dev/null 2>&1) &
SERVE_PID=$!
trap 'kill $SERVE_PID 2>/dev/null || true' EXIT
until curl -fs "http://127.0.0.1:$PORT/pack.toml" >/dev/null; do sleep 0.2; done
"$JAVA_HOME/bin/java" -jar "$ROOT/build/cache/packwiz-installer-bootstrap.jar" -g -s server "http://127.0.0.1:$PORT/pack.toml" \
  | grep -E 'Finished|Failed|error' || true
kill $SERVE_PID 2>/dev/null || true

echo "== booting NeoForge $NEOFORGE"
PATH=$JAVA_HOME/bin:$PATH nohup ./run.sh nogui > console.log 2>&1 < /dev/null &
SERVER_PID=$!
until grep -qE 'Done \(|Crash report|Failed to start|Missing or unsupported mandatory dependencies' console.log 2>/dev/null \
      || ! kill -0 $SERVER_PID 2>/dev/null; do
  sleep 2
done
if ! grep -q 'Done (' console.log; then
  echo "FAIL: server did not start"; grep -E 'Crash report|Failed|mandatory|Exception' console.log | head -20; exit 1
fi
grep -o 'Done ([0-9.]*s)' console.log

FAIL=0
echo "== unexpected log errors (allowlist: test/known-log-errors.txt)"
if grep -E '/ERROR\]' logs/latest.log | grep -vEf <(grep -vE '^\s*(#|$)' "$ROOT/test/known-log-errors.txt"); then
  FAIL=1
else
  echo "none"
fi

echo "== datapack"
if python3 "$ROOT/test/rcon.py" -p .rcon-pass 'datapack list enabled' | grep -q 'file/keel-and-cloud'; then
  echo "keel-and-cloud enabled"
else
  echo "FAIL: keel-and-cloud datapack not enabled"; FAIL=1
fi

if [ $KEEP = 0 ]; then
  python3 "$ROOT/test/rcon.py" -p .rcon-pass stop >/dev/null
  while kill -0 $SERVER_PID 2>/dev/null; do sleep 1; done
fi
[ $FAIL = 0 ] && echo "PASS" || { echo "FAIL"; exit 1; }
