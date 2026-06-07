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
    