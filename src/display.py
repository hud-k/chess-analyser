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
        'Wins': [openings[o]["wins"] for o in openings],
        "Losses": [openings[o]["losses"] for o in openings],
        "Draws": [openings[o]["draws"] for o in openings]
    })
    st.dataframe(df, hide_index=True)