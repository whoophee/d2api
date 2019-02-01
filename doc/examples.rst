Examples
########

Example 1
=========

.. code-block:: python

   import d2api

   api = d2api.APIWrapper()

   # fetch latest matches
   match_history = api.get_match_history()

   # extract heroes playing in the most recently recorded game
   heroes = [player['hero'] for player in match_history['matches'][0]['players']]

   # Print list of all heroes playing in that game
   print(heroes)

Example 2
=========

.. code-block:: python
   
   import d2api
   from d2api.src import entities

   # These arguments accomplish the same thing.
   by_hero_id = api.get_match_history(hero_id = 67)
   by_hero = api.get_match_history(hero = entities.Hero(67))

   # As do these
   by_steam_id = api.get_match_history(account_id = 1234)
   by_steam_account = api.get_match_history(steam_account = entities.SteamAccount(1234))