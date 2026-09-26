# Keel & Cloud

![Keel & Cloud: an airship over the sea at dusk, a submarine below](assets/banner.png)

**Build an airship. Fly it across the world. Then build a submarine and go find out what's at the bottom of
the ocean.**

Keel & Cloud is Minecraft with real physics. Anything you build with Create can take off: bolt on
propellers and a balloon, walk around on deck while it flies, mount cannons on the side. Seal a hull, add
ballast tanks and an air supply, and dive past the ocean monuments into the deep. Worlds are bigger and
wilder, with towering mountains, oceans deep enough to be worth a submarine, and dozens of new biomes.
There's magic too: craft your own spells, then wire them into your machines, so a factory can run on
starbuncle power and your airship can carry a spell turret. There are no quests and no skill trees; it
still feels like Minecraft, you just get to go further.

## How to play

You need a launcher that can import modpacks. **[Prism Launcher](https://prismlauncher.org/)** is free and
works on Windows, macOS and Linux; the [Modrinth App](https://modrinth.com/app) works too. The CurseForge
app cannot open this pack.

1. Download `Keel-and-Cloud-<version>.mrpack` from the
   [latest release](https://github.com/haimgel/keel-and-cloud-mc/releases/latest). It is a small file: the
   launcher downloads the mods itself.
2. In Prism: **Add Instance → Import**, choose the file, click **OK**. Wait for the downloads. You can
   rename the instance to "Keel & Cloud" and give it [the icon](assets/icon-256.png) (right-click →
   **Change Icon**).
3. Make Prism use the right Java. The pack needs **Java 21**; a newer Java may be picked and fail. In
   **Settings → Java**, tick **Auto-detect Java version** and **Auto-download Mojang Java**.
4. Give it more memory: right-click the instance → **Edit → Settings → Java**, tick **Memory** and set
   **Maximum memory** to **6144 MB** (at least 4096 MB if your computer has 8 GB or less).
5. Launch and open **Multiplayer**: the Keel & Cloud server (`keel-mc.g8n.me`) is already in the list.

When the pack is updated you will get a new `.mrpack`. Import it as a new instance; your worlds live on the
server, so nothing is lost.

The Create recipes for Ars Nouveau items and the monument fixes only apply on the server. The pack runs in
singleplayer too, just without them.

## What's inside

| | |
|---|---|
| Machines and flight | Create, Create Aeronautics (with Sable physics), Aeroworks controls, Create Big Cannons, Power Loader |
| Under the sea | Create Deep Seas: submarines, pressure, oxygen, and the Abyss |
| Magic | Ars Nouveau, Ars Creo (spells on contraptions), Create: Enchantment Industry |
| World | Biomes O' Plenty, Tectonic terrain, YUNG's better monuments, mineshafts and dungeons |
| Everyday | Farmer's Delight, Sophisticated Backpacks, Corpse, Effortless Building, JEI, Jade, Xaero's maps, Ping Wheel |
| Speed | Sodium, ModernFix, FerriteCore |

The full list with exact versions is in `pack/mods/`.

## For maintainers

The pack is a [packwiz](https://packwiz.infra.link/) manifest. `CLAUDE.md` has the design rules, how to
add or change mods, and why things are the way they are. Read it before changing anything.

```sh
make mrpack   # dist/Keel-and-Cloud-<version>.mrpack, the file to share
make test     # install the pack into a local server on a fresh world and check it boots cleanly
make smoke    # build the server image and boot-test it
```

To release: bump `version` in `pack/pack.toml`, commit, tag `v<version>` and push the tag. CI builds and
tests the server image and publishes it to `ghcr.io/haimgel/keel-and-cloud-mc`. Then attach the `.mrpack`
to the GitHub release: `make mrpack && gh release create v<version> dist/Keel-and-Cloud-<version>.mrpack`.

### Running the server

```sh
docker run -d --name keel -p 25565:25565 -v keel-data:/data \
  -e MEMORY_SIZE=6G -e RCON_PASSWORD=<secret> ghcr.io/haimgel/keel-and-cloud-mc:latest
docker exec keel rcon-cli --password <secret> list
```

| Variable | Default | |
|---|---|---|
| `MEMORY_SIZE` | `6G` | Java heap. Give the container at least 1.5 GB more than this |
| `RCON_PASSWORD` | unset | Enables RCON on port 25575. Only read when `server.properties` is first created |
| `JAVA_FLAGS` | Aikar's G1 flags | Extra JVM flags |

- `/data` holds the world and everything an operator owns: `server.properties`, ops, whitelist, logs.
- Mods, libraries, `config/`, the pack's datapack and the server icon come from the image and are replaced
  on every start.
  Change them in the pack, not on the server.
- `docker stop` saves the world: the entrypoint `exec`s Java so it receives the stop signal. Allow it time
  to finish (Kubernetes: `terminationGracePeriodSeconds` of 60 or more).
