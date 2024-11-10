from flask import Flask, render_template

app = Flask(__name__)

# Landing Page Route
@app.route('/')
def landing():
    return render_template('landing.html')

# Login Page Route
@app.route('/login')
def login():
    return "Login Page"

# Sign Up Page Route
@app.route('/signup')
def signup():
    return "Sign Up Page"

# Profile Page Route
@app.route('/profile')
def profile():
    # Example user data passed to the template
    return render_template('profile.html', user={
        "username": "Player123",
        "email": "player123@example.com",
        "games_played": 25,
        "highest_score": 1900
    })

if __name__ == '__main__':
    app.run(debug=True)
