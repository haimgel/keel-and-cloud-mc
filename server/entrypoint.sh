#!/usr/bin/env bash
# Prepares /data from the image, then replaces itself with the server process so the container's SIGTERM
# reaches Minecraft directly and the world is saved on shutdown.
set -euo pipefail

IMAGE=/opt/minecraft/server
cd /data

# Owned by the image and replaced on every start, so the server always runs exactly the image's pack.
# Edits made to these on the live server are lost on restart: change them in the pack instead.
rm -rf libraries mods config world/datapacks/keel-and-cloud
ln -s "$IMAGE/libraries" libraries
ln -s "$IMAGE/mods" mods
cp -a "$IMAGE/config" config
mkdir -p world/datapacks
cp -a "$IMAGE/world/datapacks/keel-and-cloud" world/datapacks/

# Owned by the operator: written once, then left alone.
if [ ! -f server.properties ]; then
  cp /opt/minecraft/server.properties server.properties
  if [ -n "${RCON_PASSWORD:-}" ]; then
    printf 'enable-rcon=true\nrcon.port=%s\nrcon.password=%s\n' "$RCON_PORT" "$RCON_PASSWORD" >> server.properties
  fi
fi
echo 'eula=true' > eula.txt

exec java -Xms"$MEMORY_SIZE" -Xmx"$MEMORY_SIZE" $JAVA_FLAGS @"$IMAGE/unix_args.txt" nogui
