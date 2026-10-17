# Out of the world before the kill, so she leaves in a puff of smoke instead of dying and dropping loot.
particle minecraft:witch ~ ~1 ~ 0.3 0.6 0.3 0 40
playsound minecraft:entity.witch.celebrate hostile @a[distance=..32] ~ ~ ~ 1 1
tp @s ~ -1000 ~
kill @s
