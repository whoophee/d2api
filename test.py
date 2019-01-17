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
            d2api.APIWrapper().api_call(endpoints.GET_MATCH_DETAILS, wrappers.MatchDetails)

    def test_logger_check(self):
        tmp_api = d2api.APIWrapper(logging_enabled = True)
        self.assertIsNotNone(tmp_api.logger, 
        'Logger should not be None when \'logging_enabled\' was set to True')

    def test_update_local_files(self):
        self.assertNotEqual(update_local_data(), {},
        msg = "Update must return remote metadata. Instead, it returned an empty dict.")

    def test_unparsed_results_dtype(self):
        self.assertIsInstance(d2api.APIWrapper().api_call(endpoints.GET_MATCH_HISTORY, parse_results = False), dict,
        msg = 'Setting parse_results = False should return a dict.')


class EndpointTests(unittest.TestCase):
    """
    Working endpoints cause 403(authentication) error.
    Enpoints that do not exist/are discontinued cause 404(not found) error.
    """
    def setUp(self):
        api = d2api.APIWrapper(api_key = "0000")
        self.api_call = api.api_call

    def test_get_match_history_endpoint(self):
        with self.assertRaises(d2errors.APIAuthenticationError, msg = "GET_MATCH_HISTORY endpoint is not working as intended."):
            self.api_call(endpoints.GET_MATCH_HISTORY, wrappers.MatchHistory)
    
    def test_get_match_history_by_seq_num_endpoint(self):
        with self.assertRaises(d2errors.APIAuthenticationError, msg = "GET_MATCH_HISTORY_BY_SEQ_NUM endpoint is not working as intended."):
            self.api_call(endpoints.GET_MATCH_HISTORY_BY_SEQ_NUM, wrappers.MatchHistory)
    
    def test_get_match_details_endpoint(self):
        with self.assertRaises(d2errors.APIAuthenticationError, msg = "GET_MATCH_DETAILS endpoint is not working as intended."):
            self.api_call(endpoints.GET_MATCH_DETAILS, wrappers.MatchDetails, match_id = '123')
    
    def test_get_heroes_endpoint(self):
        with self.assertRaises(d2errors.APIAuthenticationError, msg = "GET_HEROES endpoint is not working as intended."):
            self.api_call(endpoints.GET_HEROES, wrappers.Heroes)
    
    def test_get_game_items_endpoint(self):
        with self.assertRaises(d2errors.APIAuthenticationError, msg = "GET_GAME_ITEMS endpoint is not working as intended."):
            self.api_call(endpoints.GET_GAME_ITEMS, wrappers.GameItems)

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
        obj2.b = 2
        obj2['c'] = 3
        self.assertEqual(obj1.a, 1, 'BaseWrapper __getattr__ does not work as intended.')
        self.assertEqual(obj1['b'], 2, 'BaseWrapper __getitem__ does not work as intended.')
        self.assertEqual(obj1, obj2, 'BaseWrapper __eq__ does not work as intended.')
        with self.assertRaises(KeyError, msg = 'Trying to access non-existant properties should raise KeyError.'):
            obj1.unexpected_key


class MatchHistoryTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_match_history = api.get_match_history
    
    def test_get_match_history_dtype(self):
        self.assertIsInstance(self.get_match_history(), wrappers.MatchHistory, 
        'get_match_history() should return a MatchHistory object')

# m = cur.get_match_details('4176987886')

# steamIDs = [114539087, 4294967295, 4294967295, 30633942, 78964422, 4294967295, 283619584, 20778465, 4294967295, 59769890]

class MatchDetailsTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_match_details = api.get_match_details
    
    def test_get_match_details_dtype(self):
        match_id = '4176987886'
        self.assertIsInstance(self.get_match_details(match_id), wrappers.MatchDetails,
        f'get_match_details(\'{match_id}\') should return a MatchDetails object')

    def test_incorrect_matchid(self):
        res = self.get_match_details(match_id = 1)
        self.assertTrue(res.error, msg = 'Incorrect match_id should have response error')
    
    def test_match_content(self):
        match_id = '4176987886'
        res = self.get_match_details(match_id)

        q = res.players_minimal[0].hero
        a = entities.Hero(35)
        self.assertEqual(q, a, f'get_match_details(\'{match_id}\').players_minimal[0].hero is {a}')

        q = res.players[6].items()[0].item_name
        a = 'item_tango'
        self.assertEqual(q, a, f'get_match_details(\'{match_id}\').players[6].items()[0].item_name is {a}')

        q = res['tower_status_dire']
        a = 2047
        self.assertEqual(q, a, f'get_match_details(\'{match_id}\')[\'tower_status_dire\'] is {a}')

class HeroesTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_heroes = api.get_heroes
    
    def test_get_heroes_dtype(self):
        self.assertIsInstance(self.get_heroes(), wrappers.Heroes,
        'get_heroes() should return a Heroes object')

    def test_hero_localized_name(self):
        res = self.get_heroes()
        cur_id = 59
        cur_hero = [h for h in res.heroes if h.id == cur_id][0]
        self.assertEqual(cur_hero.localized_name, 'Huskar',
        f'Localized name of id = {cur_id} should be Huskar')

class GameItemsTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_game_items = api.get_game_items
    
    def test_get_game_items_dtype(self):
        self.assertIsInstance(self.get_game_items(), wrappers.GameItems,
        'get_game_items() should return a GameItems object')
        
    def test_item_localized_name(self):
        res = self.get_game_items()
        cur_id = 265
        cur_item = [i for i in res.items if i.id == cur_id][0]
        self.assertEqual(cur_item.localized_name, 'Infused Raindrops',
        f'Localized name of id = {cur_id} should be Infused Raindrops')

class TournamentPrizePoolTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_tournament_prize_pool = api.get_tournament_prize_pool
    
    def test_get_tournament_prize_pool_dtype(self):
        self.assertIsInstance(self.get_tournament_prize_pool(), wrappers.TournamentPrizePool,
        'get_tournament_prize_pool() should return a TournamentPrizePool object.')

class TopLiveGameTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_top_live_game = api.get_top_live_game
    
    def test_get_top_live_game_dtype(self):
        self.assertIsInstance(self.get_top_live_game(), wrappers.TopLiveGame,
        'get_top_live_game() should return a TopLiveGame object.')

class LanguageTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper(language = 'zh-CN')
        self.api = api
    
    def test_wrapper_default_language(self):
        am_name = "敌法师"
        ret = self.api.get_heroes()

        queried_am_name = None
        for h in ret.heroes:
            if h.id == 1:
                queried_am_name = h.localized_name
                break
        
        self.assertEqual(queried_am_name, am_name, f'Anti-mage has the name {am_name} in {self.api.language}')
    
    def test_wrapper_forced_language(self):
        am_name = "敵法僧"
        forced_lang = 'zh-TW'
        ret = self.api.get_heroes(language = forced_lang)

        queried_am_name = None
        for h in ret.heroes:
            if h.id == 1:
                queried_am_name = h.localized_name
                break
        
        self.assertEqual(queried_am_name, am_name, f'Anti-mage has the name {am_name} in {forced_lang}')

class TeamInfoByTeamIDTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_team_info_by_team_id = api.get_team_info_by_team_id

    def test_get_team_info_by_team_id_dtype(self):
        self.assertIsInstance(self.get_team_info_by_team_id(), wrappers.TeamInfoByTeamID,
        'get_team_info_by_team_id() should return a TeamInfoByTeamID object.')

    def test_team_info_content(self):
        team_id = 46
        team_name = "Team Empire"
        time_created = 1340178158
        team_info = self.get_team_info_by_team_id(start_at_team_id = team_id).teams[0]

        self.assertEqual(team_info.name, team_name, f'Team with team_id = {team_id} is {team_name}.')
        self.assertEqual(team_info.time_created, time_created, f'Team {team_name} was created at {time_created}.')

class LiveLeagueGamesTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_live_league_games = api.get_live_league_games
    
    def test_get_live_league_games_dtype(self):
        self.assertIsInstance(self.get_live_league_games(), wrappers.LiveLeagueGames,
        'get_live_league_games() should return a LiveLeagueGames object.' )

if __name__ == '__main__':
    unittest.main()
