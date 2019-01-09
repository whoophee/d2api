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
    def __init__(self, api_key = None, logging_enabled = False):

        self.api_key = api_key if api_key else os.environ.get('D2_API_KEY')
        if logging_enabled:
            logger = logging.getLogger("d2api")
            logger.setLevel(logging.DEBUG)
            self.logger = logger
        else:
            logging.getLogger("requests").setLevel(logging.WARNING)


    def api_call(self, url = endpoints.GET_MATCH_HISTORY, **kwargs):
        kwargs['key'] = self.api_key
        response = requests.get(url, params = kwargs, timeout = 60)
        status = response.status_code
        if status == 200:
            return response
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
        api_response = self.api_call(endpoints.GET_MATCH_HISTORY, **kwargs)
        return wrappers.MatchHistory(api_response)

    def get_match_history_by_sequence_num(self, **kwargs):
        api_response = self.api_call(endpoints.GET_MATCH_HISTORY_BY_SEQ_NUM, **kwargs)
        return wrappers.MatchHistory(api_response)

    def get_match_details(self, match_id, **kwargs):
        kwargs['match_id'] = match_id
        api_response = self.api_call(endpoints.GET_MATCH_DETAILS, **kwargs)
        return wrappers.MatchDetails(api_response)

    def get_heroes(self, **kwargs):
        kwargs['language'] = kwargs.get('language', 'en_us')
        api_response = self.api_call(endpoints.GET_HEROES, **kwargs)
        return wrappers.Heroes(api_response)

    def get_game_items(self, **kwargs):
        kwargs['language'] = kwargs.get('language', 'en_us')
        api_response = self.api_call(endpoints.GET_GAME_ITEMS, **kwargs)
        return wrappers.GameItems(api_response)
    
    def update_local_data(self, purge = True):
        entities.update_local_data(purge)