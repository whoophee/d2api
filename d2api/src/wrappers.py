#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy

from . import entities

class BaseWrapper:
    def __eq__(self, other):
        if self.__class__.__name__ == other.__class__.__name__:
            return self._obj == other._obj
        return False

    def __getitem__(self, key):
        return self._obj[key]
    
    def __setitem__(self, key, val):
        self._obj[key] = val
    
    def get(self, *args):
        return self._obj.get(*args)
    
    def pop(self, *args):
        return self._obj.pop(*args)
    
    def __getattr__(self, k):
        return self._obj[k]

    def __init__(self, default_obj = {}):
        self._obj = default_obj


class AbstractParse(BaseWrapper):
    def __init__(self, default_obj = {}):
        self._obj = default_obj
        self.parse()
    
    def parse(self):
        pass

class AbstractResponse(BaseWrapper):
    def __init__(self, response, unparsed = False):
        self.raw_json = response.content
        self._obj = response.json()
        if not unparsed:
            self.parse_response()

    def parse_response(self, rname = 'result'):
        self._obj = self.get(rname, {})

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
        tot = self._items['backpack'] + self._items['inventory']
        return tot

    def backpack(self):
        return self._items['backpack']

    def inventory(self):
        return self._items['inventory']

    def build_item_list(self):
        self._items = {'inventory':[], 'backpack':[]}

        for item_slot in ['item_{}'.format(i) for i in range(6)]:
            cur_item = entities.Item(self.get(item_slot))
            self[item_slot] = cur_item
            self._items['inventory'].append(cur_item)

        for backpack_slot in ['backpack_{}'.format(i) for i in range(3)]:
            cur_item = entities.Item(self.get(backpack_slot))
            self[backpack_slot] = cur_item
            self._items['backpack'].append(cur_item)

class AdditionalUnit(InventoryUnit):
    def parse(self):
        self.build_item_list()

class PlayerUnit(InventoryUnit):
    def minimal(self):
        return BaseWrapper({
        'steam_account':self._steam_account,
        'side':self._side,
        'hero':self._hero
        })

    def parse(self):
        self.build_item_list()

        self._steam_account = entities.SteamAccount(self.get('account_id', None))
        self._side = entities.get_side(self.get('player_slot', 0))
        self._hero = entities.Hero(self.get('hero_id', None))

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

        self['players'] = [PlayerUnit(pl) for pl in self.get('players', [])]
        self['players_minimal'] = [p.minimal() for p in self['players']]

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

            tower_status = self.get('tower_status_{}'.format(side))
            if tower_status != None:
                for i, t in enumerate(towers):
                    cur_tower_status = ((1<<i) & tower_status) >> i
                    self['{}_{}'.format(side, t)] = cur_tower_status

            barracks_status = self.get('barracks_status_{}'.format(side))
            if barracks_status != None:
                for i, b in enumerate(barracks):
                    cur_barracks_status = ((1<<i) & barracks_status) >> i
                    self['{}_{}'.format(side, b)] = cur_barracks_status

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