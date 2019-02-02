from d2api.src import entities

# Hero/Item/Ability information is available without having to specify a key
print(entities.Hero(67)['hero_name'])
print(entities.Item(208)['item_aliases'])
print(entities.Ability(6697)['ability_name'])

# Use steam32/steam64 IDs interchangeably
steam_account = entities.SteamAccount(1020002)
print(steam_account['id32'], steam_account['id64'])