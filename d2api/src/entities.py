#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import shutil
from pathlib import Path

import requests

all_heroes = {}
all_items = {}
all_abilities = {}


def ensure_data_folder():
    directory = Path(os.path.join(os.path.dirname(__file__), '..', 'data'))
    if not os.path.exists(directory):
        os.makedirs(directory)

def load_local_json(file_name):
    try:
        p = Path(os.path.join(os.path.dirname(__file__), '..', 'data', file_name))
        with open(p, 'r') as f:
            return json.load(f)
    except IOError:
        return {}

def load_remote_json(file_name):
    url = f"https://raw.githubusercontent.com/whoophee/d2api/master/d2api/data/{file_name}"
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()
    else:
        return {}

def write_local_json(data, file_name):
    p = Path(os.path.join(os.path.dirname(__file__), '..', 'data', file_name))
    with open(p, 'w') as outfile:
        if file_name == 'meta.json':
            json.dump(data, outfile, sort_keys=True, indent=4)
        else:
            json.dump(data, outfile)


def get_side(player_slot):
    return "radiant" if player_slot < 128 else "dire"

class Entity:
    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        if self.__class__.__name__ == other.__class__.__name__:
            return self.__dict__ == other.__dict__
        return False
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {tuple(list(self.__dict__.values()))}>"

class Hero(Entity):
    def __init__(self, hero_id = None):
        hero_id = str(hero_id)
        self.hero_id = hero_id
        cur_hero = all_heroes.get(hero_id, {})
        self.hero_name = cur_hero.get('hero_name', 'unknown_hero')
        

class Item(Entity):
    def __init__(self, item_id = None):
        item_id = str(item_id)
        self.item_id = item_id
        cur_item = all_items.get(item_id, {})
        self.item_cost = cur_item.get('item_cost', 0)
        self.item_aliases = cur_item.get('item_aliases', [])
        self.item_name = cur_item.get('item_name', 'unknown_item')

class Ability(Entity):
    def __init__(self, ability_id = None):
        ability_id = str(ability_id)
        self.ability_id = ability_id
        cur_ability = all_abilities.get(ability_id, {})
        self.ability_name = cur_ability.get('ability_name', 'unknown_ability')

class SteamAccount(Entity):
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


def _update(purge):
    global all_heroes
    global all_items
    global all_abilities
    try:
        if purge:
            shutil.rmtree(Path(os.path.join(os.path.dirname(__file__), '..', 'data')))
        # Find version of local data
        local_meta = load_local_json('meta.json')
        local_version = local_meta.get('version')

        # find version of remote data
        remote_meta = load_remote_json('meta.json')
        remote_version = remote_meta.get('version')

        # update local files if they're outdated
        if local_version != remote_version:
            ensure_data_folder()
            write_local_json(remote_meta, "meta.json")

            for content_name in remote_meta.get('content_files', []):
                remote_content = load_remote_json(content_name)
                write_local_json(remote_content, content_name)

        all_heroes = load_local_json('heroes.json')
        all_items = load_local_json('items.json')
        all_abilities = load_local_json('abilities.json')
        return remote_meta
    except:
        return {}
