from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login')
def login():
    return "Login Page"  

@app.route('/signup')
def signup():
    return "Sign Up Page" 

if __name__ == '__main__':
    app.run(debug=True)
