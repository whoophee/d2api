#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest
from pathlib import Path

import d2api
from d2api.src import endpoints
from d2api.src import entities
from d2api.src import errors as d2errors
from d2api.src import wrappers
from d2api import update_local_data
from d2api.src import util

# TODO: A whole lot more test cases

class MatchHistoryTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_match_history = api.get_match_history
    
    def test_get_match_history_dtype(self):
        self.assertIsInstance(self.get_match_history(), wrappers.MatchHistory, 
        'get_match_history() should return a MatchHistory object')
    
    def test_steamaccount_arg(self):
        steam_account = entities.SteamAccount('76561198088874284')
        account_id = '76561198088874284'
        
        res1 = self.get_match_history(steam_account = steam_account)
        res2 = self.get_match_history(account_id = account_id)

        self.assertEqual(res1, res2, 
        f"get_match_history(steam_account = {steam_account}) should be the same as get_match_history(match_id = {account_id})")
    
    def test_hero_arg(self):
        hero = entities.Hero(1)
        hero_id = 1

        res1 = self.get_match_history(account_id = '76561198088874284', hero = hero)
        res2 = self.get_match_history(account_id = '76561198088874284', hero_id = hero_id)

        self.assertEqual(res1, res2,
        f"get_match_history(hero = {hero}) should be the same as get_match_history(hero_id = {hero_id})")


class MatchHistoryBySeqNumTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_match_history_by_sequence_num = api.get_match_history_by_sequence_num
    
    def test_get_match_history_by_sequence_num_dtype(self):
        self.assertIsInstance(self.get_match_history_by_sequence_num(), wrappers.MatchHistory, 
        'get_match_history_by_sequence_num() should return a MatchHistory object')

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
        self.assertTrue(res['error'], msg = 'Incorrect match_id should have response error')
    
    def test_match_content(self):
        match_id = '4176987886'
        res = self.get_match_details(match_id)

        q = res['players_minimal'][0]['hero']
        a = entities.Hero(35)
        self.assertEqual(q, a, f'get_match_details(\'{match_id}\')[\'players_minimal\'][0][\'hero\'] is {a}')

        q = res['players'][6].all_items()[0]['item_name']
        a = 'item_tango'
        self.assertEqual(q, a, f'get_match_details(\'{match_id}\')[\'players\'][6].all_items()[0][\'item_name\'] is {a}')

        q = res['dire_buildings']['tower_status']
        a = 2047
        self.assertEqual(q, a, f'get_match_details(\'{match_id}\')[\'dire_buildings\'][\'tower_status\'] is {a}')
    
    def test_leaver_status(self):
        match_id = '4176987886'
        res = self.get_match_details(match_id)
        self.assertTrue(res.has_leavers(), f"get_match_details(\'{match_id}\').has_leavers() is True")

        leavers = [entities.SteamAccount(account_id = 4294967295), 
        entities.SteamAccount(account_id = 283619584), 
        entities.SteamAccount(account_id = 20778465), 
        entities.SteamAccount(account_id = 4294967295), 
        entities.SteamAccount(account_id = 59769890)]

        self.assertEqual(res.leavers(), leavers, f"get_match_details(\'{match_id}\').leavers() does not work as intended")
    
    def test_ability_upgrade(self):
        match_id = '4300255508'
        res = self.get_match_details(match_id)
        ability = res['players'][0]['ability_upgrades'][0]['ability']
        ability_match = entities.Ability(ability_id = 5008)
        
        self.assertEqual(ability, ability_match, 
        f"get_match_details({match_id})[\'players\'][0][\'ability_upgrades\'][0][\'ability\'] should be {ability_match}")

class HeroesTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_heroes = api.get_heroes
    
    def test_get_heroes_dtype(self):
        self.assertIsInstance(self.get_heroes(), wrappers.Heroes,
        'get_heroes() should return a Heroes object')

    def test_hero_localized_name(self):
        res = self.get_heroes(language = 'en_us')
        cur_id = 59
        cur_hero = [h for h in res['heroes'] if h['id'] == cur_id][0]
        self.assertEqual(cur_hero['localized_name'], 'Huskar',
        f'Localized name of id = {cur_id} should be Huskar')

class GameItemsTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_game_items = api.get_game_items
    
    def test_get_game_items_dtype(self):
        self.assertIsInstance(self.get_game_items(), wrappers.GameItems,
        'get_game_items() should return a GameItems object')
        
    def test_item_localized_name(self):
        res = self.get_game_items(language = 'en_us')
        cur_id = 265
        cur_item = [i for i in res['game_items'] if i['id'] == cur_id][0]
        self.assertEqual(cur_item['localized_name'], 'Infused Raindrops',
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
        api = d2api.APIWrapper()
        self.api = api
    
    def test_wrapper_language(self):
        am_name = "敵法僧"
        lang = 'zh-TW'
        ret = self.api.get_heroes(language = lang)
        queried_am_name = [h['localized_name'] for h in ret['heroes'] if h['id'] == 1][0]
        
        self.assertEqual(queried_am_name, am_name, f'Anti-mage has the name {am_name} in {lang}')

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
        team_info = self.get_team_info_by_team_id(start_at_team_id = team_id)['teams'][0]

        self.assertEqual(team_info['name'], team_name, f'Team with team_id = {team_id} is {team_name}.')
        self.assertEqual(team_info['time_created'], time_created, f'Team {team_name} was created at {time_created}.')

class LiveLeagueGamesTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_live_league_games = api.get_live_league_games
    
    def test_get_live_league_games_dtype(self):
        self.assertIsInstance(self.get_live_league_games(), wrappers.LiveLeagueGames,
        'get_live_league_games() should return a LiveLeagueGames object.' )
    
    def test_livegame_parse(self):
        p = Path(os.path.join(os.path.dirname(__file__), 'ref', 'livegame.json'))
        json = util.decode_json(open(p, encoding = 'utf8').read())
        game = wrappers.Game(json)
        
        self.assertEqual(game['scoreboard']['radiant']['players'][0]['abilities'][3]['ability'], entities.Ability(ability_id = 6491),
        "Parsing repeated keys does not work as intended.")