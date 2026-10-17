# Every 5 seconds. Each Momster goes home after 3 minutes, so none linger around a base.
scoreboard players add @e[type=witch,tag=keel.momster] keel.momster_age 5
execute as @e[type=witch,tag=keel.momster,scores={keel.momster_age=180..}] at @s run function keel:momster/leave
schedule function keel:momster/age 5s replace
