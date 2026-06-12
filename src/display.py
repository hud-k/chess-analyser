import streamlit as st

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
    pass