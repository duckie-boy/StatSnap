from flask import Flask, render_template

app = Flask(__name__)

# Sample leaderboard data for Apex Legends
apex_leaderboard = [
    {"player_name": "Hal", "rank": "Pred38", "score": "1500 RP"},
    {"player_name": "Timmy", "rank": "Pred100", "score": "12300 RP"},
    {"player_name": "Aceu", "rank": "Pred150", "score": "11200 RP"},
]

@app.route("/")
def home():
    """Render the home page."""
    return render_template("home.html")

@app.route("/apexlegends")
def apex_legends():
    """Render the Apex Legends leaderboard."""
    return render_template("apexlegends.html", leaderboard=apex_leaderboard)

@app.route("/findgame")
def find_game():
    """Render the Find Game page."""
    
    return render_template("findgame.html")

if __name__ == "__main__":
    app.run(debug=True)
