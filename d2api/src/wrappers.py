from pathlib import Path

def load_json(file_name):
    try:
        f = open(Path('../../../data/{}'.format(filename)), 'r')
        return json.load(f)
    except IOError:
        return None

heroes = {}


class BaseWrapper:
    def __getattr__(self, attr):
        return self._obj[attr]

    def __init__(self, **kwargs):
        self._obj = kwargs

class Hero:
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.hero_id == other.hero_id and self.hero_name == other.hero_name
        return False

    def __init__(self, hero_id = 0):
        if hero_id is None:
            self.hero_id = self.hero_name = None

        self.hero_id = hero_id
        self.hero_name = heroes.get(hero_id, 'unknown_hero')

class Player:
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id32 == other.id32 and self.id64 == other.id64
        return False

    def __init__(self, steam_id):
        if steam_id is None:
            self.id32 = self.id64 = None
            return

        steam64 = 76561197960265728
        if steam_id < steam64:
            self.id32 = steam_id
            self.id64 = steam_id + steam64
        else:
            self.id32 = steam_id - steam64
            self.id64 = steam_id

class MatchSummary(BaseWrapper):
    def heroes(self):
        return [p['hero'] for p in self._players]

    def players(self):
        return self._players.__iter__()

    def __init__(self, match_json):
        """Returns a MatchSummary object with helper functions

        :return: MatchSummary object
        """
        side = lambda x: "radiant" if x < 128 else "dire"
        players = []

        for player in match_json.get('players', []):
            p = Player(player.get('account_id'))
            s = side(player.get('player_slot', 0))
            h = Hero(player.get('hero_id'))
            players.append(BaseWrapper(player = p, side = s, hero = h))

        match_json.pop('players', None)
        self._obj = match_json
        self._players = players
