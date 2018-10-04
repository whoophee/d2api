import api
from api.src import rtypes, wrappers
import pprint
import json
tmp = api.APIWrapper('E0D20CC6B9F3F28C348082F7AC53334F')

res = tmp.get_match_history(skill = 3, min_players = 10, matches_requested = 100)

for match in res.matches():
    print(match.match_id)
