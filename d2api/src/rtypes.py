from .wrappers import *

class GenericResponse(BaseWrapper):
    def json(self):
        return self.raw_json

    def _parse(self, response_json):
        upper_keys = list(response_json.keys())
        if len(upper_keys) == 1:
            self._obj = response_json[upper_keys[0]]
        else:
            self._obj = response_json

    def __init__(self, response, raw = False):
        self.raw_json = response.content
        self._obj = {}
        if not raw:
            self._parse(response.json())

class MatchHistoryResponse(GenericResponse):
    def matches(self):
        return self._matches.__iter__()

    def _parse(self, response_json):
        self._obj = response_json.get('result', {})
        self._matches = [MatchSummary(match) for match in self._obj.get('matches', [])]
        self._obj.pop('matches', None)
