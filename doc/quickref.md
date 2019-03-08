# Quick Reference
Below, is the generic dictionary access structure for any of the given endpoints.

## get_match_history()

    {
        list(matches): {
            dire_team_id,
            lobby_type,
            match_id,
            match_seq_num,
            list(players): {
                hero: {hero_id, hero_name},
                side,
                steam_account: {id32, id64}
            },
            radiant_team_id,
            start_time
        },
        num_results,
        results_remaining,
        status,
        total_results
    }
    

## get_match_details()

    {
        cluster,
        dire_buildings: {
            barracks_status,
            bot_ancient,
            bot_melee,
            bot_ranged,
            bot_t1,
            bot_t2,
            bot_t3,
            mid_melee,
            mid_ranged,
            mid_t1,
            mid_t2,
            mid_t3,
            top_ancient,
            top_melee,
            top_ranged,
            top_t1,
            top_t2,
            top_t3,
            tower_status
        },
        dire_score,
        duration,
        engine,
        first_blood_time,
        flags,
        game_mode,
        human_players,
        leagueid,
        lobby_type,
        match_id,
        match_seq_num,
        negative_votes,
        list(picks_bans): {
            hero: {hero_id, hero_name},
            is_pick,
            order,
            side
        },
        list(players): {
            ability_upgrades,
            list(additional_units): {
                list(backpack): {
                    item_aliases,
                    item_cost,
                    item_id,
                    item_name
                },
                list(inventory): {
                    list(item_aliases),
                    item_cost,
                    item_id,
                    item_name
                },
                unitname
            },
            assists,
            list(backpack): {
                list(item_aliases),
                item_cost,
                item_id,
                item_name
            },
            deaths,
            denies,
            gold_per_min,
            hero: {hero_id, hero_name},
            list(inventory): {
                list(item_aliases),
                item_cost,
                item_id,
                item_name
            },
            kills,
            last_hits,
            leaver_status,
            level,
            side,
            steam_account: {id32, id64},
            xp_per_min
        },
        list(players_minimal): {
            hero: {hero_id, hero_name},
            side,
            steam_account: {id32, id64}
        },
        positive_votes,
        pre_game_duration,
        radiant_buildings: {
            barracks_status,
            bot_ancient,
            bot_melee,
            bot_ranged,
            bot_t1,
            bot_t2,
            bot_t3,
            mid_melee,
            mid_ranged,
            mid_t1,
            mid_t2,
            mid_t3,
            top_ancient,
            top_melee,
            top_ranged,
            top_t1,
            top_t2,
            top_t3,
            tower_status
        },
        radiant_score,
        start_time,
        winner
    }
    

## get_heroes()

    {
        count,
        list(heroes): {
            id,
            localized_name,
            name
        },
        status
    }
    

## get_game_items()

    {
        list(game_items): {
            cost,
            id,
            localized_name,
            name,
            recipe,
            secret_shop,
            side_shop
        },
        status
    }
    

## get_tournament_prize_pool()

    {
        league_id,
        prize_pool,
        status
    }
    

## get_top_live_game()

    {
        list(game_list): {
            activate_time,
            average_mmr,
            deactivate_time,
            delay,
            dire_score,
            dire_team: {dire_id, dire_name},
            dire_towers: {
                bot_ancient,
                bot_t1,
                bot_t2,
                bot_t3,
                mid_t1,
                mid_t2,
                mid_t3,
                top_ancient,
                top_t1,
                top_t2,
                top_t3,
                tower_status
            },
            game_mode,
            game_time,
            last_update_time,
            league_id,
            lobby_id,
            lobby_type,
            match_id,
            list(players): {
                hero: {hero_id, hero_name},
                steam_account: {id32, id64}
            },
            radiant_lead,
            radiant_score,
            radiant_team: {team_id, team_name},
            radiant_towers: {
                bot_ancient,
                bot_t1,
                bot_t2,
                bot_t3,
                mid_t1,
                mid_t2,
                mid_t3,
                top_ancient,
                top_t1,
                top_t2,
                top_t3,
                tower_status
            },
            series_id,
            server_steam_id,
            sort_score,
            spectators
        }
    }
    

## get_team_info_by_team_id()

    {
        status,
        list(teams): {
            admin_account_id,
            calibration_games_remaining,
            country_code,
            games_played,
            logo,
            logo_sponsor,
            name,
            player_0_account_id,
            player_1_account_id,
            player_2_account_id,
            player_3_account_id,
            player_4_account_id,
            player_5_account_id,
            tag,
            time_created,
            url
        }
    }
    

## get_live_league_games()

    {games, status}
    

## get_broadcaster_info()

    {
        live,
        server_steam_id,
        steam_account: {id32, id64}
    }
    

## get_player_summaries()

    {
        list(players): {
            avatar,
            avatarfull,
            avatarmedium,
            communityvisibility,
            lastlogoff,
            personaname,
            personastate,
            personastateflags,
            primaryclanid,
            profilestate,
            profileurl,
            realname,
            steam_account: {id32, id64},
            steamid,
            timecreated
        }
    }
    
