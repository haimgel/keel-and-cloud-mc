# keel.momster: game time of a player's last Momster. keel.momster_age: seconds a Momster has been out.
scoreboard objectives add keel.momster dummy
scoreboard objectives add keel.momster_age dummy
schedule function keel:momster/age 5s replace
