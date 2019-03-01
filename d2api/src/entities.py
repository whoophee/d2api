#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import shutil

import requests

# TODO : Implement cleaner way to ensure data is up to date and multi-language compliant
# This appears to be an especially weird problem since the data has to parsed from a local Dota 2 installation

_here = os.path.abspath(os.path.dirname(__file__))

def _ensure_data_folder():
    """Helper method to ensure data folder existence."""
    directory = os.path.abspath(os.path.join(_here, '..', 'ref'))
    if not os.path.exists(directory):
        os.makedirs(directory)

def _load_local_json(file_name):
    """Helper method to read local data."""
    try:
        p = os.path.abspath(os.path.join(_here, '..', 'ref', file_name))
        with open(p, 'r') as f:
            return json.load(f)
    except IOError:
        return {}

def _load_remote_json(file_name):
    """Helper method to retrieve remote data."""
    url = "https://raw.githubusercontent.com/whoophee/d2api/master/d2api/ref/{}".format(file_name)
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()
    else: # pragma: no cover
        return {}

def _write_local_json(data, file_name):
    """Helper method to write local data."""
    p = os.path.abspath(os.path.join(_here, '..', 'ref', file_name))
    with open(p, 'w') as outfile:
        if file_name == 'meta.json':
            json.dump(data, outfile, sort_keys=True, indent=4)
        else:
            json.dump(data, outfile)

all_heroes = _load_local_json('heroes.json')
all_items = _load_local_json('items.json')
all_abilities = _load_local_json('abilities.json')


# Most ID based response values have more data associated with them.
# This wrapper helps fetch them without having to use auxillary/helper functions.
class Entity(dict):
    """Generic entity class"""
    def __str__(self):
        return self.__repr__()

class Hero(Entity):
    """Wrapper to map hero information to hero_id

    Attributes
    ----------
    hero_id : int
        Unique identifier of hero
    hero_name : str
        Name of the hero
    """
    def __repr__(self):
        return "Hero(hero_id = {})".format(self['hero_id'])

    def __bool__(self):
        return self['hero_id'] != None

    def __init__(self, hero_id):
        if hero_id != None:
            hero_id = str(hero_id)
        self['hero_id'] = hero_id
        cur_hero = all_heroes.get(hero_id, {})
        self['hero_name'] = cur_hero.get('hero_name', 'unknown_hero')


class Item(Entity):
    """Wrapper to map item information to item_id

    Attributes
    ----------
    item_id : int
        Unique identifier of item
    item_cost : int
        Cost of the item
    item_aliases : list(str)
        List of names by which the item is known
    item_name : str
        Name of the item
    """
    def __repr__(self):
        return "Item(item_id = {})".format(self['item_id'])

    def __bool__(self):
        return self['item_id'] != None

    def __init__(self, item_id):
        if item_id != None:
            item_id = str(item_id)
        self['item_id'] = item_id
        cur_item = all_items.get(item_id, {})
        self['item_cost'] = cur_item.get('item_cost', 0)
        self['item_aliases'] = cur_item.get('item_aliases', [])
        self['item_name'] = cur_item.get('item_name', 'unknown_item')

class Ability(Entity):
    """Wrapper to map ability data to ability_id

    Attributes
    ----------
    ability_id : int
        Unique identifier of ability
    ability_name : str
        Name of the ability
    """
    def __repr__(self):
        return "Ability(ability_id = {})".format(self['ability_id'])

    def __bool__(self):
        return self['ability_id'] != None

    def __init__(self, ability_id):
        if ability_id != None:
            ability_id = str(ability_id)
        self['ability_id'] = ability_id
        cur_ability = all_abilities.get(ability_id, {})
        self['ability_name'] = cur_ability.get('ability_name', 'unknown_ability')

# Removes the hassle of having to manually convert between Steam 32-bit/64-bit IDs
class SteamAccount(Entity):
    """Wrapper to implicitly store steam32 and steam64 account IDs

    Attributes
    ----------
    id32 : int
        32-bit Steam ID
    id64 : int
        64-bit Steam ID
    """
    def __repr__(self):
        return "SteamAccount(account_id = {})".format(self['id32'])

    def __bool__(self):
        return self['id32'] != None

    def __init__(self, account_id):
        if account_id is None:
            self['id32'] = self['id64'] = None
        else:
            account_id = int(account_id)
            steam64 = 76561197960265728
            if account_id < steam64:
                self['id32'] = account_id
                self['id64'] = account_id + steam64
            else:
                self['id32'] = account_id - steam64
                self['id64'] = account_id

def _update(purge):
    """Helper function to synchronize local with remote data."""
    global all_heroes
    global all_items
    global all_abilities
    try:
        path = os.path.abspath(os.path.join(_here, '..', 'ref'))
        if purge and os.path.exists(path):
            shutil.rmtree(path)
        # Find version of local data
        local_meta = _load_local_json('meta.json')
        local_version = local_meta.get('version')
        # find version of remote data
        remote_meta = _load_remote_json('meta.json')
        remote_version = remote_meta.get('version')

        # update local files if they're outdated
        if local_version != remote_version:
            _ensure_data_folder()
            _write_local_json(remote_meta, "meta.json")

            for content_name in remote_meta.get('content_files', []):
                remote_content = _load_remote_json(content_name)
                _write_local_json(remote_content, content_name)

        all_heroes = _load_local_json('heroes.json')
        all_items = _load_local_json('items.json')
        all_abilities = _load_local_json('abilities.json')
        return remote_meta
    except Exception as e: # pragma: no cover
        return {"exception":e}
