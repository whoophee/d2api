from pathlib import Path
import json

def load_json(file_name):
    try:
        f = open(Path('../../../data/{}'.format(file_name)), 'r')
        return json.load(f)
    except IOError:
        return None

def get_hero(hero_id):
    ret = all_heroes.get(hero_id)
    return ret if ret else Hero(hero_id, "Unknown hero")

def get_item(item_id):
    ret = all_items.get(item_id)
    return ret if ret else Item(item_id, "Unknown item")

def get_ability(ability_id):
    ret = all_abilities.get(ability_id)
    return ret if ret else Ability(ability_id, "Unknown ability")

def get_side(player_slot):
    return "radiant" if player_slot < 128 else "dire"


class Hero:
    def __eq__(self, other):
        if self.__class__.__name__ == other.__class__.__name__:
            return self.hero_id == other.hero_id and self.hero_name == other.hero_name
        return False

    def __repr__(self):
        return "<Hero {}>".format({'hero_id':self.hero_id, 'hero_name':self.hero_name})

    def __init__(self, hero_id = None, hero_name = None):
        self.hero_id = hero_id
        self.hero_name = hero_name

class Item:
    def __eq__(self, other):
        if self.__class__.__name__ == other.__class__.__name__:
            return self.item_id == other.item_id and self.item_name == other.item_name
        return False

    def __repr__(self):
        return "<Item {}>".format({'item_id':self.item_id, 'item_name':self.item_name})

    def __init__(self, item_id = None, item_name = None):
        self.item_id = item_id
        self.item_name = item_name

class Ability:
    def __eq__(self, other):
        if self.__class__.__name__ == other.__class__.__name__:
            return self.ability_id == other.ability_id and self.ability_name == other.ability_name
        return False

    def __repr__(self):
        return "<Ability {}>".format({'ability_id':self.ability_id, 'ability_name':self.ability_name})

    def __init__(self, ability_id = None, ability_name = None):
        self.ability_id = ability_id
        self.ability_name = ability_name

class SteamAccount:
    def __eq__(self, other):
        if self.__class__.__name__ == other.__class__.__name__:
            return self.id64 == other.id64 and self.id32 == other.id32
        return False
        
    def __repr__(self):
        return "<SteamAccount {}>".format({'id32':self.id32, 'id64':self.id64})

    def __init__(self, account_id = None):
        if account_id is None:
            self.id32 = self.id64 = None
        else:
            steam64 = 76561197960265728
            if account_id < steam64:
                self.id32 = account_id
                self.id64 = account_id + steam64
            else:
                self.id32 = account_id - steam64
                self.id64 = account_id


all_heroes = {}
all_items = {}
all_abilities = {}
