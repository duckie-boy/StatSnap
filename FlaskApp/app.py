from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Simulated user profile data (In a real-world application, use a database)
user_profile = {
    "username": "Player123",
    "email": "player123@example.com",
    "bio": "Loves playing games and streaming!",
    "top_games": ["Valorant", "Fortnite", "Rocket League"]
}

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
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        # Get data from the form and update the user profile
        user_profile['username'] = request.form.get('name')
        user_profile['email'] = request.form.get('email')
        user_profile['bio'] = request.form.get('bio')
        user_profile['top_games'] = [
            request.form.get('game1'),
            request.form.get('game2'),
            request.form.get('game3')
        ]

        # Redirect to the profile page after saving changes
        return redirect(url_for('profile'))

    # Render the profile template with current user data
    return render_template('profile.html', user=user_profile)

if __name__ == '__main__':
    app.run(debug=True)
