import streamlit as st
import pandas as pd

def display_colour_stats(stats):
    for colour in stats:
        st.subheader(f"Your stats as {colour.capitalize()}")
        w, l, d, wr = st.columns(4, border=True)
        w.metric(label="Wins", value=stats[colour]["wins"])
        l.metric(label="Losses", value=stats[colour]["losses"])
        d.metric(label="Draws", value=stats[colour]["draws"])
        win_rate = (stats[colour]["wins"]/stats[colour]["total"])*100
        wr.metric(label = "Win rate", value=(f"{round(win_rate, 1)}%"))

def display_opening_stats(openings):
    df = pd.DataFrame({
        'Opening': list(openings.keys()),
        'Wins': [o["wins"] for o in openings.values()],
        "Losses": [o["losses"] for o in openings.values()],
        "Draws": [o["draws"] for o in openings.values()],
        "Win rate %": [opening_win_rate(o) for o in openings.values()]
    })
    df.sort_values("Win rate %", ascending=False)
    st.dataframe(df, hide_index=True)
    return df

def opening_win_rate(o):
    total = o["wins"] + o["losses"] + o["draws"]
    win_rate = (o["wins"]/total)*100
    return round(win_rate, 1)

def opening_bar_chart(df):
    game_threshold = 3
    top_games = df[df['Wins'] + df['Losses'] + df['Draws'] >= game_threshold].head(10)
    st.bar_chart(top_games, x='Opening', y='Win rate %', sort="-Win rate %", horizontal=True, color="red")
