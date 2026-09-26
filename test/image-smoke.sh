#!/usr/bin/env bash
# Boots a built server image and checks it: starts, datapack enabled, no unexpected log errors, and the
# world survives `docker stop` (the entrypoint must hand SIGTERM to Java for the save to happen).
#   test/image-smoke.sh <image>
set -euo pipefail

IMAGE=${1:?usage: $0 <image>}
ROOT=$(cd "$(dirname "$0")/.." && pwd)
NAME=keel-smoke-$$
PASS=smoke-$$
trap 'docker rm -f "$NAME" >/dev/null 2>&1; docker volume rm "$NAME" >/dev/null 2>&1 || true' EXIT

rcon() { docker exec "$NAME" rcon-cli --password "$PASS" "$@" 2>/dev/null | sed 's/\x1b\[[0-9;]*m//g'; }
wait_up() {
  for _ in $(seq 1 200); do
    rcon list >/dev/null && return 0
    [ "$(docker inspect -f '{{.State.Running}}' "$NAME")" = true ] || break
    sleep 3
  done
  echo "FAIL: server did not come up"; docker logs --tail 50 "$NAME"; exit 1
}

docker run -d --name "$NAME" -e RCON_PASSWORD="$PASS" -e MEMORY_SIZE=3G -v "$NAME:/data" "$IMAGE" >/dev/null
wait_up
echo "== started"

FAIL=0
if rcon 'datapack list enabled' | grep -q 'file/keel-and-cloud'; then
  echo "== datapack enabled"
else
  echo "FAIL: keel-and-cloud datapack not enabled"; FAIL=1
fi

echo "== unexpected log errors (allowlist: test/known-log-errors.txt)"
if docker logs "$NAME" 2>&1 | grep -E '/ERROR\]' | grep -vEf <(grep -vE '^\s*(#|$)' "$ROOT/test/known-log-errors.txt"); then
  FAIL=1
else
  echo "none"
fi

rcon 'forceload add 0 0' >/dev/null
rcon 'setblock 0 250 0 minecraft:gold_block' >/dev/null
docker stop -t 120 "$NAME" >/dev/null
docker start "$NAME" >/dev/null
wait_up
if rcon 'execute if block 0 250 0 minecraft:gold_block' | grep -q 'Test passed'; then
  echo "== world saved on docker stop"
else
  echo "FAIL: world changes lost on docker stop"; FAIL=1
fi

[ $FAIL = 0 ] && echo "PASS" || { echo "FAIL"; exit 1; }
