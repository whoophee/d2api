import os
import requests
from .src import endpoints
from .src.rtypes import *

def _logger_instance():
    import logging
    logging.basicConfig(level = logging.DEBUG)
    return logging.getLogger(__name__)

class APIWrapper:
    def __init__(self, api_key = None, raw = False, logging = False):

        self.api_key = api_key if api_key else os.environ.get('DOTA2_KEY', None)
        self.logger = _logger_instance() if logging else None
        self.raw = raw


    def __api_call(self, url = endpoints.MATCH_HISTORY, **kwargs):
        kwargs['key'] = self.api_key
        response = requests.get(url, params = kwargs)

        if response.status_code == 200:
            return response
        else:
            raise Exception('HTTP {}: {}'.format(response.status_code, response.reason))

    def get_match_history(self, **kwargs):
        api_response = self.__api_call(endpoints.MATCH_HISTORY, **kwargs)
        return MatchHistoryResponse(api_response, self.raw)
