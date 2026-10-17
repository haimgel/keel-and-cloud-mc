# Reward of advancement keel:momster/ate_pork: runs as and at the player who ate.
advancement revoke @s only keel:momster/ate_pork

# On Peaceful she would vanish the moment she spawned.
execute store result score #difficulty keel.momster run difficulty
execute if score #difficulty keel.momster matches 0 run return 0

# One Momster per player per 5 minutes (6000 ticks), longer than she stays, or a stack of porkchops summons a crowd.
execute store result score #now keel.momster run time query gametime
scoreboard players operation #since keel.momster = #now keel.momster
execute if score @s keel.momster matches -2147483648.. run scoreboard players operation #since keel.momster -= @s keel.momster
execute if score @s keel.momster matches -2147483648.. if score #since keel.momster matches ..5999 run return 0
scoreboard players operation @s keel.momster = #now keel.momster

# Behind the player, then beside, then in front: the first spot with room to stand and a floor.
# Blocks of a Sable ship are not at their world coordinates, so on a ship every spot fails and she appears on the player.
execute rotated ~ 0 positioned ^ ^ ^-3 align xyz positioned ~0.5 ~ ~0.5 if block ~ ~ ~ #keel:momster_room if block ~ ~1 ~ #keel:momster_room unless block ~ ~-1 ~ #minecraft:replaceable unless block ~ ~-1 ~ #keel:momster_room run return run function keel:momster/appear
execute rotated ~ 0 positioned ^3 ^ ^ align xyz positioned ~0.5 ~ ~0.5 if block ~ ~ ~ #keel:momster_room if block ~ ~1 ~ #keel:momster_room unless block ~ ~-1 ~ #minecraft:replaceable unless block ~ ~-1 ~ #keel:momster_room run return run function keel:momster/appear
execute rotated ~ 0 positioned ^-3 ^ ^ align xyz positioned ~0.5 ~ ~0.5 if block ~ ~ ~ #keel:momster_room if block ~ ~1 ~ #keel:momster_room unless block ~ ~-1 ~ #minecraft:replaceable unless block ~ ~-1 ~ #keel:momster_room run return run function keel:momster/appear
execute rotated ~ 0 positioned ^ ^ ^3 align xyz positioned ~0.5 ~ ~0.5 if block ~ ~ ~ #keel:momster_room if block ~ ~1 ~ #keel:momster_room unless block ~ ~-1 ~ #minecraft:replaceable unless block ~ ~-1 ~ #keel:momster_room run return run function keel:momster/appear
function keel:momster/appear
