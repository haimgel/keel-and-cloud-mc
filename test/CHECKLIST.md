# Hands-on test checklist

For a person playing the dev client against the test server. Ordered by risk: stop and report at the
first failure in sections 1–2, they decide whether the pack can ship as designed.

## Setup

```sh
test/server-test.sh --fresh-world --keep-running   # terminal 1: test server on localhost
test/serve.sh                                      # terminal 2: serves the pack to the client
test/client-instance.sh                            # once: creates the Prism instance
```

Launch "Keel & Cloud (dev)" in Prism, join `localhost`. Op yourself from a terminal:
`python3 test/rcon.py 'op <name>'`. Use creative for building, survival for the gameplay checks.

Most rigs can be built from the console instead of by hand, so the player only has to look:

```sh
python3 test/rcon.py 'fill ...' 'sable assemble area <from> <to>'             # blocks → physics object
python3 test/rcon.py 'execute as <player> at @s run sable info @n'             # nearest ship: id, pose, velocity
python3 test/rcon.py 'sable teleport <uuid> <x> <y> <z> 0 0'                   # move and level it
python3 test/rcon.py 'sable physics impulse <uuid> linear 800 0 0 global'      # push it
python3 test/rcon.py 'simulated lock <uuid> true'                              # freeze it for inspection
```

Put the lift above the centre of mass (balloons, ballast tanks on the roof). A deck on levitite is balanced
like a pencil on its tip and rolls over at the first push; that is correct physics, not a bug.

When something fails, keep `minecraft/logs/latest.log` from the Prism instance and the server's
`build/server/logs/latest.log`.

## 1. Sodium with physics ships

Do each check with Sodium, then again without it (move `sodium-*.jar` out of the instance's `mods/` and
launch Minecraft from Prism's folder without the pre-launch sync, or the sync puts it back). The two
runs should look the same.

- [ ] Assemble a small Aeronautics airship (propeller, hot air, or levitite). It renders while flying, with no
      missing faces, flicker, or blocks left behind at the old position.
- [ ] Walk around on the ship while it moves. No jitter or falling through.
- [ ] Create machines on the ship (a running mechanical bearing or fan) keep animating while it moves.
- [ ] Look at the ship from 100+ blocks away and fly it out of view and back. It stays visible and
      correct.
- [ ] F3 frame rate with Sodium is clearly higher than without. Note both numbers.

## 2. Submarines (Create Deep Seas) on the dedicated server

- [ ] Build a sealed submarine and dive. The interior stays dry and you can breathe inside.
- [ ] Ballast tanks change depth; the propeller moves the submarine.
- [ ] Below a few dozen blocks, pressure matters as the mod describes (hull damage or a warning).
- [ ] Water rendering inside and around the submarine is correct with Sodium (no water drawn inside the
      hull).
- [ ] Leave the submarine underwater, log out, log back in. It is where you left it, still dry inside.

## 3. Ars Nouveau with Create and ships

- [ ] JEI shows our recipes: Millstone magebloom → fiber, Millstone sourceberry bush → purple dye, Mixer
      stone + source gem → sourcestone, Compactor paper + 6 fiber → blank parchment. Run each in a machine.
- [ ] A Mechanical Arm puts items onto an Arcane Pedestal and takes the result off the Enchanting
      Apparatus (Create: Ars Compat).
- [ ] Ars Creo Starbuncle Wheel produces rotation.
- [ ] Spell turret and source jar on an assembled airship still work (Ars Creo).
- [ ] Cast a Blink spell on a moving airship and near it. You land where expected and nothing breaks.

## 4. The rest

- [ ] Create Big Cannons: a cannon mounted on an airship fires, and shots carry the ship's velocity.
- [ ] Effortless Building: build a wall in survival on the ground, then on an assembled ship.
- [ ] Fly over an ocean monument (`/locate structure betteroceanmonuments:ocean_monument`). It sits on the
      sea floor, not floating, and nothing sticks out of the water.
- [ ] Explore a mineshaft under deep ocean. No mineshaft planks or rails poking out of the ocean floor.
- [ ] Biomes O' Plenty biomes and Tectonic terrain look coherent: no hard biome edges, no cut-off
      mountains.
