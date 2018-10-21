import d2api
from d2api.src.errors import *
from d2api.src.wrappers import *
from d2api.src.entities import *
import unittest
import os

class APIPreliminaryTests(unittest.TestCase):
    def test_environment_api_key_set(self):
        self.assertIsNotNone(os.environ.get('DOTA2_API_KEY'), 
        "DOTA2_API_KEY was not set in environment.")

    def test_correct_api_key(self):
        tmp_api = d2api.APIWrapper("abcdxyz")

        with self.assertRaises(APIAuthenticationError, 
        "Request with API key \"abcdxyz\" should raise authentication error."):
            tmp_api.get_match_details('4176987886')
    
    def test_logger_check(self):
        tmp_api = d2api.APIWrapper(log_enabled = True)
        self.assertIsNotNone(tmp_api.logger, 
        "Logger should not be None when \'log_enabled\' was set to True")

class EntityTests(unittest.TestCase):
    def test_steam_32_64(self):
        steam32 = 123456
        steam64 = 76561197960265728 + steam32
        account1 = SteamAccount(account_id = steam64)
        account2 = SteamAccount(account_id = steam32)
        self.assertEqual(account1, account2,
        "SteamAccount created with 32 Bit or 64 Bit SteamID should be indistinguishable.")
    


class MatchHistoryTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.res = api.get_match_history()
    
    def test_match_history_dtype(self):
        self.assertIsInstance(self.res, MatchHistory, 
        "get_match_history() should return a MatchHistory object")


    






# m = cur.get_match_details('4176987886')

# steamIDs = [114539087, 4294967295, 4294967295, 30633942, 78964422, 4294967295, 283619584, 20778465, 4294967295, 59769890]
if __name__ == "__main__":
    unittest.main()