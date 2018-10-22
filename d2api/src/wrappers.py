from .entities import *
import json
import copy

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
        self._parse()

    def _parse(self):
        pass

class BaseParse (BaseWrapper):
    def raw_json(self):
        return self._raw_json

    def parse_response(self, response_obj):
        pass

    def __init__(self, response, unparsed = False):
        self._raw_json = response.content
        self._obj = {}
        if unparsed:
            self._obj = response.json()
        else:
            self.parse_response(response.json())

class MatchSummary(BaseWrapper):
    def players(self):
        return self._obj['_players'].__iter__()

    def _parse(self):
        self._obj['_players'] = []
        for pl in self._obj.pop('players', []):
            p = SteamAccount(pl.get('account_id'))
            s = get_side(pl.get('player_slot', 0))
            h = get_hero(pl.get('hero_id', None))
            self._obj['_players'].append(BaseWrapper({'steam_account':p, 'side':s, 'hero':h}))

class InventoryUnit:
    def items(self):
        tot = self._obj['_items']['_backpack'] + self._obj['_items']['_inventory']
        return tot.__iter__()

    def backpack(self):
        return self._obj['_items']['_backpack'].__iter__()

    def inventory(self):
        return self._obj['_items']['_inventory'].__iter__()

    def build_item_list(self):
        self._obj['_items'] = {'_inventory':[], '_backpack':[]}

        for item_slot in ['item_{}'.format(i) for i in range(6)]:
            cur_item = get_item(self._obj.get(item_slot))
            self._obj[item_slot] = cur_item
            self._obj['_items']['_inventory'].append(cur_item)

        for backpack_slot in ['backpack_{}'.format(i) for i in range(3)]:
            cur_item = get_item(self._obj.get(backpack_slot))
            self._obj[backpack_slot] = cur_item
            self._obj['_items']['_backpack'].append(cur_item)

class AdditionalUnit(InventoryUnit, BaseWrapper):
    def _parse(self):
        self.build_item_list()

class PlayerUnit(InventoryUnit, BaseWrapper):
    def minimal(self):
        return BaseWrapper({
        'steam_account':self._obj['steam_account'],
        'side':self._obj['side'],
        'hero':self._obj['hero']
        })

    def additional_units(self):
        return self._obj['_additional_units'].__iter__()

    def ability_upgrades(self):
        return self._obj['_ability_upgrades'].__iter__()

    def _parse(self):
        self.build_item_list()
        self._obj['steam_account'] = SteamAccount(self._obj.pop('account_id', None))
        self._obj['side'] = get_side(self._obj.pop('player_slot', 0))
        self._obj['hero'] = get_hero(self._obj.pop('hero_id', None))

        self._obj['_additional_units'] = [AdditionalUnit(a) for a in self._obj.pop('additional_units', [])]

        self._obj['_ability_upgrades'] = []
        for au in self._obj.pop('ability_upgrades', []):
            au['ability'] = get_ability(au.get('ability'))
            self._obj['_ability_upgrades'].append(BaseWrapper(au))


class GetMatchHistory(BaseParse):
    def matches(self):
        return self._obj['_matches'].__iter__()

    def parse_response(self, response_obj):
        self._obj = response_obj.get('result', {})
        self._obj['_matches'] = [MatchSummary(match) for match in self._obj.pop('matches', [])]


class GetMatchDetails(BaseParse):
    def players(self, minimal = False):
        if minimal:
            return [p.minimal() for p in self._obj['_players']].__iter__()
        return self._obj['_players'].__iter__()

    def picks_bans(self):
        return self._obj['_picks_bans'].__iter__()

    def leavers(self):
        return [p for p in self._obj['_players'] if p.leaver_status != 0].__iter__()

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
            h = get_hero(pb.get('hero_id'))
            s = 'dire' if pb.get('team') == 0 else 'radiant'
            o = pb.get('order')
            picksbans.append(BaseWrapper({'is_pick':ip, 'hero':h, 'side':s, 'order':o}))

        self._obj['_picks_bans'] = sorted(picksbans, key = lambda x:x.order)

class GetHeroes(BaseParse):
    def heroes(self):
        return self._obj['_heroes'].__iter__()

    def parse_response(self, response_obj):
        self._obj = response_obj.get('result', {})
        self._obj['_heroes'] = [BaseWrapper(h) for h in self._obj.pop('heroes', [])]

class GetGameItems(BaseParse):
    def items(self):
        return self._obj['_items'].__iter__()

    def parse_response(self, response_obj):
        self._obj = response_obj.get('result', {})
        self._obj['_items'] = [BaseWrapper(i) for i in self._obj.pop('items', [])]