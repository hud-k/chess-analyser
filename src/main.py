import streamlit as st
import requests
import datetime
from display import display_colour_stats, display_opening_stats, opening_bar_chart, performance_trends, display_blunder_insights
import chess
import chess.pgn
import io
import chess.engine

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

def blunder_detection(username, all_games):
    engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\Acer\Downloads\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe")
    ten_latest = all_games[-10:]
    blunder_count = 0
    white_blunders = 0
    black_blunders = 0
    blunder_moves = []
    bar = st.progress(0)
    for i, game in enumerate(ten_latest):
        bar.progress((i + 1) / 10, text="Analysing games with Stockfish...")
        game_obj = chess.pgn.read_game(io.StringIO(game["pgn"]))
        if game["white"]["username"].lower() == username.lower():
            sign = 1
        else:
            sign = -1
        prev_score = None
        for node in game_obj.mainline():
            info = engine.analyse(node.board(), chess.engine.Limit(depth=12))
            curr_score = info["score"].white().score()

            if prev_score is not None and curr_score is not None:
                score_swing = (curr_score - prev_score)*sign
            else:
                score_swing = 0
            if score_swing <= -300:
                blunder_count +=1
                blunder_moves.append(node.ply())
                if sign == 1:
                    white_blunders +=1
                else:
                    black_blunders +=1
            prev_score = curr_score
    engine.quit()
    return {"total blunders": blunder_count,
            "white blunders": white_blunders,
            "black blunders": black_blunders,
            "blunder moves": blunder_moves}

def blunder_stats(blunder_info):
    avrg_blunders = blunder_info["total blunders"]/10
    blunder_moves = blunder_info["blunder moves"]
    if len(blunder_moves) > 0:
        avrg_blunder_move = sum(blunder_moves)/len(blunder_moves)
    else:
        avrg_blunder_move = 0
    return {"average blunders": round(avrg_blunders, 1),
            "average blunder move": round(avrg_blunder_move / 2),
            "white blunders": blunder_info["white blunders"],
            "black blunders": blunder_info["black blunders"]}

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

    tab1, tab2, tab3, tab4 = st.tabs(["Colour Stats", "Openings", "Performance Trends", "Blunder Insights"])
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
    with tab4:
        b_stats = blunder_stats(blunder_detection(username, all_games))
        display_blunder_insights(b_stats)




    
        