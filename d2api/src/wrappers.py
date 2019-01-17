#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import pprint

from . import entities

class BaseWrapper:
    def __eq__(self, other):
        if self.__class__.__name__ == other.__class__.__name__:
            return self.__dict__ == other.__dict__
        return False

    def __str__(self):
        return pprint.pformat(self.__dict__)

    def __getitem__(self, key):
        return self.__dict__[key]
    
    def __setitem__(self, key, val):
        self.__dict__[key] = val
    
    def get(self, *args):
        return self.__dict__.get(*args)
    
    def pop(self, *args):
        return self.__dict__.pop(*args)
    
    def __getattr__(self, k):
        return self.__getitem__(k)

    def __init__(self, default_obj = {}):
        self.__dict__ = default_obj


class AbstractParse(BaseWrapper):
    def __init__(self, default_obj = {}):
        self.__dict__ = default_obj
        self.parse()
    
    def parse(self):
        pass

class AbstractResponse(BaseWrapper):
    def __init__(self, response):
        self.raw_json = response.content
        self.__dict__ = response.json()
        self.parse_response()

    def parse_response(self, rname = 'result'):
        self.__dict__ = self.get(rname, {})

class MatchSummary(AbstractParse):
    def parse(self):
        player_list = []
        for pl in self.get('players', []):
            p = entities.SteamAccount(pl.get('account_id'))
            s = entities.get_side(pl.get('player_slot', 0))
            h = entities.Hero(pl.get('hero_id', None))
            player_list.append(BaseWrapper({'steam_account':p, 'side':s, 'hero':h}))
        
        self['players'] = player_list

class InventoryUnit(AbstractParse):
    def items(self):
        tot = self._items['inventory'] + self._items['backpack']
        return tot

    def backpack(self):
        return self._items['backpack']

    def inventory(self):
        return self._items['inventory']

    def build_item_list(self):
        self._items = {'inventory':[], 'backpack':[]}

        for item_slot in [f'item_{i}' for i in range(6)]:
            cur_item = entities.Item(self.get(item_slot))
            self[item_slot] = cur_item
            self._items['inventory'].append(cur_item)

        for backpack_slot in [f'backpack_{i}' for i in range(3)]:
            cur_item = entities.Item(self.get(backpack_slot))
            self[backpack_slot] = cur_item
            self._items['backpack'].append(cur_item)

class AdditionalUnit(InventoryUnit):
    def parse(self):
        self.build_item_list()

class PlayerUnit(InventoryUnit):
    def parse(self):
        self.build_item_list()

        self['steam_account'] = entities.SteamAccount(self.pop('account_id', None))
        self['side'] = entities.get_side(self.pop('player_slot', 0))
        self['hero'] = entities.Hero(self.pop('hero_id', None))

        self['additional_units'] = [AdditionalUnit(a) for a in self.get('additional_units', [])]

        au_list = []
        for au in self.get('ability_upgrades', []):
            au['ability'] = entities.Ability(au.get('ability'))
            au_list.append(BaseWrapper(au))

        self['ability_upgrades'] = au_list


class MatchHistory(AbstractResponse):
    def parse_response(self):
        super().parse_response()
        self['matches'] = [MatchSummary(match) for match in self.get('matches', [])]


class MatchDetails(AbstractResponse):
    def leavers(self):
        return [p for p in self['players'] if p.leaver_status != 0]

    def has_leaver(self):
        for p in self['players']:
            if p.leaver_status != 0:
                return True
        return False

    def parse_response(self):
        super().parse_response()


        minimal = lambda x: BaseWrapper({
            'steam_account':x.steam_account,
            'side':x.side,
            'hero':x.hero
            })

        self['players'] = [PlayerUnit(pl) for pl in self.get('players', [])]
        self['players_minimal'] = [minimal(p) for p in self['players']]

        picksbans = []

        for pb in self.get('picks_bans', []):
            ip = pb.get('is_pick')
            h = entities.Hero(pb.get('hero_id'))
            s = 'dire' if pb.get('team') == 0 else 'radiant'
            o = pb.get('order')
            picksbans.append(BaseWrapper({'is_pick':ip, 'hero':h, 'side':s, 'order':o}))

        self['picks_bans'] = sorted(picksbans, key = lambda x:x.order)

        towers = ['top_t1', 'top_t2', 'top_t3', 'mid_t1', 'mid_t2', 'mid_t3', 'bot_t1', 'bot_t2', 'bot_t3', 'ancient_bot', 'ancient_top']
        barracks = ['top_melee', 'top_ranged', 'mid_melee', 'mid_ranged', 'bot_melee', 'bot_ranged']

        for side in ['radiant', 'dire']:

            tower_status = self.get(f'tower_status_{side}')
            if tower_status != None:
                for i, t in enumerate(towers):
                    cur_tower_status = ((1<<i) & tower_status) >> i
                    self[f'{side}_{t}'] = cur_tower_status

            barracks_status = self.get(f'barracks_status_{side}')
            if barracks_status != None:
                for i, b in enumerate(barracks):
                    cur_barracks_status = ((1<<i) & barracks_status) >> i
                    self[f'{side}_{b}'] = cur_barracks_status

class Heroes(AbstractResponse):
    def parse_response(self):
        super().parse_response()
        self['heroes'] = [BaseWrapper(h) for h in self.get('heroes', [])]

class GameItems(AbstractResponse):
    def parse_response(self):
        super().parse_response()
        self['items'] = [BaseWrapper(i) for i in self.get('items', [])]

class TournamentPrizePool(AbstractResponse):
    def parse_response(self):
        super().parse_response()

class Player(AbstractParse):
    def parse(self):
        self['steam_account'] = entities.SteamAccount(self.pop('account_id', None))
        self['hero'] = entities.Hero(self.pop('hero_id', None))

        team = {0:'radiant', 1:'dire', 2:'broadcaster', 4:'unassigned'}
        self['team'] = team[self.get('team', 4)]

class PlayerLive(AbstractParse):
    def parse(self):
        self['hero'] = entities.Hero(self.pop('hero_id', None))
        self['steam_account'] = entities.SteamAccount(self.pop('account_id', None))

        items = []
        for i in range(6):
            items.append(entities.Item(self.pop(f'item{i}', None)))
        self['items'] = items

class TeamLive(AbstractParse):
    def parse(self):
        towers = ['top_t1', 'top_t2', 'top_t3', 'mid_t1', 'mid_t2', 'mid_t3', 'bot_t1', 'bot_t2', 'bot_t3', 'ancient_bot', 'ancient_top']
        barracks = ['top_melee', 'top_ranged', 'mid_melee', 'mid_ranged', 'bot_melee', 'bot_ranged']

        tower_status = self.get(f'tower_state')
        if tower_status != None:
            for i, t in enumerate(towers):
                cur_tower_status = ((1<<i) & tower_status) >> i
                self[t] = cur_tower_status

        barracks_status = self.get(f'barracks_state')
        if barracks_status != None:
            for i, b in enumerate(barracks):
                cur_barracks_status = ((1<<i) & barracks_status) >> i
                self[b] = cur_barracks_status
        
        self['picks'] = [entities.Hero(h['hero_id']) for h in self.get('picks', [])]
        self['bans'] = [entities.Hero(h['hero_id']) for h in self.get('bans', [])]
        self['players'] = [PlayerLive(p) for p in self.get('players', [])]

        abilities = []

        for ab in self.get('abilities', []):
            ability_id = ab.get('ability_id', None)
            ability_level = ab.get('ability_level', 1)
            abilities.append(BaseWrapper({'ability': entities.Ability(ability_id), 'ability_level':ability_level}))
        
        self['abilities'] = abilities

class Scoreboard(AbstractParse):
    def parse(self):
        self['radiant'] = TeamLive(self.get('radiant', {}))
        self['dire'] = TeamLive(self.get('dire', {}))

class Game(AbstractParse):
    def parse(self):
        self['radiant_team'] = BaseWrapper(self.get('radiant_team', {}))
        self['dire_team'] = BaseWrapper(self.get('dire_team', {}))
        self['scoreboard'] = Scoreboard(self.get('scoreboard', {}))

        players = []
        for p in self.get('players', {}):
            p['steam_account'] = entities.SteamAccount(p.pop('account_id'))
            p['hero'] = entities.Hero(p.pop('hero_id'))
            p['team'] = 'dire' if p.get('team') == 0 else 'radiant'
            players.append(BaseWrapper(p))
        self['players'] = players

class LiveLeagueGames(AbstractResponse):
    def parse_response(self):
        super().parse_response()
        self['games'] = [Game(g) for g in self['games']]

class LiveGameSummary(AbstractParse):
    def parse(self):
        tower_state = format(2**31 + self.get('building_state', 0), 'b')[::-1]
        tower = ['top_t1', 'top_t2', 'top_t3', 'mid_t1', 'mid_t2', 'mid_t3', 'bot_t1', 'bot_t2', 'bot_t3', 'ancient_bot', 'ancient_top']
        for i in range(len(tower)):
            cur_tower = f'radiant_{tower[i]}'
            self[cur_tower] = int(tower_state[i])

            cur_tower = f'dire_{tower[i]}'
            self[cur_tower] = int(tower_state[i + 11])
        
        players = []
        for p in self.get('players', []):
            steamacc = entities.SteamAccount(p.get('account_id', None))
            hero = entities.Hero(p.get('hero_id', None))
            players.append(BaseWrapper({'steam_account':steamacc, 'hero': hero}))
        
        self['players'] = players

class TopLiveGame(AbstractResponse):
    def parse_response(self):
        self['game_list'] = [LiveGameSummary(g) for g in self.get('game_list', [])]

class TeamInfoByTeamID(AbstractResponse):
    def parse_response(self):
        super().parse_response()
        self['teams'] = [BaseWrapper(t) for t in self['teams']]

