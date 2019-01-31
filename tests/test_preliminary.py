#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest

import d2api
from d2api.src import endpoints
from d2api.src import entities
from d2api.src import errors as d2errors
from d2api.src import wrappers
from d2api import update_local_data

# TODO: A whole lot more test cases

class APIPreliminaryTests(unittest.TestCase):
    def test_environment_api_key_set(self):
        self.assertIsNotNone(os.environ.get('D2_API_KEY'), 
        'D2_API_KEY was not set in environment')

    def test_correct_api_key(self):
        key = 'abcdxyz'
        tmp_api = d2api.APIWrapper(key)

        with self.assertRaises(d2errors.APIAuthenticationError, 
        msg = f'Request with API key \'{key}\' should raise authentication error'):
            tmp_api.get_match_details('4176987886')
    
    def test_insufficient_params(self):
        with self.assertRaises(d2errors.APIInsufficientArguments, msg = "match_id is a required argument for get_match_details"):
            d2api.APIWrapper().get_match_details(match_id = None)
        
    def test_api_method_unavailable(self):
        method_url = 'http://api.steampowered.com/IDOTA2Match_570/RANDOMMETHOD/v0001/'
        with self.assertRaises(d2errors.APIMethodUnavailable, msg = f"{method_url} is an unavailable method."):
            d2api.APIWrapper()._api_call(method_url)

    def test_update_local_files(self):
        remote_meta = update_local_data()
        self.assertNotEqual(remote_meta, {},
        msg = "Update must return remote metadata. Instead, it returned nothing.")

    def test_unparsed_results_dtype(self):
        api = d2api.APIWrapper(parse_results = False)
        self.assertIsInstance(api.get_match_history(), dict,
        msg = 'Setting parse_results = False should return a dict.')

class EntityTests(unittest.TestCase):
    def test_item_repr(self):
        item_repr = repr(entities.Item(3))
        item_match_str = "Item(item_id = 3)"
        self.assertEqual(item_repr, item_match_str, f"repr(entities.Item(3)) should be {item_match_str}")

    def test_hero_repr(self):
        hero_repr = repr(entities.Hero(1))
        hero_match_str = "Hero(hero_id = 1)"
        self.assertEqual(hero_repr, hero_match_str, f"repr(entities.Hero(1)) should be {hero_match_str}")

    def test_ability_repr(self):
        ability_repr = repr(entities.Ability(1))
        ability_match_str = "Ability(ability_id = 1)"
        self.assertEqual(ability_repr, ability_match_str, f"repr(entities.Ability(1)) should be {ability_match_str}")

    def test_steamaccount_repr(self):
        steam_repr = repr(entities.SteamAccount(1))
        steam_match_str = "SteamAccount(account_id = 1)"
        self.assertEqual(steam_repr, steam_match_str, f"repr(entities.SteamAccount(1)) should be {steam_match_str}")
    
    def test_ability_bool(self):
        ability1 = entities.Ability(None)
        ability2 = entities.Ability(2)
        self.assertTrue(not ability1, f"not {ability1} should be True")
        self.assertFalse(not ability2, f"not {ability2} should be False")
    
    def test_hero_bool(self):
        hero1 = entities.Hero(None)
        hero2 = entities.Hero(2)
        self.assertTrue(not hero1, f"not {hero1} should be True")
        self.assertFalse(not hero2, f"not {hero2} should be False")
    
    def test_item_bool(self):
        item1 = entities.Item(None)
        item2 = entities.Item(2)
        self.assertTrue(not item1, f"not {item1} should be True")
        self.assertFalse(not item2, f"not {item2} should be False")
    
    def test_steamaccount_bool(self):
        acct1 = entities.SteamAccount(None)
        acct2 = entities.SteamAccount(2)
        self.assertTrue(not acct1, f"not {acct1} should be True")
        self.assertFalse(not acct2, f"not {acct2} should be False")
    

class DtypeTests(unittest.TestCase):
    def test_steam_32_64(self):
        steam32 = 123456
        steam64 = 76561197960265728 + steam32
        account1 = entities.SteamAccount(account_id = steam64)
        account2 = entities.SteamAccount(account_id = steam32)
        self.assertEqual(account1, account2,
        'SteamAccount created with 32 Bit or 64 Bit SteamID should be indistinguishable')
    
    def test_basewrapper(self):
        obj1 = wrappers.BaseWrapper({'a':1, 'b':2, 'c':3})
        obj2 = wrappers.BaseWrapper({'a':1})
        self.assertNotEqual(obj1, obj2, f'{obj1} and {obj2} are unequal.')
        obj2['b'] = 2
        obj2['c'] = 3
        self.assertEqual(obj1['b'], 2, 'BaseWrapper __getitem__ does not work as intended.')
        with self.assertRaises(KeyError, msg = 'Trying to access non-existent properties should raise KeyError.'):
            obj1['unexpected_key']
