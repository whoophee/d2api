#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import requests

from .src import endpoints, entities, errors, wrappers

def _parse_steam_account(cur_args):
    """steam_account/account_id parse helper"""
    account_id = None

    if 'account_id' in cur_args:
        account_id = entities.SteamAccount(cur_args['account_id'])['id64']
    
    if 'steam_account' in cur_args:
        account_id = cur_args.pop('steam_account')['id64']
    
    cur_args['account_id'] = account_id

def _parse_hero(cur_args):
    """hero/hero_id parse helper"""

    if 'hero' in cur_args:
        cur_args['hero_id'] = cur_args.pop('hero')['hero_id']

def _parse_steam_account_list(cur_args):
    """account_ids/steam_accounts parse helper"""
    account_ids = None

    if 'account_ids' in cur_args:
        account_ids = ','.join([str(entities.SteamAccount(s)['id64']) for s in cur_args.pop('account_ids')])
    
    if 'steam_accounts' in cur_args:
        account_ids = ','.join([str(s['id64']) for s in cur_args.pop('steam_accounts')])

    cur_args['steamids'] = account_ids



class APIWrapper:
    """Wrapper initialization requires either environment variable ``D2_API_KEY`` be set, or ``api_key`` be provided as an argument.

    :param api_key: Steam API key
    :param parse_response: set to ``False`` to get an unparsed json string (default ``True``)

    :type api_key: str
    :type parse_response: bool, optional
    """
    def __init__(self, api_key = None, parse_response = True):
        self.api_key = api_key if api_key else os.environ.get('D2_API_KEY')

        self.parse_response = parse_response


    def _api_call(self, url, wrapper_class = wrappers.BaseWrapper, **kwargs):
        """Helper function to perform WebAPI requests.

        :param url: Request url
        :param wrapper_class: Wrapper class used to parse response

        :type url: string, required
        :type wrapper_class: Class
        """
        if not 'key' in kwargs:
            kwargs['key'] = self.api_key

        response = requests.get(url, params = kwargs, timeout = 60)
        status = response.status_code

        if status == 200:
            return wrapper_class(response.text) if self.parse_response else response.text
        elif status == 403:
            raise errors.APIAuthenticationError(self.api_key)
        elif status == 404:
            raise errors.APIMethodUnavailable(url)
        elif status == 503: # pragma: no cover
            raise errors.APITimeoutError()
        elif status == 400:
            raise errors.APIInsufficientArguments(url, kwargs)
        else: # pragma: no cover
            raise errors.BaseError(msg = response.reason)

    def get_match_history(self, **kwargs):
        """A list of matches, filterable by various parameters.
        
        :param hero_id: A list of hero IDs can be fetched via the :py:meth:`~d2api.APIWrapper.get_heroes` method
        :param hero: Used in place of hero_id
        :param game_mode: Games of this game mode are fetched
        :param skill: Skill bracket for the matches (Ignored if an account ID is specified)
        :param min_players: Minimum amount of players in a match for the match to be returned.
        :param account_id: 32/64-bit account ID
        :param steam_account: Used in place of account_id
        :param league_id: Only return matches from this league. get_league_listing() has been discontinued
        :param start_at_match_id: Start searching for matches equal to or older than this match ID
        :param matches_requested: Defaults to `100`
        :param tournament_games_only: 0 = False, 1 = True

        :type hero_id: int, optional
        :type hero: Hero, optional
        :type game_mode: int, optional
        :type skill: int, optional
        :type min_players: int, optional
        :type account_id: int, optional
        :type steam_account: SteamAccount, optional
        :type league_id: int, optional
        :type start_at_match_id: int, optional
        :type matches_requested: int, optional
        :type tournament_games_only: int, optional

        :rtype: MatchHistory 
        """
        _parse_steam_account(kwargs)
        _parse_hero(kwargs)
        return self._api_call(endpoints.GET_MATCH_HISTORY, wrappers.MatchHistory, **kwargs)

    def get_match_history_by_sequence_num(self, **kwargs):
        """A list of matches ordered by sequence number. 
        Uses a parser similar to that of :py:meth:`~d2api.APIWrapper.get_match_history` method
        
        :param start_at_match_seq_num: The match sequence number to start returning results from
        :param matches_requested: Defaults to `100`

        :type start_at_match_seq_num: int
        :type matches_requested: int, optional

        :rtype: MatchHistory
        """
        return self._api_call(endpoints.GET_MATCH_HISTORY_BY_SEQ_NUM, wrappers.MatchHistory, **kwargs)

    def get_match_details(self, match_id, **kwargs):
        """Detailed information about a particular match.
        
        :param match_id: Match ID

        :type match_id: int, string

        :rtype: MatchDetails
        """
        kwargs['match_id'] = match_id
        return self._api_call(endpoints.GET_MATCH_DETAILS, wrappers.MatchDetails, **kwargs)

    def get_heroes(self, **kwargs):
        """A list of heroes in Dota 2.
        
        :param language: The `language <https://partner.steamgames.com/doc/store/localization#supported_languages>`_ to provide hero names in
        :param itemizedonly: Return a list of itemized heroes only

        :type language: string, optional
        :type itemizedonly: bool, optional

        :rtype: Heroes
        """
        return self._api_call(endpoints.GET_HEROES, wrappers.Heroes, **kwargs)

    def get_game_items(self, **kwargs):
        """A list of items in Dota 2.
        
        :param language: The `language <https://partner.steamgames.com/doc/store/localization#supported_languages>`_ to provide hero names in

        :type language: string, optional

        :rtype: GameItems
        """
        return self._api_call(endpoints.GET_GAME_ITEMS, wrappers.GameItems, **kwargs)
    
    def get_tournament_prize_pool(self, **kwargs):
        """The current prizepool of specific tournaments.
        
        :param leagueid: The ID of the league to get the prize pool of

        :type leagueid: int

        :rtype: TournamentPrizePool
        """
        return self._api_call(endpoints.GET_TOURNAMENT_PRIZE_POOL, wrappers.TournamentPrizePool, **kwargs)
    
    def get_top_live_game(self, partner = 0, **kwargs):
        """Details of on-going live games.
        
        :param partner: Which partner's games to use (default `0`)

        :type partner: int, optional

        :rtype: TopLiveGame
        """
        kwargs['partner'] = partner
        return self._api_call(endpoints.GET_TOP_LIVE_GAME, wrappers.TopLiveGame, **kwargs)
    
    def get_team_info_by_team_id(self, **kwargs):
        """A list of teams' information.
        
        :param start_at_team_id: The team id to start returning results from
        :param teams_requested: The amount of teams to return

        :type start_at_team_id: int, optional
        :type teams_requested: int, optional

        :rtype: TeamInfoByTeamID
        """
        return self._api_call(endpoints.GET_TEAM_INFO_BY_TEAM_ID, wrappers.TeamInfoByTeamID, **kwargs)

    def get_live_league_games(self, **kwargs):
        """A list of in-progress league matches, as well as their details at the time of query.
        
        :rtype: LiveLeagueGames"""
        return self._api_call(endpoints.GET_LIVE_LEAGUE_GAMES, wrappers.LiveLeagueGames, **kwargs)

    def get_broadcaster_info(self, **kwargs):
        """Get the broadcasting status of a user.

        :param account_id: 32/64-bit account ID
        :param steam_account: Used in place of account_id

        :type account_id: int
        :type steam_account: SteamAccount

        :rtype: BroadcasterInfo
        """
        _parse_steam_account(kwargs)
        kwargs['broadcaster_steam_id'] = kwargs.pop('account_id')
        return self._api_call(endpoints.GET_BROADCASTER_INFO, wrappers.BroadcasterInfo, **kwargs)

    def get_player_summaries(self, **kwargs):
        """Get Steam details of users.

        :param account_ids: 32/64-bit account ID
        :param steam_accounts: Used in place of account IDs

        :type account_ids: list(int)
        :type steam_accounts: list(SteamAccount)

        :rtype: PlayerSummaries
        """
        _parse_steam_account_list(kwargs)
        return self._api_call(endpoints.GET_PLAYER_SUMMARIES, wrappers.PlayerSummaries, **kwargs)


def update_local_data(purge = True):
    """Synchronize local data with current repository data
    
    :param purge: Set to ``True`` to delete local content

    :type purge: bool
    """
    return entities._update(purge)
