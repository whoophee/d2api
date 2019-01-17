#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging

import requests

from .src import endpoints, wrappers, errors, entities

__author__ = "Raghav Sairam"
__date__ = "25/10/2018"
__license__ = "MIT"

class APIWrapper:
    def __init__(self, api_key = None, language = 'en_us ', parse_results = True, logging_enabled = False):

        self.api_key = api_key if api_key else os.environ.get('D2_API_KEY')

        self.parse_results = parse_results
        self.language = language

        if logging_enabled:
            logger = logging.getLogger("d2api")
            logger.setLevel(logging.DEBUG)
            self.logger = logger
        else:
            logging.getLogger("requests").setLevel(logging.WARNING)


    def api_call(self, url, wrapper_class = lambda x: x, **kwargs):

        if not 'key' in kwargs:
            kwargs['key'] = self.api_key
        
        if not 'language' in kwargs:
            kwargs['language'] = self.language

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
        return self.api_call(endpoints.GET_MATCH_HISTORY, wrappers.MatchHistory, **kwargs)

    def get_match_history_by_sequence_num(self, **kwargs):
        return self.api_call(endpoints.GET_MATCH_HISTORY_BY_SEQ_NUM, wrappers.MatchHistory, **kwargs)

    def get_match_details(self, match_id, **kwargs):
        kwargs['match_id'] = match_id
        return self.api_call(endpoints.GET_MATCH_DETAILS, wrappers.MatchDetails, **kwargs)

    def get_heroes(self, **kwargs):
        return self.api_call(endpoints.GET_HEROES, wrappers.Heroes, **kwargs)

    def get_game_items(self, **kwargs):
        return self.api_call(endpoints.GET_GAME_ITEMS, wrappers.GameItems, **kwargs)
    
    def get_tournament_prize_pool(self, **kwargs):
        return self.api_call(endpoints.GET_TOURNAMENT_PRIZE_POOL, wrappers.TournamentPrizePool, **kwargs)
    
    def get_top_live_game(self, partner = 0, **kwargs):
        kwargs['partner'] = partner
        return self.api_call(endpoints.GET_TOP_LIVE_GAME, wrappers.TopLiveGame, **kwargs)
    
    def get_team_info_by_team_id(self, **kwargs):
        return self.api_call(endpoints.GET_TEAM_INFO_BY_TEAM_ID, wrappers.TeamInfoByTeamID, **kwargs)

    def get_live_league_games(self, **kwargs):
        return self.api_call(endpoints.GET_LIVE_LEAGUE_GAMES, wrappers.LiveLeagueGames, **kwargs)
    
def update_local_data(purge = True):
    entities._update(purge)