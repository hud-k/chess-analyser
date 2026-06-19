# Chess Analyser
Chess.com game analyser built with Python and Streamlit. Takes in a player's Chess.com username and fetches their games from the last 12 months to display:

- Game statistics for both white and black
- Table of statistics for the openings played by the user
- Bar chart displaying their 10 best openings (calculated using win rate for each opening)
- Line chart showing their win rate progression by month.

## Screenshots

### Colour Stats
![Colour Stats](assets/Colour%20Stats.png)

### Opening Stats
![Opening Stats](assets/Opening%20Stats.png)

### Performance Trends
![Performance Trends](assets/Performance%20Trends.png)

## Live Demo
[View Live Demo](https://chess-analyser.streamlit.app/)

## Run Locally

1. Clone the repository
```
git clone https://github.com/hud-k/chess-analyser
```

2. Install dependencies
```
pip install -r requirements.txt
```

3. Run the app
```
streamlit run src/main.py
```

## Tech stack
- Python
- Streamlit
- Chess.com Public API
- Pandas