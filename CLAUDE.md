# Keel & Cloud

A NeoForge 1.21.1 modpack built around Create Aeronautics (physics airships and submarines), with Ars
Nouveau as the magic side. One packwiz manifest produces both the client pack and the dedicated server.

## Design rules

These decide what gets added or removed. Check a proposed mod against them before adding it.

- **Close to vanilla.** No questlines, skill trees or progression systems.
- **One mod per job.** No overlapping mods (one magic system, one storage mod, one map).
- **Solid and supported.** Maintained mods on both Modrinth and CurseForge; no alphas, no broken ports.
- **Magic meets tech through Create.** Create machines process Ars materials, but everything that costs
  Source (imbuing, essences, the Enchanting Apparatus) stays in Ars. A Create recipe that produces Source
  gems or essences turns Ars into a reskin of Create.
- **Travel is by ship.** No waystones or teleport mods; airships and submarines are how players get around.

## Layout

| Path | What |
|---|---|
| `pack/` | packwiz manifest. `pack/mods/*.pw.toml` is one file per mod |
| `pack/world/datapacks/keel-and-cloud/` | Our datapack: Create recipes for Ars items, YUNG's monument height |
| `server/` | Server image: `Dockerfile`, `entrypoint.sh`, default `server.properties` |
| `.github/workflows/image.yml` | Builds, boot-tests and publishes the image to ghcr.io |
| `test/` | Server test harness and checks |
| `Makefile` | `make mrpack` (the file players import), `make test`, `make smoke` |
| `README.md` | For players and friends: what the pack is, how to install it |
| `build/`, `dist/` | Test server, caches, built `.mrpack` files (gitignored) |

## Working on the pack

packwiz is installed with `mise exec go@1.26.7 -- go install github.com/packwiz/packwiz@latest`
(binary: `~/.local/share/mise/installs/go/1.26.7/bin/packwiz`). Run it from `pack/`.

- Add a mod by pinned version: `packwiz mr add https://modrinth.com/mod/<slug>/version/<id>`, then
  `packwiz pin <slug>`. Every mod is pinned so `packwiz update --all` never moves anything silently.
- packwiz does not understand Modrinth's `client_only_server_optional` / `server_only_client_optional` and
  marks such mods `both`. Set `side` by hand: client-only mods (Sodium, Xaero's maps) must be `client`, or
  the dedicated server may refuse to start.
- Some mods declare dependencies only in their jar, not on Modrinth (Ars Nouveau needs Curios and
  GeckoLib). The server boot test catches a missing one.
- After editing files outside `mods/`, run `packwiz refresh`.

## The datapack

- It ships inside the pack at `world/datapacks/` and reaches the server's world before the first start:
  the image entrypoint copies it in, and packwiz does the same for the test server. That only works with
  `level-name=world`. Clients get the recipes synced from the
  server; singleplayer worlds do not get the datapack.
- **Worldgen overrides only apply to chunks generated after they are in place.** Changing
  `data/betteroceanmonuments/...` on a live server affects new terrain only.
- `ocean_monument.json` is YUNG's file with only `start_height` changed. Tectonic's `monument_offset` only
  moves vanilla monuments, and YUNG's replaces them, so without this override monuments float 8–12 blocks
  above Tectonic's deeper sea floor. `start_height` 30–40 was chosen by measurement (`test/monuments.py`):
  higher leaves monuments floating or breaking the surface; `project_start_to_heightmap` samples one
  corner and is worse. Re-measure if Tectonic's ocean settings or YUNG's change.

## Shipped configs

Files under `pack/config/` are installed on every sync and overwrite local edits. Start each from the
file the mod generates, change only the keys that matter, and keep the default comments so diffs stay
readable.

| File | Changed | Why |
|---|---|---|
| `create_submarine-common.toml` | `disableStartupScreens = true` | Players would otherwise get a "configure the mod" prompt for settings the server controls |
| `options.txt` | Music volume 25% | Default only: marked `preserve = true` in `index.toml`, so it is installed when missing and never overwrites a player's own settings |

`preserve` has no meaning in a `.mrpack`: overrides are applied on import, which is always a fresh instance.

`options.txt` holds only the keys we set; Minecraft fills in the rest. Keep its `version:` line at the
Minecraft data version (3955 for 1.21.1), or Minecraft runs its old-format upgrade over the file. The
`preserve` flag lives only in `index.toml`, so check it is still there after editing the file.

Keep `enableDeeperOceans = false` in the Deep Seas config: Tectonic already deepens oceans, and the
YUNG's monument height above is calibrated to Tectonic's sea floor alone.

## Server image

Pins for the build tools are ARGs at the top of `server/Dockerfile`; NeoForge comes from `pack.toml`.

- **Ubuntu base, not Alpine.** Sable extracts native physics libraries built against glibc.
- **The entrypoint must `exec` Java.** Minecraft saves the world in its SIGTERM shutdown hook; a shell in
  between swallows the signal and `docker stop` loses everything since the last autosave.
  `test/image-smoke.sh` checks this with a block placed before the stop.
- **Image-owned vs operator-owned files.** Mods, libraries, `config/` and our datapack are replaced from
  the image on every start, so a server always matches its image tag. `server.properties`, ops, whitelist
  and the world are written once and then left to the operator.
- `allow-flight=true` is required: players standing on a moving ship otherwise get kicked for flying.
- The NeoForge install stays cached across pack changes because only the extracted version string is
  copied into its stage. Keep it that way; a full `COPY pack/` there makes every build reinstall NeoForge.

## Releasing

Bump `version` in `pack/pack.toml`, commit, tag `v<version>`, push the tag. CI publishes
`ghcr.io/haimgel/keel-and-cloud-mc:<version>` and `:latest`. Build the matching `.mrpack` with
`make mrpack` from the same commit and share it; players and server must run the same version.

## Testing

```sh
test/server-test.sh --fresh-world --keep-running   # install pack, boot, check log + datapack
python3 test/monuments.py                          # monument placement against the Tectonic sea floor
python3 test/rcon.py 'command' ...                 # console commands on the running test server
make smoke                                         # build the image and boot-test it, as CI does
```

- `--fresh-world` is required after any worldgen change.
- The test server runs with `max-tick-time=-1`: force-loading many monument areas generates them in one
  tick and trips the watchdog. The production server keeps the default.
- `test/known-log-errors.txt` lists log errors known to be harmless, each with a reason. A new error in
  the server test means something changed; do not allowlist it without finding out what.

## Version decisions

Pins live in `pack/mods/*.pw.toml`. Record here only what was deliberately not taken, and when to revisit.

| Mod | Decision | Revisit when |
|---|---|---|
| Create Deep Seas | Pinned 2.2.4, the first release that starts on a dedicated server. 3.0 (physics rewrite, High Seas module) is pending upstream | 3.0 is released: back up the world, test on a copy first |
| Sodium | 0.8.13. Sable rejects anything below 0.8.12-alpha.2; Deep Seas rejects 0.6.13 | A Sable or Deep Seas release changes its declared Sodium range |
| Create: Ars Nouveau Compat | Not taken: despite the name, its recipes mill finished Ars blocks back into scrap and it needs Create: Compat Core | Never, unless it starts making Ars items |
| Iron's Spells, Northstar, Power Grid, Waystones, Immersive Aircraft | Not taken: duplicate systems, progression, or teleporting | The design rules change |
| Simple Voice Chat | Removed: players use Discord. Proximity voice is the only thing lost, and the server needs no extra UDP port | Players want positional voice in-game |
