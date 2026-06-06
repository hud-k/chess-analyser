import streamlit as st
import requests

username = st.text_input("Enter Chess.com username:")

if username:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(f"https://api.chess.com/pub/player/{username}/games/archives", headers=headers)
    st.write(response.status_code)

    if response.status_code == 200:
        gameData = response.json()
        st.write(gameData)
    else:
        st.write(f"Error {response.status_code}: Failed to retrieve game data for {username}")