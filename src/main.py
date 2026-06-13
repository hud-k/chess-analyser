import streamlit as st
import requests
import re
from display import display_colour_stats, display_opening_stats

LOSS_STATES = {"checkmated", "resigned", "abandoned", "timeout"}

def get_result(username, game):
    if game["white"]["username"] == username:
        return game["white"]["result"]
    else:
        return game["black"]["result"]

def colour_stats(username, all_games):
    white_games_won = 0
    white_games_lost = 0
    white_total_games = 0

    black_games_won = 0
    black_games_lost = 0
    black_total_games = 0

    for game in all_games:
        if game["white"]["username"] == username:
            white_result = get_result(username, game)
            white_total_games+=1

            if white_result == "win":
                white_games_won+=1
            elif white_result in LOSS_STATES:
                white_games_lost+=1

        else:
            black_result = get_result(username, game)
            black_total_games+=1

            if black_result == "win":
                black_games_won+=1
            elif black_result in LOSS_STATES:
                black_games_lost+=1
    
    white_games_drawn = white_total_games - (white_games_won + white_games_lost)
    black_games_drawn = black_total_games - (black_games_won + black_games_lost)

    return {
        "white": {"wins": white_games_won, "losses": white_games_lost, "draws": white_games_drawn, "total": white_total_games},
        "black": {"wins": black_games_won, "losses": black_games_lost, "draws": black_games_drawn, "total": black_total_games}
    }

def extract_opening(game):
    opening_url = game.get("eco", None)
    if not opening_url:
        return "Unknown"
    opening = opening_url.rsplit("/", 1)[-1]
    opening = opening.replace("-", " ")
    return opening
    
def opening_stats(username, all_games):
    opening_dict = {}
    for game in all_games:
        opening = extract_opening(game)
        result = get_result(username, game)
        opening_dict.setdefault(opening, {"wins": 0, "losses": 0, "draws": 0})
        if result == "win":
            opening_dict[opening]["wins"]+=1
        elif result in LOSS_STATES:
            opening_dict[opening]["losses"]+=1
        else:
            opening_dict[opening]["draws"]+=1
    return opening_dict

username = st.text_input("Enter Chess.com username:")
timeframe = 12

if username:
    headers = {"User-Agent": "Mozilla/5.0"}
    archives_response = requests.get(f"https://api.chess.com/pub/player/{username}/games/archives", headers=headers)

    if archives_response.status_code == 200:
        archives = archives_response.json()['archives']
        recent_archives = archives[-12:]
    else:
        st.write(f"Error {archives_response.status_code}: Failed to retrieve game data for {username}")

    all_games = []

    for month in recent_archives:
        game_response = requests.get(month, headers=headers)
        games = game_response.json()['games']
        for game in games:
            if game["rated"] and game["rules"] == "chess":
                all_games.append(game)

    stats = colour_stats(username, all_games)
    openings = opening_stats(username, all_games)

    display_colour_stats(stats)
    display_opening_stats(openings)

    
            
