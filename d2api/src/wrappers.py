#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Parse wrapper definitions"""

import pprint
from collections.abc import MutableMapping 

from . import entities
from . import util

def _get_side_from_slot(player_slot):
    """Get player team based on player slot"""
    return "radiant" if player_slot < 128 else "dire"

def _get_side_from_team(team):
    """Map integer reference to string"""
    return {0:'radiant', 1:'dire', 2:'broadcaster', 4:'unassigned'}.get(team, 'unassigned')

def _get_subdict(d, keys):
    """Get a subdict with specific keys"""
    return {k: d.get(k) for k in keys}

class Dota2Dict(MutableMapping):
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, val):
        self.data[key] = val
    
    def __delitem__(self, key):
        del self.data[key]
    
    def __iter__(self):
        return self.data.__iter__()
    
    def __len__(self):
        return self.data.__len__()

    def assign_subkey(self, key):
        self.data = self.data.get(key, {})

    def __init__(self, data = None):
        self.data = data if data != None else {}

class AbstractParse(Dota2Dict):
    """Interface to implement parsed objects."""
    def __str__(self):
        return pprint.pformat(self.data)

    def __init__(self, default_obj):
        """
        Parameters
        ----------
        default_obj : dict
            The class wraps around this dict.
        """
        super().__init__(default_obj)
        self.parse()

    def parse(self):
        pass

class AbstractResponse(Dota2Dict):
    """Interface to implement parsed response objects."""
    def __str__(self):
        return pprint.pformat(self.data)

    def __init__(self, response_text):
        self.raw_json = response_text
        super().__init__(util.decode_json(response_text))
        self.parse_response()

    def parse_response(self):
        self.assign_subkey('result')

class PlayerMinimal(AbstractParse):
    """A minimal information wrapper for a player

    Attributes
    ----------
    steam_account : SteamAccount
        Steam account of player
    side : str
        side to which a player belongs (radiant/dire)
    hero : Hero
        hero played
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

    Attributes
    ----------
    match_id : int
        The unique ID of a match
    match_seq_num : int
        Represents the sequence in which matches were recorded
    start_time : int
        Unix timestamp of game begin time
    lobby_type : int
        Integer representing type of lobby
    players : list(PlayerMinimal)
        List of player summaries
    """
    def parse(self):
        self['players'] = [PlayerMinimal(p) for p in self.get('players', [])]

class MatchHistory(AbstractResponse):
    """:any:`get_match_history` or :any:`get_match_history_by_sequence_num` response object

    Attributes
    ----------
    matches : list(MatchSummary)
        List of match summaries
    """
    def parse_response(self):
        self.assign_subkey('result')
        self['matches'] = [MatchSummary(match) for match in self.get('matches', [])]

class InventoryUnit(AbstractParse):
    """Any unit having item slots."""
    def all_items(self):
        """
        Returns
        -------
        list(Item)
            Combined list of inventory and backpack items
        """
        tot = self['inventory'] + self['backpack']
        return tot

    def _build_item_list(self):
        self['inventory'] = []
        self['backpack'] = []

        for item_slot in ['item_{}'.format(i) for i in range(6)]:
            cur_item = entities.Item(self.pop(item_slot, None))
            self['inventory'].append(cur_item)

        for backpack_slot in ['backpack_{}'.format(i) for i in range(3)]:
            cur_item = entities.Item(self.pop(backpack_slot, None))
            self['backpack'].append(cur_item)

class AdditionalUnit(InventoryUnit):
    """An inventoried unit besides heroes (e.g. Lone druid bear)

    Attributes
    ----------
    inventory : list(Item)
        List of inventory items
    backpack : list(Item)
        List of backpack items
    """

    def parse(self):
        self._build_item_list()

class AbilityInfo(AbstractParse):
    """Ability upgrade during game.

    Attributes
    ----------
    ability : Ability
        Ability upgraded.
    time : int
        Game time at which ability was upgraded
    level : int
        Level of the player at which ability was upgraded.
    """
    def parse(self):
        self['ability'] = entities.Ability(self.pop('ability_id', None))

# TODO: add leaver status enumeration

class PlayerUnit(InventoryUnit):
    """An inventoried hero unit

    Attributes
    ----------
    steam_account : SteamAccount
        Steam account of player
    side : str
        Side to which a player belongs (radiant/dire)
    hero : Hero
        Hero played
    kills : int
        Number of kills at the end of the match
    deaths : int
        Number of deaths at the end of the match
    assists : int
        Number of assists at the end of the match
    leaver_status : int
        Type of leaver
    gold : int
        Amount of gold remaining at the end of the match
    last_hits : int
        Number of list hits at the end of the match
    denies : int
        Number of denies at the end of the game
    gold_per_minute : int
        Overall gold/minute
    xp_per_minute : int
        Overall XP/min
    gold_spent : int
        Amount of gold spent during the match
    hero_damage : int
        Total damage done to other heroes at the end of the match
    tower_damage : int
        Total damage done to opponent towers at  the end of the match
    hero_healing : int
        Total healing done to other heroes at the end of the match
    additional_units : list(AdditionalUnit)
        Additional units belonging to the current unit
    inventory : list(Item)
        List of inventory items
    backpack : list(Item)
        List of backpack items
    ability_upgrades : list(AbilityInfo)
        Ability upgrade information
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
            au_list.append(AbilityInfo(au))
        self['ability_upgrades'] = au_list

class Buildings(AbstractParse):
    """Represents current state of buildings

    Attributes
    ----------
    {lane}_{position} : bool
        Tower status [lane = top, mid, bot][position = 1, 2, 3] (e.g. top_t2)
    ancient_bot : bool
        Ancient bottom tower
    ancient_top : bool
        Ancient top tower
    {lane}_{type} : bool
        Barracks status [lane = top, mid, bot][type = ranged, melee] (e.g. mid_melee)
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

    Attributes
    ----------
    is_pick : bool
        ``True`` if the hero was picked
    hero : Hero
        Hero being picked/banned
    side : str
        Side that picked/banned this hero (radiant/dire)
    order : int
        Order in which the hero was picked/banned
    """
    def parse(self):
        self['hero'] = entities.Hero(self.pop('hero_id', None))
        self['side'] = 'dire' if self.pop('team', 0) == 0 else 'radiant'



class MatchDetails(AbstractResponse):
    """:any:`get_match_details` response object

    Attributes
    ----------
    players : PlayerUnit
        List of players in the game
    players_minimal : PlayerMinimal
        List of players represented minimally
    picks_bans : PickBan
        List of picks/bans
    season : int
        The season in which the game was played
    winner : str
        Side that won the game (radiant/dire)
    duration : int
        Duration of the game (in seconds)
    pre_game_duration : int
        Duration for game to begin (in seconds)
    start_time : int
        Unix timestamp of match start
    match_seq_num : int
        Number denoting the order in which matches were recorded
    radiant_buildings : Buildings
        Radiant building statuses at the end of the game
    dire_buildings : Buildings
        Dire building statuses at the end of the game
    cluster : int
        The server cluster the match was played upon (used to fetch replays)
    first_blood_time : int
        Time of first-blood occurrance
    lobby_type : int
        Type of lobby
    human_players : int
        Number of human players in the game
    leagueid : int
        The league that this match was a part of
    positive_votes : int
        The number of thumbs-up the game has received by users
    negative_votes : int
        The number of thumbs-down the game has received by users
    game_mode : int
        Game mode
    engine : int
        Source 1/Source 2
    radiant_score : int
        TODO
    dire_score : int
        TODO
    flags : ?
        TODO
    """
    def leavers(self):
        """
        Returns
        -------
        list(SteamAccount)
            List of leavers in a game.
        """
        return [p['steam_account'] for p in self['players'] if p['leaver_status'] != 0]

    def has_leavers(self):
        """
        Returns
        -------
        bool
            ``True`` if the game contains a leaver
        """
        has_leaver = False
        for p in self['players']:
            has_leaver |= p.get('leaver_status', 0) != 0
        return has_leaver

    def parse_response(self):
        self.assign_subkey('result')

        minimal = lambda x: PlayerMinimal(_get_subdict(x, ['account_id', 'player_slot', 'hero_id']))

        self['players_minimal'] = [minimal(p) for p in self.get('players', [])]
        self['players'] = [PlayerUnit(pl) for pl in self.get('players', [])]

        if 'radiant_win' in self:
            self['winner'] = 'radiant' if self.pop('radiant_win', None) else 'dire'

        picks_bans = [PickBan(pb) for pb in self.get('picks_bans', [])]
        self['picks_bans'] = sorted(picks_bans, key = lambda x: x['order'])


        for side in ['radiant', 'dire']:
            tower_status = self.pop('tower_status_{}'.format(side), None)
            barracks_status = self.pop('barracks_status_{}'.format(side), None)
            self['{}_buildings'.format(side)] = Buildings({'tower_status': tower_status, 'barracks_status': barracks_status})

class LocalizedHero(AbstractParse):
    """Localized hero information

    Attributes
    ----------
    name : str
        Hero name
    id : int
        Hero ID
    localized_name : str
        Name of hero in language specified
    """
    pass

class LocalizedGameItem(AbstractParse):
    """Localized item information

    Attributes
    ----------
    id : int
        Item ID
    name : str
        Item name
    cost : int
        Cost of item
    secret_shop : bool
        True if the item is sold in secret shop
    side_shop : bool
        True if the item is sold in side shop
    recipe : bool
        True if it is a recipe
    localized_name : str
        Name of item in language specified
    """
    pass

class Heroes(AbstractResponse):
    """:any:`get_heroes` response object

    Attributes
    ----------
    heroes : list(LocalizedHero)
        List of localized hero information
    count : int
        Number of heroes returned
    """
    def parse_response(self):
        self.assign_subkey('result')
        self['heroes'] = [LocalizedHero(h) for h in self.get('heroes', [])]

class GameItems(AbstractResponse):
    """:any:`get_game_items` response object

    Attributes
    ----------
    game_items : list(LocalizedGameItems)
        List of localized item information
    """
    def parse_response(self):
        self.assign_subkey('result')
        self['game_items'] = [LocalizedGameItem(i) for i in self.pop('items', [])]

class TournamentPrizePool(AbstractResponse):
    """:any:`get_tournament_prize_pool` response object

    Attributes
    ----------
    prize_pool : int
        Prize pool
    league_id : int
        League ID for which prize pool was fetched
    """
    pass

# TODO: add enumeration for state of ultimate
class PlayerLive(AbstractParse):
    """Information of a player in live game

    Attributes
    ----------
    player_slot : int
        Slot of player within the team
    steam_account : SteamAccount
        Steam account of the player
    hero : Hero
        Hero played
    kills : int
        Number of kills
    deaths : int
        Number of deaths
    assists : int
        Number of assists
    last_hits : int
        Number of last hits
    denies : int
        Number of denies
    gold : int
        Current amount of gold
    level : int
        Current level
    gold_per_min : int
        gold/min at time of query
    xp_per_min : int
        XP/min at time of query
    abilities : list(AbilityInfo)
        List of ability information
    ultimate_state : int
        Current state of ultimate
    ultimate_cooldown : int
        Remaining time for ultimate to come off cooldown
    inventory : list(Item)
        List of items in player inventory
    respawn_timer : int
        Remain time for player to respawn
    position_x : float
        X coordinate of hero
    position_y : float
        Y coordinate of hero
    net_worth : int
        Net worth of the hero
    """
    def parse(self):
        self['hero'] = entities.Hero(self.pop('hero_id', None))
        self['steam_account'] = entities.SteamAccount(self.pop('account_id', None))

        self['deaths'] = self.pop('death', 0)

        self['inventory'] = [entities.Item(self.pop('item{}'.format(i), None)) for i in range(6)]

        self['abilities'] = [AbilityInfo(au) for au in self.get('abilities', [])]

class TeamLive(AbstractParse):
    """Information of a team in live game

    Attributes
    ----------
    score : int
        Current number of kills by the team
    buildings : Buildings
        State of buildings
    picks : list(Hero)
        List of heroes picked
    bans : list(Hero)
        List of heroes banned
    players : list(PlayerLive)
        List of player summaries
    """
    def parse(self):

        tower_status = self.get('tower_state')
        barracks_status = self.get('barracks_state')
        self['buildings'] = Buildings({'tower_status': tower_status, 'barracks_status': barracks_status})

        self['picks'] = [entities.Hero(h['hero_id']) for h in self.get('picks', [])]
        self['bans'] = [entities.Hero(h['hero_id']) for h in self.get('bans', [])]

        players = self.get('players', [])
        # because the WebAPI is stupid
        # Steam WebAPI returns multiple entries with the same name which I can only assume correspond to each player
        # util.decode_json describes the modified parser (to handle repeated names)
        for i, player in enumerate(players):
            player['abilities'] = self.pop('abilities_{}'.format(i), [])

        self.pop("abilities", None)

        self['players'] = [PlayerLive(p) for p in players]

class Scoreboard(AbstractParse):
    """Scoreboard of live game

    Attributes
    ----------
    duration : int
        Duration of the game at time of query
    roshan_respawn_timer : int
        Time left for Roshan to respawn
    radiant : TeamLive
        Radiant team summary
    dire : TeamLive
        Dire team summary
    """
    def parse(self):
        self['radiant'] = TeamLive(self.get('radiant', {}))
        self['dire'] = TeamLive(self.get('dire', {}))

class TeamInfo(AbstractParse):
    """Information about team

    Attributes
    ----------
    team_name : str
        The team's name.
    team_id : int
        The team's unique ID.
    team_logo : int
        The UGC id for the team logo.
    complete : bool
        Whether the players for this team are all team members.
    """
    pass

# TODO: enumerate series type
class Game(AbstractParse):
    """Summary of a live league game

    Attributes
    ----------
    radiant_team : TeamInfo
        Radiant team information
    dire_team : TeamInfo
        Dire team information
    players : List(PlayerMinimal)
        List of players in the game
    scoreboard : Scoreboard
        Game scoreboard at time of query
    lobby_id : int
        ID of lobby
    match_id : int
        Unique ID used to identify match
    spectators : int
        Number of spectators
    league_id : int
        Unique ID for the league of the match
    league_node_id : int
        Unique ID of node within the league
    stream_delay_s : int
        Stream delay in seconds
    radiant_series_win : int
        Number of wins by radiant team
    dire_series_win : int
        Number of wins by dire team
    series_type : int
        Type of series
    """
    def parse(self):
        self['radiant_team'] = TeamInfo(self.get('radiant_team', {}))
        self['dire_team'] = TeamInfo(self.get('dire_team', {}))
        self['scoreboard'] = Scoreboard(self.get('scoreboard', {}))
        self['players'] = [PlayerMinimal(p) for p in self.get('players', [])]

class LiveLeagueGames(AbstractResponse):
    """:any:`get_live_league_games` response object

    Attributes
    ----------
    games : list(Game)
        List of games
    """
    def parse_response(self):
        self.assign_subkey('result')
        self['games'] = [Game(g) for g in self['games']]

# TODO: add lobby type enumeration
# TODO: add game mode enumeration
class LiveGameSummary(AbstractParse):
    """Summary of a live game

    Attributes
    ----------
    players : PlayerMinimal
        List of player info
    radiant_towers : Buildings
        Radiant towers
    dire_towers : Buildings
        Dire towers
    activate_time : int
        TODO
    deactivate_time : int
        TODO
    server_steam_id : int
        Steam ID of server
    lobby_id : int
        ID of lobby
    league_id : int
        Unique ID for the league of the match
    lobby_type : int
        Type of lobby
    game_time : int
        Game time
    delay : int
        Stream delay (game, spectator delay)
    spectators : int
        Current number of spectators
    game_mode : int
        Game mode of current game
    average_mmr : int
        Average MMR of the game
    match_id : int
        Unique ID used to identify match
    series_id : int
        Unique ID used to identify series
    radiant_team : TeamInfo
        Information about radiant team
    dire_team : TeamInfo
        Information about dire team
    sort_score : int
        TODO
    last_update_time : int
        TODO
    radiant_lead : int
        Gold lead of radiant team
    radiant_score : int
        TODO
    dire_score : int
        TODO
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
    """:any:`get_top_live_game` response object

    Attributes
    ----------
    game_list : list(LiveGameSummary)
        List of top live games
    """
    def parse_response(self):
        self['game_list'] = [LiveGameSummary(g) for g in self.get('game_list', [])]

class TeamInfoByTeamID(AbstractResponse):
    """:any:`get_team_info_by_team_id` response object

    Attributes
    ----------
    teams : list(TeamInfo)
        List of team information
    """
    def parse_response(self):
        self.assign_subkey('result')
        self['teams'] = [TeamInfo(t) for t in self.get('teams', [])]

class BroadcasterInfo(AbstractResponse):
    """:any:`get_broadcaster_info` response object

    Attributes
    ----------
    steam_account : SteamAccount
        Steam account of broadcaster
    server_steam_id : int
        Unique ID of game server currently being broadcasted
    live : bool
        ``True`` if the user is currently broadcasting
    allow_live_video : bool
        ``True`` if the user has allowed live video
    """
    def parse_response(self):
        self['steam_account'] = entities.SteamAccount(self.pop('account_id', None))

class SteamDetails(AbstractParse):
    """Information about a player as on Steam.

    Attributes
    ----------
    steam_account : SteamAccount
        Steam account of the player
    communityvisibility : str
        A string representing the access setting of the profile
    profilestate : int
        Set to ``1`` if the user has configured their profile
    personname : str
        Display name
    lastlogoff : int
        Unix timestamp of when the player was last online
    profileurl : str
        The URL to the user's steam profile
    avatar : str
        URL of 32x32 image
    avatarmedium : str
        URL of 64x64 image
    avatarfull : str
        URL of 184x184 image
    personastate : str
        A string representing user's status
    commentpermission : int
        If present the profile allows public comments
    realname : str
        The user's real name
    primaryclanid : int
        The 64 bit ID of the user's primary group
    timecreated : int
        A unix timestamp of the date the profile was created
    loccountrycode : int
        ISO 3166 code of where the user is located
    locstatecode : int
        Variable length code representing the state the user is located in
    loccityid : int
        An integer ID internal to Steam representing the user's city
    gameid : int
        If the user is in game this will be set to it's app ID as a string
    gameextrainfo : str
        The title of the game
    gameserverip : str
        The server URL given as an IP address and port number
    """
    def parse(self):
        self['steam_account'] = entities.SteamAccount(self.get('steamid'))

        comm_descr = {
            1: 'private',
            2: 'friends_only',
            3: 'friends_of_friends',
            4: 'users_only',
            5: 'public'
        }

        self['communityvisibility'] = comm_descr[self.pop('communityvisibilitystate', 1)]

        persona_descr = {
            0: 'offline',
            1: 'online',
            2: 'busy',
            3: 'away',
            4: 'snooze',
            5: 'looking_to_trade',
            6: 'looking_to_play'
        }
        self['personastate'] = persona_descr[self.pop('personastate', 0)]

class PlayerSummaries(AbstractResponse):
    """:any:`get_player_summaries` response object

    Attributes
    ----------
    players : list(SteamDetails)
        List of steam information in ascending order of account ids
    """
    def parse_response(self):
        self.assign_subkey('response')
        # For some reason, the WebAPI doesn't maintain relative ordering. Sorted to make the response consistent.
        self['players'] = sorted([SteamDetails(p) for p in self.get('players', [])], key = lambda x: x['steam_account']['id64'])