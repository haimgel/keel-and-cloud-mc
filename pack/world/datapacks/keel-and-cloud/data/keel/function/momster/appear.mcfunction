# Runs at the spawn spot. A vanilla witch, so clients need nothing: she attacks the nearest player on her own.
summon witch ~ ~ ~ {CustomName:'"Momster"',CustomNameVisible:1b,Tags:["keel.momster"]}
particle minecraft:witch ~ ~1 ~ 0.3 0.6 0.3 0 40
playsound minecraft:entity.witch.celebrate hostile @a[distance=..32] ~ ~ ~ 1 1
tellraw @a[distance=..32] [{"text":"<Momster> ","color":"dark_purple"},{"text":"Don't eat non-kosher food!","color":"white"}]
return 1
