#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging

import requests

from .src import endpoints, wrappers, errors, entities

__author__ = "Raghav Sairam"
__date__ = "25/10/2018"
__license__ = "MIT"

def parse_get_match_history(cur_args):
    if 'account_id' in cur_args:
        cur_args['account_id'] = entities.SteamAccount(cur_args['account_id'])['id32']
    
    if 'steam_account' in cur_args:
        cur_args['account_id'] = cur_args.pop('steam_account')['id32']
    
    if 'hero' in cur_args:
        cur_args['hero_id'] = cur_args.pop('hero')['hero_id']
        

# TODO: Link argument datatypes to appropriate class definition
class APIWrapper:
    """Wrapper initialization requires either environment variable ``D2_API_KEY`` be set, or ``api_key`` be provided as an argument.

    :param api_key: Steam API key
    :param parse_results: set to ``False`` to get plain json dict (default ``True``)
    :param logging_enabled: set to ``True`` to enable logging (default ``False``)

    :type api_key: str
    :type parse_results: bool, optional
    :type logging_enabled: bool, optional
    """
    def __init__(self, api_key = None, parse_results = True, logging_enabled = False):
        self.api_key = api_key if api_key else os.environ.get('D2_API_KEY')

        self.parse_results = parse_results

        if logging_enabled:
            logger = logging.getLogger("d2api")
            logger.setLevel(logging.DEBUG)
            self.logger = logger
        else:
            logging.getLogger("requests").setLevel(logging.WARNING)


    def _api_call(self, url, wrapper_class = wrappers.BaseWrapper, **kwargs):
        """Helper function to perform WebAPI requests.

        :param url: Request url
        :param wrapper_class: Wrapper class used to parse response

        :type url: string, required
        :type wrapper_class: Class
        """
        if not wrapper_class:
            wrapper_class = lambda x: x

        if not 'key' in kwargs:
            kwargs['key'] = self.api_key

        response = requests.get(url, params = kwargs, timeout = 60)
        status = response.status_code
        
        if status == 200:
            return wrapper_class(response) if self.parse_results else response.json()
        elif status == 403:
            raise errors.APIAuthenticationError(self.api_key)
        elif status == 404:
            raise errors.APIMethodUnavailable(url)
        elif status == 503:
            raise errors.APITimeoutError()
        elif status == 400:
            raise errors.APIInsufficientArguments(url, kwargs)
        else:
            raise errors.BaseError(msg = response.reason)

    def get_match_history(self, **kwargs):
        """:param hero_id: A list of hero IDs can be fetched via the :py:meth:`~d2api.APIWrapper.get_heroes` method
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
        """
        parse_get_match_history(kwargs)
        return self._api_call(endpoints.GET_MATCH_HISTORY, wrappers.MatchHistory, **kwargs)

    def get_match_history_by_sequence_num(self, **kwargs):
        """:param start_at_match_seq_num: The match sequence number to start returning results from
        :param matches_requested: Defaults to `100`

        :type start_at_match_seq_num: int
        :type matches_requested: int, optional
        """
        return self._api_call(endpoints.GET_MATCH_HISTORY_BY_SEQ_NUM, wrappers.MatchHistory, **kwargs)

    def get_match_details(self, match_id, **kwargs):
        """:param match_id: Match ID

        :type match_id: string
        """
        kwargs['match_id'] = match_id
        return self._api_call(endpoints.GET_MATCH_DETAILS, wrappers.MatchDetails, **kwargs)

    def get_heroes(self, **kwargs):
        """:param language: The `language <https://partner.steamgames.com/doc/store/localization#supported_languages>`_ to provide hero names in
        :param itemizedonly: Return a list of itemized heroes only

        :type language: string, optional
        :type itemizedonly: bool, optional
        """
        return self._api_call(endpoints.GET_HEROES, wrappers.Heroes, **kwargs)

    def get_game_items(self, **kwargs):
        """:param language: The language to provide hero names in

        :type language: string, optional
        """
        return self._api_call(endpoints.GET_GAME_ITEMS, wrappers.GameItems, **kwargs)
    
    def get_tournament_prize_pool(self, **kwargs):
        """:param leagueid: The ID of the league to get the prize pool of

        :type leagueid: int
        """
        return self._api_call(endpoints.GET_TOURNAMENT_PRIZE_POOL, wrappers.TournamentPrizePool, **kwargs)
    
    def get_top_live_game(self, partner = 0, **kwargs):
        """:param partner: Which partner's games to use (default `0`)

        :type partner: int, optional
        """
        kwargs['partner'] = partner
        return self._api_call(endpoints.GET_TOP_LIVE_GAME, wrappers.TopLiveGame, **kwargs)
    
    def get_team_info_by_team_id(self, **kwargs):
        """:param start_at_team_id: The team id to start returning results from
        :param teams_requested: The amount of teams to return

        :type start_at_team_id: int, optional
        :type teams_requested: int, optional
        """
        return self._api_call(endpoints.GET_TEAM_INFO_BY_TEAM_ID, wrappers.TeamInfoByTeamID, **kwargs)

    def get_live_league_games(self, **kwargs):
        """No parameters.
        """
        return self._api_call(endpoints.GET_LIVE_LEAGUE_GAMES, wrappers.LiveLeagueGames, **kwargs)

def update_local_data(purge = True):
    """Synchronize local data with current repository data"""
    entities._update(purge)