import json
import os
from prettyprinter import pprint
from io import StringIO
import d2api
from functools import partial

def path_to_doc(x = ''):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), 'doc', x))


def resolve_path(path_inp):
    ret = []
    for p in path_inp.split('$')[1:]:
        if p[-2:] == '[]':
            ret.append('list({})'.format(p[:-2]))
        else:
            ret.append(p)
    return ret

class QuickRef:
    def __init__(self, funcs = []):
        self.partials = funcs
        self.md = []
    
    def add_func(self, name, partialfunc):
        self.partials.append((name, partialfunc))

    def generate_all(self):
        for name, func in self.partials:
            self.generate_quickref(func(), name)
        
        self.generate_markdown()


    def _find_structure(self, inp_json, cur_path = ""):

        self.all_paths.add(cur_path)

        cur_iter = []

        t = None

        if issubclass(inp_json.__class__, dict): 
            cur_iter = list(inp_json.keys())
            t = 'dict'

        if isinstance(inp_json, list):
            cur_iter = list(range(len(inp_json)))
            t = 'list'
        
        for x in cur_iter:
            if t == 'list':
                new_path = "{}[]".format(cur_path)
            else:
                new_path = "{}${}".format(cur_path, x)

            self._find_structure(inp_json[x], new_path)

    def generate_quickref(self, curdict, fname):

        self.all_paths = set()

        self._find_structure(curdict)
        refined = []
        for p in sorted(self.all_paths):
            if p[-2:] == '[]':
                refined.pop()
            if p:
                refined.append(p)

        jsonroot = {}

        for p in refined:
            cur = jsonroot
            cur_paths = resolve_path(p)
            leaf = cur_paths.pop()
            for x in cur_paths:
                cur = cur[x]
            cur[leaf] = {}

        output = StringIO()

        pprint(jsonroot, stream=output)

        output.seek(0)
        output = output.read()

        output = output.replace(": {}", "").replace("'", "")
        self.md.append((fname, output))
        
    
    def generate_markdown(self):
        with open(path_to_doc("quickref.md"), 'w') as f:
            f.write("# Quick Reference\n")
            f.write("Below, is the generic dictionary access structure for any of the given endpoints.\n")
            for fname, content in self.md:
                f.write("\n## {}\n\n".format(fname))
                for c in content.split("\n"):
                    f.write("    {}\n".format(c))

api = d2api.APIWrapper()

qr = QuickRef()
qr.add_func("get_match_history()", api.get_match_history)
qr.add_func("get_match_details()", partial(api.get_match_details, '4176987886'))
qr.add_func("get_heroes()", partial(api.get_heroes, language = "en_us"))
qr.add_func("get_game_items()", partial(api.get_game_items, language = "en_us"))
qr.add_func("get_tournament_prize_pool()", api.get_tournament_prize_pool)
qr.add_func("get_top_live_game()", api.get_top_live_game)
qr.add_func("get_team_info_by_team_id()", api.get_team_info_by_team_id)
qr.add_func("get_live_league_games()", api.get_live_league_games)
qr.add_func("get_broadcaster_info()", partial(api.get_broadcaster_info, account_id = '76561198088874284'))
qr.add_func("get_player_summaries()", partial(api.get_player_summaries, account_ids = [1, 2]))
qr.generate_all()