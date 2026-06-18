import streamlit as st
import requests
import datetime
from display import display_colour_stats, display_opening_stats, opening_bar_chart, performance_trends

LOSS_STATES = {"checkmated", "resigned", "abandoned", "timeout"}
st.set_page_config(layout="wide")

def get_result(username, game):
    if game["white"]["username"].lower() == username.lower():
        return game["white"]["result"]
    else:
        return game["black"]["result"]

def monthly_win_rate(username, monthly_games, monthly_stats):
    total_wins = 0
    if len(monthly_games) > 0:
        unix_time = monthly_games[0]["end_time"]  
        month = str(datetime.date.fromtimestamp(unix_time))
        for game in monthly_games:
            result = get_result(username, game)
            if result == "win":
                total_wins+=1
        monthly_stats.setdefault(month, {"win_rate": 0})
        monthly_stats[month]["win_rate"] = round((total_wins/len(monthly_games))*100, 1)
      
def colour_stats(username, all_games):
    white_games_won = 0
    white_games_lost = 0
    white_total_games = 0

    black_games_won = 0
    black_games_lost = 0
    black_total_games = 0

    for game in all_games:
        if game["white"]["username"].lower() == username.lower():
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

@st.cache_data(show_spinner=False)
def fetch_games(username):
    headers = {"User-Agent": "Mozilla/5.0"}
    archives_response = requests.get(f"https://api.chess.com/pub/player/{username}/games/archives", headers=headers)

    if archives_response.status_code != 200:
        return None, None
    
    archives = archives_response.json()['archives']
    recent_archives = archives[-12:]

    all_games = []
    monthly_stats = {}

    for month in recent_archives:
        game_response = requests.get(month, headers=headers)
        games = game_response.json()['games']
        monthly_win_rate(username, games, monthly_stats)
        for game in games:
            if game["rated"] and game["rules"] == "chess":
                all_games.append(game)
    return all_games, monthly_stats

username = st.text_input("Enter Chess.com username:")
timeframe = 12

if username:
    with st.spinner("Fetching games..."):
        all_games, monthly_stats = fetch_games(username)

    if all_games is None:
        st.error(f"User '{username}' not found")
        st.stop()

    stats = colour_stats(username, all_games)
    openings = opening_stats(username, all_games)

    tab1, tab2, tab3 = st.tabs(["Colour Stats", "Openings", "Performance Trends"])
    with tab1:
        display_colour_stats(stats)
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            data_frame=display_opening_stats(openings)
        with col2:
            st.subheader("Your Best Openings", divider="red")
            opening_bar_chart(data_frame)
    with tab3:
        performance_trends(monthly_stats)
    
            
