#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import copy

from . import entities

class BaseWrapper:
    def __eq__(self, other):
        if self.__class__.__name__ == other.__class__.__name__:
            return self._obj == other._obj
        return False
        
    def __getattr__(self, attr):
        return self._obj[attr]

    def __getitem__(self, attr):
        if attr == '_obj':
            return self._obj
        return self._obj[attr]

    def __init__(self, default_obj = {}):
        self._obj = copy.deepcopy(default_obj)
        self.parse()
        
    def parse(self):
        pass

class ParseInterface(BaseWrapper):
    pass
    
class ResponseInterface(BaseWrapper):
    def parse_response(self, response_obj):
        pass

    def __init__(self, response, unparsed = False):
        self.raw_json = response.content
        self._obj = {}
        if unparsed:
            self._obj = response.json()
        else:
            self.parse_response(response.json())
    

class MatchSummary(ParseInterface):
    def players(self):
        return self._obj['_players']

    def parse(self):
        self._obj['_players'] = []
        for pl in self._obj.pop('players', []):
            p = entities.SteamAccount(pl.get('account_id'))
            s = entities.get_side(pl.get('player_slot', 0))
            h = entities.Hero(pl.get('hero_id', None))
            self._obj['_players'].append(BaseWrapper({'steam_account':p, 'side':s, 'hero':h}))

class InventoryUnit(ParseInterface):
    def items(self):
        tot = self._obj['_items']['_backpack'] + self._obj['_items']['_inventory']
        return tot

    def backpack(self):
        return self._obj['_items']['_backpack']

    def inventory(self):
        return self._obj['_items']['_inventory']

    def build_item_list(self):
        self._obj['_items'] = {'_inventory':[], '_backpack':[]}

        for item_slot in ['item_{}'.format(i) for i in range(6)]:
            cur_item = entities.Item(self._obj.get(item_slot))
            self._obj[item_slot] = cur_item
            self._obj['_items']['_inventory'].append(cur_item)

        for backpack_slot in ['backpack_{}'.format(i) for i in range(3)]:
            cur_item = entities.Item(self._obj.get(backpack_slot))
            self._obj[backpack_slot] = cur_item
            self._obj['_items']['_backpack'].append(cur_item)

class AdditionalUnit(InventoryUnit):
    def parse(self):
        self.build_item_list()

class PlayerUnit(InventoryUnit):
    def minimal(self):
        return BaseWrapper({
        'steam_account':self._obj['steam_account'],
        'side':self._obj['side'],
        'hero':self._obj['hero']
        })

    def additional_units(self):
        return self._obj['_additional_units']

    def ability_upgrades(self):
        return self._obj['_ability_upgrades']

    def parse(self):
        self.build_item_list()
        self._obj['steam_account'] = entities.SteamAccount(self._obj.pop('account_id', None))
        self._obj['side'] = entities.get_side(self._obj.pop('player_slot', 0))
        self._obj['hero'] = entities.Hero(self._obj.pop('hero_id', None))

        self._obj['_additional_units'] = [AdditionalUnit(a) for a in self._obj.pop('additional_units', [])]

        self._obj['_ability_upgrades'] = []
        for au in self._obj.pop('ability_upgrades', []):
            au['ability'] = entities.Ability(au.get('ability'))
            self._obj['_ability_upgrades'].append(BaseWrapper(au))


class MatchHistory(ResponseInterface):
    def matches(self):
        return self._obj['_matches']

    def parse_response(self, response_obj):
        self._obj = response_obj.get('result', {})
        self._obj['_matches'] = [MatchSummary(match) for match in self._obj.pop('matches', [])]


class MatchDetails(ResponseInterface):
    def players(self, minimal = False):
        if minimal:
            return [p.minimal() for p in self._obj['_players']]
        return self._obj['_players']

    def picks_bans(self):
        return self._obj['_picks_bans']

    def leavers(self):
        return [p for p in self._obj['_players'] if p.leaver_status != 0]

    def has_leaver(self):
        for p in self._obj['_players']:
            if p.leaver_status != 0:
                return True
        return False

    def parse_response(self, response_obj):
        self._obj = response_obj.get('result', {})

        self._obj['_players'] = [PlayerUnit(pl) for pl in self._obj.pop('players', [])]

        picksbans = []

        for pb in self._obj.pop('picks_bans', []):
            ip = pb.get('is_pick')
            h = entities.Hero(pb.get('hero_id'))
            s = 'dire' if pb.get('team') == 0 else 'radiant'
            o = pb.get('order')
            picksbans.append(BaseWrapper({'is_pick':ip, 'hero':h, 'side':s, 'order':o}))

        self._obj['_picks_bans'] = sorted(picksbans, key = lambda x:x.order)

        towers = ['top_t1', 'top_t2', 'top_t3', 'mid_t1', 'mid_t2', 'mid_t3', 'bot_t1', 'bot_t2', 'bot_t3', 'ancient_bot', 'ancient_top']
        barracks = ['top_melee', 'top_ranged', 'mid_melee', 'mid_ranged', 'bot_melee', 'bot_ranged']

        for side in ['radiant', 'dire']:

            tower_status = self._obj.get('tower_status_{}'.format(side))
            if tower_status != None:
                for i, t in enumerate(towers):
                    cur_tower_status = ((1<<i) & tower_status) >> i
                    self._obj['{}_{}'.format(side, t)] = cur_tower_status

            barracks_status = self._obj.get('barracks_status_{}'.format(side))
            if barracks_status != None:
                for i, b in enumerate(barracks):
                    cur_barracks_status = ((1<<i) & barracks_status) >> i
                    self._obj['{}_{}'.format(side, b)] = cur_barracks_status

class Heroes(ResponseInterface):
    def heroes(self):
        return self._obj['_heroes']

    def parse_response(self, response_obj):
        self._obj = response_obj.get('result', {})
        self._obj['_heroes'] = [BaseWrapper(h) for h in self._obj.pop('heroes', [])]

class GameItems(ResponseInterface):
    def items(self):
        return self._obj['_items']

    def parse_response(self, response_obj):
        self._obj = response_obj.get('result', {})
        self._obj['_items'] = [BaseWrapper(i) for i in self._obj.pop('items', [])]