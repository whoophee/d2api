#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time

import requests

from .src import endpoints, entities, errors, wrappers

# Decorator to limit API request rate
def rate_limited(max_per_second):
    min_interval = 1.0 / float(max_per_second)
    def decorate(func):
        last_time_called = [0.0]
        def rate_limited_function(*args,**kargs):
            elapsed = time.clock() - last_time_called[0]
            left = min_interval - elapsed
            if left > 0:
                time.sleep(left)
            ret = func(*args,**kargs)
            last_time_called[0] = time.clock()
            return ret
        return rate_limited_function
    return decorate


def _parse_steam_account(cur_args):
    """steam_account/account_id parse helper"""
    account_id = None

    if 'account_id' in cur_args:
        account_id = entities.SteamAccount(cur_args['account_id'])['id64']

    if 'steam_account' in cur_args:
        account_id = cur_args.pop('steam_account')['id64']

    cur_args['account_id'] = account_id

def _parse_hero(cur_args):
    """hero/hero_id parse helper"""

    if 'hero' in cur_args:
        cur_args['hero_id'] = cur_args.pop('hero')['hero_id']

def _parse_steam_account_list(cur_args):
    """account_ids/steam_accounts parse helper"""
    account_ids = None

    if 'account_ids' in cur_args:
        account_ids = ','.join([str(entities.SteamAccount(s)['id64']) for s in cur_args.pop('account_ids')])

    if 'steam_accounts' in cur_args:
        account_ids = ','.join([str(s['id64']) for s in cur_args.pop('steam_accounts')])

    cur_args['steamids'] = account_ids



class APIWrapper:
    """Wrapper initialization requires either environment variable ``D2_API_KEY`` be set, or ``api_key`` be provided as an argument.

    Parameters
    ----------
    api_key : str
        Steam API key
    parse_response : bool
        set to ``False`` to get an unparsed json string
    """
    def __init__(self, api_key = None, parse_response = True):
        self.api_key = api_key if api_key else os.environ.get('D2_API_KEY')

        self.parse_response = parse_response

    @rate_limited(1)
    def _api_call(self, url, wrapper_class = lambda x: x, **kwargs):
        """Helper function to perform WebAPI requests.

        Parameters
        ----------
        url : string
            Request url
        wrapper_class : Class
            Wrapper class used to parse response
        """
        if not 'key' in kwargs:
            kwargs['key'] = self.api_key

        response = requests.get(url, params = kwargs, timeout = 60)
        status = response.status_code

        if status == 200:
            if self.parse_response:
                current_response = wrapper_class(response.text)
                current_response.url = response.url
                return current_response
            else:
                return response.text
        elif status == 403:
            raise errors.APIAuthenticationError(self.api_key)
        elif status == 404:
            raise errors.APIMethodUnavailable(url)
        elif status == 503: # pragma: no cover
            raise errors.APITimeoutError()
        elif status == 400:
            raise errors.APIInsufficientArguments(url, kwargs)
        else: # pragma: no cover
            raise errors.BaseError(msg = response.reason)

    def get_match_history(self, **kwargs):
        """Get a list of matches, filtered by various parameters.

        Parameters
        ----------
        hero_id : int, optional
            Matches containing this hero. A list of hero IDs can be fetched via the :any:`get_heroes()` method
        hero : Hero, optional
            Used in place of hero_id
        game_mode : int, optional
            Games of this game mode are fetched
        skill : int, optional
            Skill bracket for the matches (Ignored if an account ID is specified)
        min_players : int, optional
            Minimum amount of players in a match for the match to be returned.
        account_id : int, optional
            32/64-bit account ID
        steam_account : SteamAccount, optional
            Used in place of account_id
        league_id : int, optional
            Only return matches from this league. get_league_listing() has been discontinued
        start_at_match_id : int, optional
            Start searching for matches equal to or older than this match ID
        matches_requested : int, optional
            Defaults to `100`
        tournament_games_only : int, optional
            0 = False, 1 = True

        Returns
        -------
        MatchHistory
            Information of matches.
        """
        _parse_steam_account(kwargs)
        _parse_hero(kwargs)
        return self._api_call(endpoints.GET_MATCH_HISTORY, wrappers.MatchHistory, **kwargs)

    def get_match_history_by_sequence_num(self, **kwargs):
        """Get a list of matches ordered by sequence number.
        Uses a parser similar to that of :any:`get_match_history()` method

        Parameters
        ----------
        start_at_match_seq_num : int
            The match sequence number to start returning results from
        matches_requested : int, optional
            Defaults to `100`

        Returns
        -------
        MatchHistory
            Information of matches.
        """
        return self._api_call(endpoints.GET_MATCH_HISTORY_BY_SEQ_NUM, wrappers.MatchHistory, **kwargs)

    def get_match_details(self, match_id, **kwargs):
        """Get detailed information about a particular match.

        Parameters
        ----------
        match_id : int, string
            Match ID

        Returns
        -------
        MatchDetails
            Details of a match.
        """
        kwargs['match_id'] = match_id
        return self._api_call(endpoints.GET_MATCH_DETAILS, wrappers.MatchDetails, **kwargs)

    def get_heroes(self, **kwargs):
        """Get a list of heroes in Dota 2.

        Parameters
        ----------
        language : string, optional
            The `language <https://partner.steamgames.com/doc/store/localization#supported_languages>`_ to provide hero names in
        itemizedonly : bool, optional
            Return a list of itemized heroes only

        Returns
        -------
        Heroes
            Hero information.
        """
        return self._api_call(endpoints.GET_HEROES, wrappers.Heroes, **kwargs)

    def get_game_items(self, **kwargs):
        """Get a list of items in Dota 2.

        Parameters
        ----------
        language : string, optional
            The `language <https://partner.steamgames.com/doc/store/localization#supported_languages>`_ to provide hero names in

        Returns
        -------
        GameItems
            Item information.
        """
        return self._api_call(endpoints.GET_GAME_ITEMS, wrappers.GameItems, **kwargs)

    def get_tournament_prize_pool(self, **kwargs):
        """Get the current prizepool of specific tournaments.

        Parameters
        ----------
        leagueid : int
            The ID of the league to get the prize pool of

        Return
        ------
        TournamentPrizePool
            Prizepool of a tournament.
        """
        return self._api_call(endpoints.GET_TOURNAMENT_PRIZE_POOL, wrappers.TournamentPrizePool, **kwargs)

    def get_top_live_game(self, partner = 0, **kwargs):
        """Get details of on-going live games.

        Parameters
        ----------
        partner : int, optional
            Which partner's games to use (default `0`)

        Returns
        -------
        TopLiveGame
            Details of on-going live games.
        """
        kwargs['partner'] = partner
        return self._api_call(endpoints.GET_TOP_LIVE_GAME, wrappers.TopLiveGame, **kwargs)

    def get_team_info_by_team_id(self, **kwargs):
        """Get a list of teams' information.

        Parameters
        ----------
        start_at_team_id : int, optional
            The team id to start returning results from
        teams_requested : int, optional
            The amount of teams to return

        Returns
        -------
        TeamInfoByTeamID
            A list of teams' information.
        """
        return self._api_call(endpoints.GET_TEAM_INFO_BY_TEAM_ID, wrappers.TeamInfoByTeamID, **kwargs)

    def get_live_league_games(self, **kwargs):
        """Get a list of in-progress league matches, as well as their details at the time of query.

        Returns
        -------
        LiveLeagueGames
            Details of in-progress live league games.
        """
        return self._api_call(endpoints.GET_LIVE_LEAGUE_GAMES, wrappers.LiveLeagueGames, **kwargs)

    def get_broadcaster_info(self, **kwargs):
        """Get the broadcasting status of a user.

        Parameters
        ----------
        account_id : int
            32/64-bit account ID
        steam_account : SteamAccount
            Used in place of account_id

        Returns
        -------
        BroadcasterInfo
            Broadcasting information of a user.
        """
        _parse_steam_account(kwargs)
        kwargs['broadcaster_steam_id'] = kwargs.pop('account_id')
        return self._api_call(endpoints.GET_BROADCASTER_INFO, wrappers.BroadcasterInfo, **kwargs)

    def get_player_summaries(self, **kwargs):
        """Get Steam details of users.

        Parameters
        ----------
        account_ids : list(int)
            32/64-bit account ID
        steam_accounts : list(SteamAccount)
            Used in place of account IDs

        Returns
        -------
        PlayerSummaries
            Information of steam accounts
        """
        _parse_steam_account_list(kwargs)
        return self._api_call(endpoints.GET_PLAYER_SUMMARIES, wrappers.PlayerSummaries, **kwargs)


def update_local_data(purge = True):
    """Synchronize local data with current repository data

    Parameters
    ----------
    purge : bool
        Set to ``True`` to delete local content
    """
    return entities._update(purge)
