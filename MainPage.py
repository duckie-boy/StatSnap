import os

import pytz
from supabase import create_client
from dotenv import load_dotenv
from fasthtml.common import *


#Load environment variables
load_dotenv()


#Initialize Supabase client
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))


app,rt = fast_app()


def signup(username, password):
    # Check if the username already exists
    usernameresponse = supabase.table("StatSnap_Login").select("*").eq("username", username).execute()


    if usernameresponse.data:  # If data is returned, the username exists
        return False  # Username already taken


    supabase.table("StatSnap_Login").insert(
        {"username": username, "password": password,}
    ).execute()
    return True  # Sign up successful




def get_messages():
    # Sort by 'id' in ascending order to get the first entered entries first
    response = supabase.table("StatSnap_Login").select("*").order("id", desc=False).execute()
    return response.data
""""
def render_message(entry):
    return (
        Article(
            Header(f"Username: {entry['username']}"),
            P(entry["password"]),
        ),
    )


def render_message_list():
    messages = get_messages()


    return Div(
        *[render_message(entry) for entry in messages],
        id="signup-list",
    )
"""




def logo_placement():
    # Image for the logo
    image = Img(
        src="/static/images/StatSnap_Logo2.png",  # Path to the image
        alt="Logo",
        width="120",  # Optional width
        height="auto",  # Optional height
        style="object-fit: cover; width: 100px; height: 100px;",  # Crops and resizes the image
    )


    return Div(
        image
    )






def render_content():
    form = Form(
        Fieldset(
            Input(
                type="text",
                name="username",
                placeholder="Username",
                required=True,
                maxlength=16,
            ),
            Input(
                type="password",
                name="password",
                placeholder="Password",
                required=True,
                maxlength=25,
            ),
            Button("Submit", type="submit"),
        ),
        method="post",
        hx_post="/submit-signup",
        #hx_target="#signup-list",
        hx_swap="outerHTML",
        hx_on_after_request="this.reset()",
    )


    return Div(
        form,
        #render_message_list(),
    )


def login(username, password):
    # Check if the username exists
    user_response = supabase.table("StatSnap_Login").select("*").eq("username", username).execute()
   
    if not user_response.data:
        return False, "Username does not exist."  # Return error if username is not found


    # Check if the password is correct
    user = user_response.data[0]
    if user["password"] == password:
        return True, None  # Password matches, return success
    else:
        return False, "Incorrect password."  # Password does not match
   
def render_login_form(error: str = None):
    error_message = ""
    if error:
        error_message = P(f"Error: {error}", style="color: red; font-weight: bold;")  # Display error message
    form = Form(
        Fieldset(
            Input(
                type="text",
                name="username",
                placeholder="Username",
                required=True,
                maxlength=16,
            ),
            Input(
                type="password",
                name="password",
                placeholder="Password",
                required=True,
                maxlength=25,
            ),
            Button("Log In", type="submit"),
        ),
        method="post",
        hx_post="/submit-login",
        hx_target="#login-container",  # Target the entire login container for swap
        hx_swap="outerHTML",
        hx_on_after_request="this.reset()",
    )


    return Div(
        error_message,  # Include the error message
        form,
        id="login-container"  # The target for swapping the content
    )


@rt('/signup', methods=["GET"])
def get(error: str = None):  # Accept the optional error parameter
    error_message = ""
    if error:
        error_message = P(f"Error: {error}", style="color: red; font-weight: bold;")  # Display error message
   
    return Titled(
        "SIGN UP✍️",
        Hr(),
        P('Welcome to the Sign Up Page!'),
        error_message,  # Include the error message, if any
        render_content(),
        A("Go back to home", href="/")
    )


@rt('/login', methods=["GET"])
def get(error: str = None):
    error_message = ""
    if error:
        error_message = P(f"Error: {error}", style="color: red; font-weight: bold;")
   
    return Titled(
        "LOG IN📝",
        Hr(),
        P('Log In to StatSnap!'),
        error_message,
        render_login_form(error),
        A("Go back to home", href="/")
    )


@rt('/')
def get():
    return Titled(
        Div(
            logo_placement(),  # Image on one side
            Div(P("Welcome to StatSnap!")),  # Text on the other side
            style="display: flex; align-items: center;",  # Flexbox styling to align side-by-side
        ),
        Div(
            P(A("Sign Up", href="/signup", style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; margin-right: 10px;")),  # Stylish Sign Up button
            P(A("Log In", href="/login", style="padding: 10px 20px; background-color: #008CBA; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;")),  # Stylish Log In button
            style="display: flex; justify-content: ; gap: 10px; margin-top: 20px;"  # Center the buttons and add spacing
        )


    )
   


@rt("/submit-signup", methods=["POST"])
def post(username: str, password: str):
   if signup(username, password):  # If signup is successful (no duplicate username)
       #render_message_list()
       return Redirect("/profile")  # Redirect to the profile page after successful sign-up
   #signup(username, password)
   else:
        # Redirect back to signup page with an error message as a query parameter
        return Redirect(f"/signup?error=Username '{username}' is already taken.")
   


@rt("/submit-login", methods=["POST"])
def post(username: str, password: str):
    success, error = login(username, password)
   
    if success:
        return Redirect("/home")  # Redirect to profile page
    else:
        # Re-render the form with the error message
        return render_login_form(error)
   
@rt('/profile', methods=["GET"])
def get():
    return Titled("SnapStat Profile Creation",Hr(), P('Set up your profile now!'), A("Sign Out", href="/"))


@rt('/home', methods=["GET"])
def get():
    return Titled("Welcome to the StatSnap Home Page",Hr(), P('Enter stats for any games!'), A("Sign Out", href="/"))


serve()

