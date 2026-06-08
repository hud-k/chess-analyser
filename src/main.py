import streamlit as st
import requests

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
            all_games.append(game)
    
    def calculate_stats(username, all_games):
        white_games_won = 0
        white_games_lost = 0
        white_total_games = 0

        black_games_won = 0
        black_games_lost = 0
        black_total_games = 0

        loss_states = {"checkmated", "resigned", "abandoned", "timeout"}
        for game in all_games:

            white_result = game["white"]["result"]
            black_result = game["black"]["result"]

            if game["white"]["username"] == username:
                white_total_games+=1
                if white_result == "win":
                    white_games_won+=1
                elif white_result in loss_states:
                    white_games_lost+=1

            else:
                black_total_games+=1
                if black_result == "win":
                    black_games_won+=1
                elif black_result in loss_states:
                    black_games_lost+=1
        
        white_games_drawn = white_total_games - (white_games_won + white_games_lost)
        black_games_drawn = black_total_games - (black_games_won + black_games_lost)

        return {
            "white": {"wins": white_games_won, "losses": white_games_lost, "draws": white_games_drawn},
            "black": {"wins": black_games_won, "losses": black_games_lost, "draws": black_games_drawn}
        }
    
    stats = calculate_stats(username, all_games)
    st.write(stats)