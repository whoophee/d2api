#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import pprint

from . import entities
"""Parse wrapper definitions"""

def _get_side_from_slot(player_slot):
    """Get player team based on player slot"""
    return "radiant" if player_slot < 128 else "dire"

def _get_side_from_team(team):
    """Map integer reference to string"""
    return {0:'radiant', 1:'dire', 2:'broadcaster', 4:'unassigned'}.get(team, 'unassigned')

def _get_subdict(d, keys):
    """Get a subdict with specific keys"""
    return {k: d.get(k) for k in keys}

class BaseWrapper(dict):
    """Base wrapper class for parsed results."""
    def __str__(self):
        return pprint.pformat(super().copy())

    def _copy_dict(self, other):
        for k, v in other.items():
            super().__setitem__(k, v)
            
    def __init__(self, default_obj = {}):
        self._copy_dict(default_obj)

class AbstractParse(BaseWrapper):
    """Interface to implement parsed objects."""
    def __init__(self, default_obj = {}):
        """
        :param default_obj: 

        :type default_obj: dict
        """
        super().__init__(default_obj)
        self.parse()
    
    def parse(self):
        pass

class AbstractResponse(BaseWrapper):
    """Interface to implement parsed response objects."""
    def __init__(self, response):
        self.raw_json = response.content
        super().__init__(response.json())
        self.parse_response()

    def parse_response(self, rname = 'result'):
        super()._copy_dict(self.pop(rname, {}))

class PlayerMinimal(AbstractParse):
    """A minimal information wrapper for a player

    :var steam_account: Steam account of player
    :var side: side to which a player belongs (radiant/dire)
    :var hero: hero played

    :vartype steam_account: SteamAccount
    :vartype side: str
    :vartype hero: Hero
    """
    def parse(self):
        self['steam_account'] = entities.SteamAccount(self.pop('account_id', None))

        player_slot = self.pop('player_slot', None)
        if not player_slot == None:
            self['side'] = _get_side_from_slot(player_slot)

        team = self.pop('team', None)
        if not team == None:
            self['side'] = _get_side_from_team(team)

        self['hero'] = entities.Hero(self.pop('hero_id', None))

# TODO : parse lobby_type or add enumeration for lobby_type
class MatchSummary(AbstractParse):
    """A brief summary of queried games

    :var match_id: The unique ID of a match
    :var match_seq_num: Represents the sequence in which matches were recorded
    :var start_time: Unix timestamp of game begin time
    :var lobby_type: Integer representing type of lobby
    :var players: List of player summaries

    :vartype match_id: int
    :vartype match_seq_num: int
    :vartype start_time: int
    :vartype lobby_type: int
    :vartype players: list(PlayerMinimal)
    """
    def parse(self):
        self['players'] = [PlayerMinimal(p) for p in self.get('players', [])]

class MatchHistory(AbstractResponse):
    """get_match_history response object

    :var matches: List of match summaries

    :vartype matches: list(MatchSummary)
    """
    def parse_response(self):
        super().parse_response()
        self['matches'] = [MatchSummary(match) for match in self.get('matches', [])]
       
class InventoryUnit(AbstractParse):
    """Any unit having item slots."""
    def all_items(self):
        """
        :return: Combined list of inventory and backpack items
        
        :rtype: list(Item)
        """
        tot = self['inventory'] + self['backpack']
        return tot

    def _build_item_list(self):
        self['inventory'] = []
        self['backpack'] = []

        for item_slot in [f'item_{i}' for i in range(6)]:
            cur_item = entities.Item(self.pop(item_slot, None))
            self['inventory'].append(cur_item)

        for backpack_slot in [f'backpack_{i}' for i in range(3)]:
            cur_item = entities.Item(self.pop(backpack_slot, None))
            self['backpack'].append(cur_item)

class AdditionalUnit(InventoryUnit):
    """An inventoried unit besides heroes (e.g. Lone druid bear)
    
    :var inventory: List of inventory items
    :var backpack: List of backpack items

    :vartype inventory: list(Item)
    :vartype backpack: list(Item)
    """

    def parse(self):
        self._build_item_list()

class AbilityUpgrade(AbstractParse):
    """Ability upgrade during game.

    :var ability: Ability upgraded.
    :var time: Game time at which ability was upgraded
    :var level: Level of the player at which ability was upgraded.

    :vartype ability: Ability
    :vartype time: int
    :vartype level: int
    """
    def parse(self):
        self['ability'] = entities.Ability(self.pop('ability_id', None))

# TODO: add leaver status enumeration

class PlayerUnit(InventoryUnit):
    """An inventoried hero unit

    :var steam_account: Steam account of player
    :var side: Side to which a player belongs (radiant/dire)
    :var hero: Hero played
    :var kills: Number of kills at the end of the match
    :var deaths: Number of deaths at the end of the match
    :var assists: Number of assists at the end of the match
    :var leaver_status: Type of leaver
    :var gold: Amount of gold remaining at the end of the match
    :var last_hits: Number of list hits at the end of the match
    :var denies: Number of denies at the end of the game
    :var gold_per_minute: Overall gold/minute
    :var xp_per_minute: Overall XP/min
    :var gold_spent: Amount of gold spent during the match
    :var hero_damage: Total damage done to other heroes at the end of the match
    :var tower_damage: Total damage done to opponent towers at  the end of the match
    :var hero_healing: Total healing done to other heroes at the end of the match
    :var additional_units: Additional units belonging to the current unit
    :var inventory: List of inventory items
    :var backpack: List of backpack items
    :var ability_upgrades: Ability upgrade information
    

    :vartype steam_account: SteamAccount 
    :vartype side: str
    :vartype hero: Hero
    :vartype kills: int
    :vartype deaths: int
    :vartype assists: int
    :vartype leaver_status: int
    :vartype gold: int
    :vartype last_hits: int
    :vartype denies: int
    :vartype gold_per_min: int
    :vartype xp_per_min: int
    :vartype gold_spent: int
    :vartype hero_damage: int
    :vartype tower_damage: int
    :vartype hero_healing: int
    :vartype additional_units: list(AdditionalUnit)
    :vartype inventory: list(Item)
    :vartype backpack: list(Item)
    :vartype ability_upgrades: list(AbilityUpgrade)
    """
    def parse(self):
        self._build_item_list()

        self['steam_account'] = entities.SteamAccount(self.pop('account_id', None))
        self['side'] = _get_side_from_slot(self.pop('player_slot', 0))
        self['hero'] = entities.Hero(self.pop('hero_id', None))

        self['additional_units'] = [AdditionalUnit(a) for a in self.get('additional_units', [])]

        au_list = []
        for au in self.get('ability_upgrades', []):
            au['ability_id'] = au.pop('ability', None)
            au_list.append(AbilityUpgrade(au))
        self['ability_upgrades'] = au_list

class Buildings(AbstractParse):
    """Represents current state of buildings

    :var {lane}_{position}: Tower status [lane = top, mid, bot][position = 1, 2, 3] (e.g. top_t2)
    :var ancient_bot: Ancient bottom tower
    :var ancient_top: Ancient top tower
    :var {lane}_{type}: Barracks status [lane = top, mid, bot][type = ranged, melee] (e.g. mid_melee) 

    :vartype {lane}_{position}: bool
    :vartype ancient_top: bool
    :vartype ancient_bot: bool
    :vartype {lane}_{type}: bool
    """
    def parse(self):

        towers = ['top_t1', 'top_t2', 'top_t3', 'mid_t1', 'mid_t2', 'mid_t3', 'bot_t1', 'bot_t2', 'bot_t3', 'bot_ancient', 'top_ancient']
        barracks = ['top_melee', 'top_ranged', 'mid_melee', 'mid_ranged', 'bot_melee', 'bot_ranged']

        tower_status = self.get('tower_status')
        if tower_status != None:
            for i, t in enumerate(towers):
                cur_tower_status = ((1<<i) & tower_status) >> i
                self[t] = cur_tower_status

        barracks_status = self.get('barracks_status')
        if barracks_status != None:
            for i, b in enumerate(barracks):
                cur_barracks_status = ((1<<i) & barracks_status) >> i
                self[b] = cur_barracks_status


class PickBan(AbstractParse):
    """Reprents a pick/ban during a game

    :var is_pick: ``True`` if the hero was picked
    :var hero: Hero being picked/banned
    :var side: Side that picked/banned this hero (radiant/dire)
    :var order: Order in which the hero was picked/banned

    :vartype is_pick: bool
    :vartype hero: Hero
    :vartype side: str
    :vartype order: int
    """
    def parse(self):
        self['hero'] = entities.Hero(self.pop('hero_id', None))
        self['side'] = 'dire' if self.pop('team', 0) == 0 else 'radiant'



class MatchDetails(AbstractResponse):
    """Detailed summary of a match

    :var players: List of players in the game
    :var players_minimal: List of players represented minimally
    :var picks_bans: List of picks/bans
    :var season: The season in which the game was played
    :var winner: Side that won the game (radiant/dire)
    :var duration: Duration of the game (in seconds)
    :var pre_game_duration: Duration for game to begin (in seconds)
    :var start_time: Unix timestamp of match start
    :var match_seq_num: Number denoting the order in which matches were recorded
    :var radiant_buildings: Radiant building statuses at the end of the game
    :var dire_buildings: Dire building statuses at the end of the game
    :var cluster: The server cluster the match was played upon (used to fetch replays)
    :var first_blood_time: Time of first-blood occurrance
    :var lobby_type: Type of lobby
    :var human_players: Number of human players in the game
    :var leagueid: The league that this match was a part of
    :var positive_votes: The number of thumbs-up the game has received by users
    :var negative_votes: The number of thumbs-down the game has received by users
    :var game_mode: Game mode
    :var engine: Source 1/Source 2
    :var radiant_score: TODO
    :var dire_score: TODO
    :var flags: TODO

    :vartype players: PlayerUnit
    :vartype players_minimal: PlayerMinimal
    :vartype picks_bans: PickBan
    :vartype season: int
    :vartype winner: str
    :vartype duration: int
    :vartype pre_game_duration: int
    :vartype start_time: int
    :vartype match_seq_num: int
    :vartype radiant_buildings: Buildings
    :vartype dire_buildings: Buildings
    :vartype cluster: int
    :vartype first_blood_time: int
    :vartype lobby_type: int
    :vartype human_players: int
    :vartype leagueid: int
    :vartype positive_votes: int
    :vartype negative_votes: int
    :vartype game_mode: int
    :vartype engine: int
    :vartype radiant_score: int
    :vartype dire_score: int
    :vartype flags: ?
    """
    def leavers(self):
        """
        :return: List of leavers in a game.

        :rtype: list(PlayerUnit)
        """
        return [p for p in self['players'] if p['leaver_status'] != 0]

    def has_leaver(self):
        """
        :return: ``True`` if the game contains a leaver

        :rtype: bool
        """
        for p in self['players']:
            if p['leaver_status'] != 0:
                return True
        return False

    def parse_response(self):
        super().parse_response()

        minimal = lambda x: PlayerMinimal(_get_subdict(x, ['account_id', 'player_slot', 'hero_id']))

        self['players_minimal'] = [minimal(p) for p in self.get('players', [])]
        self['players'] = [PlayerUnit(pl) for pl in self.get('players', [])]

        if 'radiant_win' in self:
            self['winner'] = 'radiant' if self.pop('radiant_win', None) else 'dire'

        picks_bans = [PickBan(pb) for pb in self.get('picks_bans', [])]
        self['picks_bans'] = sorted(picks_bans, key = lambda x: x['order'])

        
        for side in ['radiant', 'dire']:
            tower_status = self.pop(f'tower_status_{side}', None)
            barracks_status = self.pop(f'barracks_status_{side}', None)
            self[f'{side}_buildings'] = Buildings({'tower_status': tower_status, 'barracks_status': barracks_status})

class LocalizedHero(AbstractParse):
    """Localized hero information

    :var name: Hero name
    :var id: Hero ID
    :var localized_name: Name of hero in language specified

    :vartype name: str
    :vartype id: ind
    :vartype localized_name: str
    """
    pass

class LocalizedGameItem(AbstractParse):
    """Localized item information

    :var id: Item ID
    :var name: Item name
    :var cost: Cost of item
    :var secret_shop: True if the item is sold in secret shop
    :var side_shop: True if the item is sold in side shop
    :var recipe: True if it is a recipe
    :var localized_name: Name of item in language specified

    :vartype id: int
    :vartype name: str
    :vartype cost: int
    :vartype secret_shop: bool
    :vartype side_shop: bool
    :vartype recipe: bool
    :vartype localized_name: str
    """
    pass

class Heroes(AbstractResponse):
    """get_heroes response object

    :var heroes: List of localized hero information
    :var count: Number of heroes returned
    
    :vartype heroes: list(LocalizedHero)
    :vartype count: int
    """
    def parse_response(self):
        super().parse_response()
        self['heroes'] = [LocalizedHero(h) for h in self.get('heroes', [])]

class GameItems(AbstractResponse):
    """get_game_items response object

    :var items: List of localized item information
    
    :vartype items: list(LocalizedGameItem)
    """
    def parse_response(self):
        super().parse_response()
        self['items'] = [LocalizedGameItem(i) for i in self.get('items', [])]

class TournamentPrizePool(AbstractResponse):
    """get_tournament_prize_pool response object

    :var prize_pool: Prize pool
    :var league_id: League ID for which prize pool was fetched

    :vartype prize_pool: int
    :vartype league_id: int
    """
    pass

# TODO: add enumeration for state of ultimate
class PlayerLive(AbstractParse):
    """Information of a player in live game

    :var player_slot: Slot of player within the team
    :var steam_account: Steam account of the player
    :var hero: Hero played
    :var kills: Number of kills
    :var deaths: Number of deaths
    :var assists: Number of assists
    :var last_hits: Number of last hits
    :var denies: Number of denies
    :var gold: Current amount of gold
    :var level: Current level
    :var gold_per_min: gold/min at time of query
    :var xp_per_min: XP/min at time of query
    :var ultimate_state: Current state of ultimate
    :var ultimate_cooldown: Remaining time for ultimate to come off cooldown
    :var inventory: List of items in player inventory
    :var respawn_timer: Remain time for player to respawn
    :var position_x: X coordinate of hero
    :var position_y: Y coordinate of hero
    :var net_worth: Net worth of the hero

    :vartype player_slot: int
    :vartype steam_account: SteamAccount
    :vartype hero: Hero
    :vartype kills: int
    :vartype deaths: int
    :vartype assists: int
    :vartype denies: int
    :vartype gold: int
    :vartype level: int
    :vartype gold_per_min: int
    :vartype xp_per_min: int
    :vartype ultimate_state: int
    :vartype ultimate_cooldown: int
    :vartype inventory: list(Item)
    :vartype respawn_timer: int
    :vartype position_x: float
    :vartype position_y: float
    :vartype net_worth: int
    """
    def parse(self):
        self['hero'] = entities.Hero(self.pop('hero_id', None))
        self['steam_account'] = entities.SteamAccount(self.pop('account_id', None))

        self['deaths'] = self.pop('death', None)

        self['inventory'] = [entities.Item(self.pop(f'item{i}', None)) for i in range(6)]

class TeamLive(AbstractParse):
    """Information of a team in live game

    :var score: Current number of kills by the team
    :var buildings: State of buildings
    :var picks: List of heroes picked
    :var bans: List of heroes banned
    :var players: List of player summaries
    :var abilities: List of abilities being performed at time of query
    
    :vartype score: int 
    :vartype buildings: Buildings
    :vartype picks: list(Hero)
    :vartype bans: list(Hero)
    :vartype players: list(PlayerLive)
    :vartype abilities: list(AbilityUpgrade)
    """
    def parse(self):

        tower_status = self.get('tower_state')
        barracks_status = self.get('barracks_state')
        self['buildings'] = Buildings({'tower_status': tower_status, 'barracks_status': barracks_status})
        
        self['picks'] = [entities.Hero(h['hero_id']) for h in self.get('picks', [])]
        self['bans'] = [entities.Hero(h['hero_id']) for h in self.get('bans', [])]
        self['players'] = [PlayerLive(p) for p in self.get('players', [])]
        
        self['abilities'] = [AbilityUpgrade(ab) for ab in self.get('abilities', [])]

class Scoreboard(AbstractParse):
    """Scoreboard of live game

    :var duration: Duration of the game at time of query
    :var roshan_respawn_timer: Time left for Roshan to respawn
    :var radiant: Radiant team summary
    :var dire: Dire team summary

    :vartype duration: int
    :vartype roshan_respawn_timer: int
    :vartype radiant: TeamLive
    :vartype dire: TeamLive
    """
    def parse(self):
        self['radiant'] = TeamLive(self.get('radiant', {}))
        self['dire'] = TeamLive(self.get('dire', {}))

class TeamInfo(AbstractParse):
    """Information about team

    :var team_name: The team's name.
    :var team_id: The team's unique ID.
    :var team_logo: The UGC id for the team logo.
    :var complete: Whether the players for this team are all team members.

    :vartype team_name: str
    :vartype team_id: int
    :vartype team_logo: int
    :vartype complete: bool
    """
    pass

# TODO: enumerate series type
class Game(AbstractParse):
    """Summary of a live league game

    :var radiant_team: Radiant team information
    :var dire_team: Dire team information
    :var players: List of players in the game
    :var scoreboard: Game scoreboard at time of query
    :var lobby_id: ID of lobby
    :var match_id: Unique ID used to identify match
    :var spectators: Number of spectators
    :var league_id: Unique ID for the league of the match
    :var league_node_id: Unique ID of node within the league
    :var stream_delay_s: Stream delay in seconds
    :var radiant_series_win: Number of wins by radiant team
    :var dire_series_win: Number of wins by dire team
    :var series_type: Type of series

    :vartype radiant_team: TeamInfo
    :vartype dire_team: TeamInfo
    :vartype players: list(PlayerMinimal)
    :vartype scoreboard: Scoreboard
    :vartype lobby_id: int
    :vartype match_id: int
    :vartype spectators: int 
    :vartype league_id: int
    :vartype league_node_id: int
    :vartype stream_delay_s: int
    :vartype radiant_series_win: int
    :vartype dire_series_win: int
    :vartype series_type: int
    """
    def parse(self):
        self['radiant_team'] = TeamInfo(self.get('radiant_team', {}))
        self['dire_team'] = TeamInfo(self.get('dire_team', {}))
        self['scoreboard'] = Scoreboard(self.get('scoreboard', {}))
        self['players'] = [PlayerMinimal(p) for p in self.get('players', [])]

class LiveLeagueGames(AbstractResponse):
    """get_live_league_games response object

    :var games: List of games

    :vartype games: list(Game)
    """
    def parse_response(self):
        super().parse_response()
        self['games'] = [Game(g) for g in self['games']]

# TODO: add lobby type enumeration
# TODO: add game mode enumeration
class LiveGameSummary(AbstractParse):
    """Summary of a live game

    :var players: List of player info
    :var radiant_towers: Radiant towers
    :var dire_towers: Dire towers
    :var activate_time: TODO
    :var deactivate_time: TODO
    :var server_steam_id: Steam ID of server
    :var lobby_id: ID of lobby
    :var league_id: Unique ID for the league of the match
    :var lobby_type: Type of lobby
    :var game_time: Game time
    :var delay: Stream delay (game, spectator delay)
    :var spectators: Current number of spectators
    :var game_mode: Game mode of current game
    :var average_mmr: Average MMR of the game
    :var match_id: Unique ID used to identify match
    :var series_id: Unique ID used to identify series
    :var radiant_team: Information about radiant team
    :var dire_team: Information about dire team
    :var sort_score: TODO
    :var last_update_time: TODO
    :var radiant_lead: Gold lead of radiant team
    :var radiant_score: TODO
    :var dire_score: TODO

    :vartype players: PlayerMinimal
    :vartype radiant_towers: Buildings
    :vartype dire_towers: Buildings
    :vartype activate_time: int
    :vartype deactivate_time: int
    :vartype server_steam_id: int
    :vartype lobby_id: int
    :vartype league_id: int
    :vartype lobby_type: int
    :vartype game_time: int
    :vartype delay: int
    :vartype spectators: int
    :vartype game_mode: int
    :vartype average_mmr: int
    :vartype match_id: int
    :vartype series_id: int
    :vartype radiant_team: TeamInfo
    :vartype dire_team: TeamInfo
    :vartype sort_score: int
    :vartype last_update_time: int
    :vartype radiant_lead: int
    :vartype radiant_score: int
    :vartype dire_score: int
    """
    def parse(self):
        tower_states = self.pop('building_state', 0)
        dire_tower_state = tower_states // 2**11
        radiant_tower_state = tower_states % 2**11

    
        self['radiant_towers'] = Buildings({'tower_status': radiant_tower_state})
        self['dire_towers'] = Buildings({'tower_status': dire_tower_state})
        self['players'] = [PlayerMinimal(p) for p in self.get('players', [])]
        
        radiant_team_name = self.pop('team_name_radiant', None)
        dire_team_name = self.pop('team_name_dire', None)
        radiant_team_id = self.pop('team_id_radiant', None)
        dire_team_id = self.pop('team_id_dire', None)

        self['radiant_team'] = TeamInfo({'team_name': radiant_team_name, 'team_id': radiant_team_id})
        self['dire_team'] = TeamInfo({'dire_name': dire_team_name, 'dire_id': dire_team_id})

class TopLiveGame(AbstractResponse):
    """get_top_live_game response object

    :var game_list: List of top live games

    :vartype game_list: list(LiveGameSummary)
    """
    def parse_response(self):
        self['game_list'] = [LiveGameSummary(g) for g in self.get('game_list', [])]

class TeamInfoByTeamID(AbstractResponse):
    """get_team_info_by_team_id response object

    :var teams: List of team information

    :vartype teams: list(TeamInfo)
    """
    def parse_response(self):
        super().parse_response()
        self['teams'] = [TeamInfo(t) for t in self.get('teams', [])]

