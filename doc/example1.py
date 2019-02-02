import d2api
from d2api.src import entities

api = d2api.APIWrapper()

# fetch latest matches
match_history = api.get_match_history()

# get frequency of heroes played in the latest 100 games
heroes = {}

for match in match_history['matches']:
    for player in match['players']:
        hero_id = player['hero']['hero_id']
        if not hero_id in heroes:
            heroes[hero_id] = 0
        heroes[hero_id] += 1

# print hero frequency by name
for hero_id, freq in heroes.items():
    print(entities.Hero(hero_id)['hero_name'], freq)

