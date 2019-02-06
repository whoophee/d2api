Documentation
#############

There are several response types/entities accross the different endpoints of the `Dota 2 WebAPI <https://wiki.teamfortress.com/wiki/WebAPI#Dota_2>`_. 
This API aims at removing inconsistencies and unifying the response content. 

All variables belonging to a class are accessed using the ``__getitem__`` method (similar to a dict). See :ref:`examples <tutorial-examples>` 
for more details.


.. py:module:: d2api.src.wrappers

get_match_history()
===================
.. autoclass:: MatchHistory
   :members:

.. autoclass:: MatchSummary
   :members:

get_match_details()
===================
.. autoclass:: MatchDetails
   :members:

.. autoclass:: PlayerUnit
   :members: all_items

.. autoclass:: AdditionalUnit
   :members: all_items

.. autoclass:: PickBan
   :members:

get_heroes()
============
.. autoclass:: Heroes
   :members:

.. autoclass:: LocalizedHero
   :members:

get_game_items()
================
.. autoclass:: GameItems
   :members:

.. autoclass:: LocalizedGameItem
   :members:

get_tournament_prize_pool()
===========================
.. autoclass:: TournamentPrizePool
   :members:

get_live_league_games()
=======================
.. autoclass:: LiveLeagueGames
   :members:

.. autoclass:: Game
   :members:

.. autoclass:: Scoreboard
   :members:

.. autoclass:: TeamLive
   :members:

.. autoclass:: PlayerLive
   :members:

get_top_live_game()
===================
.. autoclass:: TopLiveGame
   :members:

.. autoclass:: LiveGameSummary
   :members:

get_team_info_by_team_id()
==========================
.. autoclass:: TeamInfoByTeamID
   :members:

get_broadcaster_info()
======================
.. autoclass:: BroadcasterInfo
   :members:

get_player_summaries()
======================
.. autoclass:: PlayerSummaries
   :members:

.. autoclass:: SteamDetails
   :members:

Common wrappers and entities
============================
.. autoclass:: TeamInfo
   :members:

.. autoclass:: AbilityInfo
   :members:

.. autoclass:: Buildings
   :members:

.. autoclass:: PlayerMinimal
   :members:

.. py:module:: d2api.src.entities

.. autoclass:: Ability
   :members:

.. autoclass:: Item
   :members:

.. autoclass:: SteamAccount
   :members:

.. autoclass:: Hero
   :members: