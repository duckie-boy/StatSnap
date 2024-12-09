import os
import bcrypt

#import pytz
from supabase import create_client
from dotenv import load_dotenv
from fasthtml.common import *
#from fasthtml import Div, Titled, Hr, A, P, H1
#from fasthtml.common import Request

#Load environment variables
load_dotenv()

#Initialize Supabase client
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

app,rt = fast_app(
    hdrs=(Link(rel="icon", type="assets/x-icon", href="/assets/favicon.png"),),
)

# Global variable to store the logged-in user ID
current_user_id = None
admin_current_user_id = None

#Function to place and style the logo image on the UI
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

#Function to define JavaScript code for a forgot password popup
def forgot_password_script():
    # JavaScript code as a string
    return Script("""
    function openForgotPasswordPopup() {
        const popup = document.createElement("div");
        popup.id = "reset-password-popup";
        popup.style.position = "fixed";
        popup.style.top = "50%";
        popup.style.left = "50%";
        popup.style.transform = "translate(-50%, -50%)";
        popup.style.background = "white";
        popup.style.padding = "20px";
        popup.style.borderRadius = "8px";
        popup.style.boxShadow = "0px 0px 10px rgba(0,0,0,0.2)";
        popup.innerHTML = `
            <h3>Reset Password</h3>
            <form id="forgot-password-form" method="post" action="/reset-password">
                <input type="text" name="username" placeholder="Username" required><br><br>
                <input type="password" name="new_password" placeholder="New Password" required><br><br>
                <input type="password" name="confirm_password" placeholder="Confirm Password" required><br><br>
                <button type="submit">Reset Password</button>
                <button type="button" onclick="closePopup()">Cancel</button>
            </form>
        `;
        document.body.appendChild(popup);
    }

    function closePopup() {
        // Find and remove the popup by its ID to ensure it only targets the popup element
        const popup = document.getElementById("reset-password-popup");
        if (popup) {
            popup.remove();
        }
    }
    """)

#Function to log the user out by clearing the current user ID
def logout():
    global current_user_id
    current_user_id = None
    return Redirect("/login")

#Function to log the admin user out by clearing the current admin user ID
def admin_logout():
    global admin_current_user_id
    admin_current_user_id = None
    return Redirect("/admin-login")

#Function to retrieve all messages (user data) in sorted order
def get_messages():
    # Sort by 'id' in ascending order to get the first entered entries first
    response = supabase.table("StatSnap_Login").select("*").order("id", desc=False).execute()
    return response.data

#Function to sign up a user if the username is unique
def signup(username, password):
    # Check if the username already exists
    usernameresponse = supabase.table("StatSnap_Login").select("*").eq("username", username).execute()

    if usernameresponse.data:  # If data is returned, the username exists
        return False  # Username already taken

    # Hash the password with bcrypt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    supabase.table("StatSnap_Login").insert(
        {"username": username, "password": hashed_password.decode('utf-8')}
    ).execute()
    return True  # Sign up successful

#Function to render the content for the sign-up form
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

#Function to log in a user, setting current_user_id on success
def login(username, password):
    global current_user_id  # Reference the global variable

    user_response = supabase.table("StatSnap_Login").select("*").eq("username", username).execute()

    if not user_response.data:
        return False, "Username does not exist."

    user = user_response.data[0]

    # Verify the hashed password
    if bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
        current_user_id = user["id"]  # Set the user ID in the global variable
        return True, None  # Login successful
    else:
        return False, "Incorrect password."

#Function to render the login form, with error/success message handling
def render_login_form(error: str = None, message: str = None):
    success_message = ""
    if message:
        success_message = P(message, style="color: green; font-weight: bold;")

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

    forgot_password = A("Forgot password?", href="#", style="color: blue;", onclick="openForgotPasswordPopup()")

    return Div(
        success_message,
        error_message,  # Include the error message
        form,
        forgot_password,
        forgot_password_script(),  # Include the JavaScript code for the popup here
        id="login-container"  # The target for swapping the content
    )

#Function to log in an admin, checking admin credentials
def admin_login(admin_username, admin_password):
    global admin_current_user_id

    # Check if the admin username exists
    response = supabase.table("StatSnap_Admin").select("*").eq("admin_username", admin_username).execute()
    if not response.data:
        return False, "Admin username does not exist."
    # Verify password
    admin = response.data[0]
    if bcrypt.checkpw(admin_password.encode('utf-8'), admin["admin_password"].encode('utf-8')):
        admin_current_user_id = admin["id"]
        return True, None  # Admin login successful
    return False, "Incorrect admin password."

#Function to render the admin login form, with error/success message handling
def render_admin_login_form(error: str = None, message: str = None):
    success_message = ""
    if message:
        success_message = P(message, style="color: green; font-weight: bold;")

    error_message = ""
    if error:
        error_message = P(f"Error: {error}", style="color: red; font-weight: bold;")  # Display error message

    form = Form(
        Fieldset(
            Input(
                type="text",
                name="admin_username",
                placeholder="Admin Username",
                required=True,
                maxlength=16,
            ),
            Input(
                type="password",
                name="admin_password",
                placeholder="Admin Password",
                required=True,
                maxlength=25,
            ),
            Button("Admin Log In", type="submit"),
        ),
        method="post",
        hx_post="/submit-admin-login",
        hx_target="#admin-login-container",  # Target the entire login container for swapping content
        hx_swap="outerHTML",
        hx_on_after_request="this.reset()",
    )

    forgot_password = A("Forgot password?", href="#", style="color: blue;", onclick="openForgotPasswordPopup()")

    return Div(
        success_message,
        error_message,  # Include the error message if any
        form,
        forgot_password,
        forgot_password_script(),  # Include the JavaScript code for the popup here
        id="admin-login-container"  # Target ID for HTMX content replacement
    )

def render_admin_user_list():
    users = supabase.table("StatSnap_Login").select("*").execute().data

    return Div(
        *[
            Div(
                Div(
                    Span(f"User: {user['username']}"),
                    Form(
                        Input(type="hidden", name="user_id", value=user["id"]),
                        Button(
                            "Remove User",
                            type="submit",
                            hx_post="/remove-user",
                            hx_target=f"#user-{user['id']}",  # Target this user's container
                            hx_confirm=f"Are you sure you want to remove user '{user['username']}'?",
                        ),
                        method="post",
                        style="margin-bottom: 10px;",
                    ),
                    id=f"user-{user['id']}",  # Unique ID for the user's container
                    style="margin-bottom: 10px; border-bottom: 1px solid #ccc; padding: 10px;"
                )
            ) for user in users
        ],
        id="admin-user-list"
    )


#JavaScript function for handling friend requests
def add_friend_script():
    return Script(f"""

    async function addFriend(friendId, button) {{
        const {{ data, error }} = await supabase
            .from("FriendRequests")
            .insert([{{ sender_id: {current_user_id}, receiver_id: friendId, status: 'pending' }}]);
       
        if (error) {{
            alert("Error sending friend request: " + error.message);
        }} else {{
            button.innerText = "Friend Request Sent";
            button.disabled = true;
        }}
    }}
    """)

#Function to initialize the Supabase client in JavaScript for the user
def js_supabase_client(current_user_id):
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    return Div(
        Script(src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@1.24.1/dist/umd/supabase.min.js"),
        Script(f"""
        document.addEventListener('DOMContentLoaded', function() {{
            if (typeof window.supabase === 'undefined') {{
                window.supabase = window.supabase.createClient('{supabase_url}', '{supabase_key}');
                console.log("Supabase client initialized.");
            }}

            const currentUserId = '{current_user_id}';

            // Define addFriend function
            async function addFriend(receiverId, button) {{
                console.log("Button clicked for friendId:", friendId);  // Debugging log

                // Send a POST request to the /add-friend route
                const response = await fetch('/add-friend', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{ receiver_id: receiverId }})
                }});

                const result = await response.json();

                if (result.success) {{
                    console.log("Friend request successfully sent for friendId:", friendId);  // Debugging log
                    button.innerText = "Friend Request Sent";
                    button.disabled = true;  // Disable the button after sending the request
                    button.style.backgroundColor = "#333";
                }} else {{
                    alert(result.message);  // Show the error message if the request fails
                }}
            }}

            // Expose addFriend function globally
            window.addFriend = addFriend;
        }});
        """)
    )

#Function to fetch sent and received friend requests for the user
def get_friend_requests(current_user_id):
    # Fetch friend requests sent by the current user
    sent_requests_response = supabase.table("FriendRequests").select("*").eq("sender_id", current_user_id).execute()
    print("Sent Requests Response:", sent_requests_response)  # Debug statement
    sent_requests = sent_requests_response.data

    # Fetch friend requests received by the current user
    received_requests_response = supabase.table("FriendRequests").select("*").eq("receiver_id", current_user_id).execute()
    print("Received Requests Response:", received_requests_response)  # Debug statement
    received_requests = received_requests_response.data

    return sent_requests, received_requests

#JavaScript function to accept a friend request
def accept_friend_script():
    return Script("""
    async function acceptFriend(userId, button) {
        const { data, error } = await supabase
            .from("FriendRequests")
            .update({ status: 'accepted' })
            .match({ sender_id: userId, receiver_id: currentUserId });

        if (error) {
            alert("Error accepting friend request: " + error.message);
        } else {
            button.innerText = "Current Friend";  // Update button text
            button.disabled = true;               // Disable the button
            button.style.backgroundColor = "#333"; // Optionally, change button style to indicate non-clickable
        }
    }
    """)

#Function to process friend requests, categorizing them by status
def process_friend_requests(current_user_id):
    sent_requests, received_requests = get_friend_requests(current_user_id)

    # Create a dictionary to map friend request statuses
    friend_status = {}

    # Process sent requests
    for request in sent_requests:
        if request['status'] == 'accepted':
            friend_status[request['receiver_id']] = 'accepted'
        else:
            friend_status[request['receiver_id']] = 'sent'

    # Process received requests
    for request in received_requests:
        if request['status'] == 'accepted':
            friend_status[request['sender_id']] = 'accepted'
        else:
            friend_status[request['sender_id']] = 'received'

    return friend_status

#Function to get other users excluding the current user
def get_other_users(current_user_id):
    response = supabase.table("StatSnap_Login").select("*").neq("id", current_user_id).execute()
    return response.data

#Function to render a list of other users with friend request actions
def render_user_list(current_user_id):
    users = get_other_users(current_user_id)
    friend_status = process_friend_requests(current_user_id)

    return Div(
        *[
            Div(
                Span(f"{user['username']}"),
                Form(
                    Input(type="hidden", name="friend_id", value=user['id']),  # Explicitly add hidden input for friend_id
                    Button(
                        "Friend Request Sent" if friend_status.get(user['id']) == 'sent'
                        else "Accept Friend Request" if friend_status.get(user['id']) == 'received'
                        else "Current Friend" if friend_status.get(user['id']) == 'accepted'
                        else "Add Friend",
                        type="button",
                        hx_post="/friend-action",  # Send POST request to /friend-action route
                        hx_target="this",  # Target this button for swap
                        hx_trigger="click",  # Trigger the request on click
                        hx_include="[name=friend_id]",  # Include friend_id hidden input in the request
                        disabled=friend_status.get(user['id']) in ['sent', 'accepted'],
                    ),
                    #action="/friend-action",  # Submits form to the '/add-friend' route
                    #method="post",
                    #hidden_inputs={"friend_id": user['id']}  # Send friend_id as hidden input
                ),
                style="margin-bottom: 10px;"
            ) for user in users if user['id'] != current_user_id
        ],
        id="user-list"
    )

#Function to retrieve IDs of current friends of the user
def get_current_friends(current_user_id):
    # Fetch records where the user is the sender
    sent_requests = supabase.table("FriendRequests").select("receiver_id").eq("sender_id", current_user_id).eq("status", "accepted").execute().data
    # Fetch records where the user is the receiver
    received_requests = supabase.table("FriendRequests").select("sender_id").eq("receiver_id", current_user_id).eq("status", "accepted").execute().data
    
    # Extract friend IDs
    friends = [req["receiver_id"] for req in sent_requests] + [req["sender_id"] for req in received_requests]
    return friends

#Function to render the group creation form for the current user's friends
def render_group_creation_form(current_user_id):
    friends = get_current_friends(current_user_id)
    friend_usernames = [
        supabase.table("StatSnap_Login").select("username").eq("id", friend_id).execute().data[0]["username"]
        for friend_id in friends
    ]
    return Form(
        Div(
            Label("Group Name:"),
            Input(type="text", name="group_name", required=True, placeholder="Enter group name"),
            style="margin-bottom: 10px;"
        ),
        *[
            Div(
                Input(type="checkbox", name="friend_ids[]", value=friend_id),
                Span(username),
                style="margin-bottom: 10px;"
            ) for friend_id, username in zip(friends, friend_usernames)
        ],
        Button("Create Group", type="submit"),
        action="/create-group",
        method="post"
    )

#Function to get games from Supabase 'Games' table
def get_games():
    response = supabase.table("Games").select("*").execute()
    return response.data

#Function to get games from Supabase 'Games' table
def render_nav_bar(current_page):
    games = get_games()
    return Div(
        A(
            "Home",
            href="/home",
            style={
                "color": "red" if current_page == "home" else "white",
                "margin-right": "10px",
                "text-decoration": "none",
                "font-size": "14px",
            },
        ),
        *[
            A(
                game["name"],
                href=game["link"],
                style={
                    "color": "white",
                    "margin-right": "10px",
                    "text-decoration": "none",
                },
            )
            for game in games
        ],
        A(
            "Find Game",
            href="/find-game",
            style={
                "color": "red" if current_page == "find-game" else "white",
                "margin-right": "10px",
                "text-decoration": "none",
                "font-size": "14px",
            },
        ),
        style={"background-color": "blue", "padding": "10px"},
    )

#Function to render the game stats form for Apex Legends
def Apex_render_content():
    form = Form(
        Fieldset(
            Input(
                type = "date",
                name = "date",
                required = True
            ),
            Fieldset(
                Legend("Did you win?"),
                Input(
                    type = "radio",
                    id = "yes",
                    name = "win-loss"
                ),
                Label("Yes"),
                Input(
                    type = "radio",
                    id = "no",
                    name = "win-loss"
                ),
                Label("No"),
            ),
            Input(
                type = "text",
                name = "map",
                placeholder = "Map",
                required = True
            ),
            Input(
                type = "text",
                name = "squadSize",
                placeholder = "Squad Size",
                required = True
            ),
            Input(
                type = "number",
                name = "palcement",
                placeholder = "Placement",
                required = True
            ),
            Input(
                type = "number",
                name = "kills",
                placeholder = "Kills",
                required = True
            ),
            Input(
                type = "number",
                name = "deaths",
                placeholder = "Deaths",
                required = True
            ),
            Input(
                type = "number",
                name = "damage",
                placeholder = "Damage"
            ),
            Button("Submit", type = "submit")
        )
    )
    return Div(
        form
    )

#Function to render the game stats form for Fortnite
def Fortnite_render_content():
        form = Form(
            Fieldset(
                Input(
                    type = "date",
                    name = "date",
                    required = True
                ),
                Fieldset(
                    Legend("Did you win?"),
                    Input(
                        type = "radio",
                        id = "yes",
                        name = "win-loss"
                    ),
                    Label("Yes"),
                    Input(
                        type = "radio",
                        id = "no",
                        name = "win-loss"
                    ),
                    Label("No"),
                ),
                Input(
                    type = "text",
                    name = "squadSize",
                    placeholder = "Squad Size",
                    required = True
                ),
                Input(
                    type = "number",
                    name = "palcement",
                    placeholder = "Placement",
                    required = True
                ),
                Input(
                    type = "number",
                    name = "kills",
                    placeholder = "Kills",
                    required = True
                ),
                Input(
                    type = "number",
                    name = "deaths",
                    placeholder = "Deaths",
                    required = True
                ),
                Input(
                    type = "number",
                    name = "revives",
                    placeholder = "Revives",
                    required = True
                ),
                Button("Submit", type = "submit")
            )
        )
        return Div(
            form
        )

#Function to render the game stats form for COD: BO6
def COD_render_content():
    form = Form(
        Fieldset(
            Input(
                type = "date",
                name = "date",
                required = True
            ),
            Fieldset(
                Legend("Did you win?"),
                Input(
                    type = "radio",
                    id = "yes",
                    name = "win-loss"
                ),
                Label("Yes"),
                Input(
                    type = "radio",
                    id = "no",
                    name = "win-loss"
                ),
                Label("No"),
            ),
            Input(
                type = "text",
                name = "map",
                placeholder = "Map",
                required = True
            ),
            Input(
                type = "text",
                name = "gamemode",
                placeholder = "Game Mode",
                required = True
            ),
            Input(
                type = "number",
                name = "kills",
                placeholder = "Kills",
                required = True
            ),
            Input(
                type = "number",
                name = "deaths",
                placeholder = "Deaths",
                required = True
            ),
            Input(
                type = "number",
                name = "score",
                placeholder = "Score",
                required = True
            ),
            Input(
                type = "number",
                name = "assists",
                placeholder = "Assists"
            ),
            Button("Submit", type = "submit")
        )
    )
    return Div(
        form
    )

#Function to render the game stats form for Warzone
def Warzone_render_content():
    form = Form(
        Fieldset(
            Input(
                type = "date",
                name = "date",
                required = True
            ),
            Fieldset(
                Legend("Did you win?"),
                Input(
                    type = "radio",
                    id = "yes",
                    name = "win-loss"
                ),
                Label("Yes"),
                Input(
                    type = "radio",
                    id = "no",
                    name = "win-loss"
                ),
                Label("No"),
            ),
            Input(
                type = "text",
                name = "map",
                placeholder = "Map",
                required = True
            ),
            Input(
                type = "text",
                name = "squadSize",
                placeholder = "Squad Size",
                required = True
            ),
            Input(
                type = "number",
                name = "palcement",
                placeholder = "Placement",
                required = True
            ),
            Input(
                type = "number",
                name = "kills",
                placeholder = "Kills",
                required = True
            ),
            Input(
                type = "number",
                name = "deaths",
                placeholder = "Deaths",
                required = True
            ),
            Input(
                type = "number",
                name = "revives",
                placeholder = "Revives",
                required = True
            ),
            Button("Submit", type = "submit")
        )
    )
    return Div(
        form
    )

#Function to render the game stats form for Rocket League
def RocketLeague_render_content():
    form = Form(
        Fieldset(
            Input(
                type = "date",
                name = "date",
                required = True
            ),
            Fieldset(
                Legend("Did you win?"),
                Input(
                    type = "radio",
                    id = "yes",
                    name = "win-loss"
                ),
                Label("Yes"),
                Input(
                    type = "radio",
                    id = "no",
                    name = "win-loss"
                ),
                Label("No"),
            ),
            Input(
                type = "text",
                name = "map",
                placeholder = "Map",
                required = True
            ),
            Input(
                type = "text",
                name = "gamemode",
                placeholder = "Game Mode",
                required = True
            ),
            Input(
                type = "number",
                name = "goals",
                placeholder = "Goals",
                required = True
            ),
            Input(
                type = "number",
                name = "assists",
                placeholder = "Assists"
            ),
            Button("Submit", type = "submit")
        )
    )
    return Div(
        form
    )

#Function to render the game stats form for Minecraft
def Minecraft_render_content():
    form = Form(
        Fieldset(
            Input(
                type = "date",
                name = "date",
                required = True
            ),
            Input(
                type = "text",
                name = "Category",
                placeholder = "Category",
                required = True
            ),
            Input(
                type = "number",
                name = "time",
                placeholder = "Time",
                required = True
            ),
            Fieldset(
                Legend("Seeded?"),
                Input(
                    type = "radio",
                    id = "yes",
                    name = "win-loss"
                ),
                Label("Yes"),
                Input(
                    type = "radio",
                    id = "no",
                    name = "win-loss"
                ),
                Label("No"),
            ),
            Button("Submit", type = "submit")
        )
    )
    return Div(
        form
    )

#Function to render the game stats form for Valorant
def Valorant_render_content():
    form = Form(
        Fieldset(
            Input(
                type = "date",
                name = "date",
                required = True
            ),
            Fieldset(
                Legend("Did you win?"),
                Input(
                    type = "radio",
                    id = "yes",
                    name = "win-loss"
                ),
                Label("Yes"),
                Input(
                    type = "radio",
                    id = "no",
                    name = "win-loss"
                ),
                Label("No"),
            ),
            Input(
                type = "text",
                name = "agent",
                placeholder = "Agent",
                required = True
            ),
            Input(
                type = "text",
                name = "map",
                placeholder = "Map",
                required = True
            ),
            Input(
                type = "number",
                name = "squadSize",
                placeholder = "Squad Size",
                required = True
            ),
            Input(
                type = "number",
                name = "palcement",
                placeholder = "Placement",
                required = True
            ),
            Input(
                type = "number",
                name = "kills",
                placeholder = "Kills",
                required = True
            ),
            Input(
                type = "number",
                name = "deaths",
                placeholder = "Deaths",
                required = True
            ),
            Input(
                type = "number",
                name = "revives",
                placeholder = "Revives",
                required = True
            ),
            Button("Submit", type = "submit")
        )
    )
    return Div(
        form
    )

#Function to render the game stats form for Dota 2 --> HAS NOT BEEN DONE!!
def Dota2_render_content():
    form = Form(
        Fieldset(
            Input(
                type = "date",
                name = "date",
                required = True
            ),
            Input(
                type = "text",
                name = "Category",
                placeholder = "Category",
                required = True
            ),
            Input(
                type = "number",
                name = "time",
                placeholder = "Time",
                required = True
            ),
            Fieldset(
                Legend("Seeded?"),
                Input(
                    type = "radio",
                    id = "yes",
                    name = "win-loss"
                ),
                Label("Yes"),
                Input(
                    type = "radio",
                    id = "no",
                    name = "win-loss"
                ),
                Label("No"),
            ),
            Button("Submit", type = "submit")
        )
    )
    return Div(
        form
    )

#Index page for StatSnap
@rt('/')
def get():
    title = Title("Welcome to StatSnap!")
    main_page = Div(
        Div(
            logo_placement(),  # Image on one side
            Titled(P("Welcome to StatSnap!")),  # Text on the other side
            style="display: flex; align-items: center;",  # Flexbox styling to align side-by-side
        ),
        Div(
            P(A("Sign Up", href="/signup", style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; margin-left: 25px;")),  # Stylish Sign Up button
            P(A("Log In", href="/login", style="padding: 10px 20px; background-color: #008CBA; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;")),  # Stylish Log In button
            P(A("Admin Log In", href="/admin-login", style="padding: 10px 20px; background-color: #FF0000; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;")), # Stylish Admin Log In button
            style="display: flex; justify-content: ; gap: 10px; margin-top: 20px;"  # Center the buttons and add spacing
        )
    )

    return title, main_page

#Reset password retrieval process
@rt("/reset-password", methods=["POST"])
def reset_password(username: str = None, new_password: str = None, confirm_password: str = None):

    # Initialize an error message variable
    error_message = None

    if not username or not new_password or not confirm_password:
        error_message = "All fields are required."

    if new_password != confirm_password:
        error_message =  "Passwords do not match."

    # Hash the new password
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Check in regular user table
    user_response = supabase.table("StatSnap_Login").select("*").eq("username", username).execute()
    if user_response.data:
        # Update password
        supabase.table("StatSnap_Login").update({"password": hashed_password}).eq("username", username).execute()
        return Redirect("/login?message=Password reset successfully.")

    # Check in admin table
    admin_response = supabase.table("StatSnap_Admin").select("*").eq("admin_username", username).execute()
    if admin_response.data:
        # Update admin password
        supabase.table("StatSnap_Admin").update({"admin_password": hashed_password}).eq("admin_username", username).execute()
        return Redirect("/admin-login?message=Password reset successfully.")

    return "Username not found."

#Signup page for StatSnap
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

#Login page for StatSnap
@rt('/login', methods=["GET"])
def get(error: str = None, message: str = None):
    error_message = ""
    success_message = ""

    # Check if message is provided directly as a function argument
    if message:
        success_message = P(message, style="color: green; font-weight: bold;")

    if error:
        error_message = P(f"Error: {error}", style="color: red; font-weight: bold;")
   
    return Titled(
        "LOG IN📝",
        Hr(),
        P('Log In to StatSnap!'),
        success_message,  # Display success message if present
        error_message,
        render_login_form(error),
        A("Go back to home", href="/")
    )

#Admin login page for StatSnap
@rt('/admin-login', methods=["GET"])
def admin_login_page(message: str = None):
    success_message = ""

    # Check if message is provided directly as a function argument
    if message:
        success_message = P(message, style="color: green; font-weight: bold;")

    return Titled(
        "Admin Log In",
        Hr(),
        P("Log in to the Admin Dashboard"),
        success_message,  # Display success message if present
        render_admin_login_form(),
        A("Go back to home", href="/")
    )

#Post signup details to process in backend
@rt("/submit-signup", methods=["POST"])
def post(username: str, password: str):
    if signup(username, password):  # If signup is successful (no duplicate username)
         # Fetch the user ID
        user = supabase.table("StatSnap_Login").select("id").eq("username", username).execute().data[0]

        global current_user_id
        current_user_id = user["id"]

        # Initialize profile
        supabase.table("UserProfile").insert({"user_id": current_user_id}).execute()

        return Redirect("/profile")  # Redirect to the profile page after successful sign-up
    else:
        # Redirect back to signup page with an error message as a query parameter
        return Redirect(f"/signup?error=Username '{username}' is already taken.")

#Post login details to process in backend
@rt("/submit-login", methods=["POST"])
def post(username: str, password: str):
    success, error = login(username, password)
   
    if success:
        return Redirect("/home")  # Redirect to profile page
    else:
        # Re-render the form with the error message
        return render_login_form(error)

#Post admin login details to process in backend
@rt("/submit-admin-login", methods=["POST"])
def submit_admin_login(admin_username: str = None, admin_password: str = None):
    # Check if both fields are provided
    if not admin_username or not admin_password:
        return render_admin_login_form("Missing required fields.")  # Display error if fields are missing

    # Perform the login check
    success, error = admin_login(admin_username, admin_password)

    # Redirect or display error based on login outcome
    if success:
        return Redirect("/admin-home")  # Redirect to the admin dashboard if login is successful
    else:
        return render_admin_login_form(error)  # Re-render the form with the error message if login fails

#Profile page for StatSnap
@rt("/profile", methods=["GET", "POST"])
def get():
    # Define the top bar with title and buttons
    top_bar = Div(
        Div(
            H1("StatSnap Home Page", style={"color": "white", "margin": "0", "font-size": "24px"}),  # Smaller title
            style={"flex-grow": "1"}  # Take up remaining space to push buttons to the right
        ),
        Div(
            A("Friends", href="/friends", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Groups", href="/my-groups", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Your Games", href="/your-games", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Profile", href="/profile", style={"color": "red", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Log Out", href="/", style={"color": "white", "text-decoration": "none", "font-size": "14px"}),  # Logout button
            style={"display": "flex", "align-items": "center"}  # Align vertically in the center
        ),
        style={
            "display": "flex",
            "justify-content": "space-between",
            "align-items": "center",
            "background-color": "blue",
            "padding": "10px"
        }
    )

    # Define the navigation bar below
    '''
    nav_bar = Div(
        Div(
            A("Home", href="/home", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Apex Legends", href="/apex", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Fortnite", href="/fortnite", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Call of Duty: BO6", href="/codbo6", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Warzone", href="/warzone", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Rocket League", href="/rocketleague", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Minecraft", href="/minecraft", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Valorant", href="/valorant", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Dota 2", href="/dota2", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Find Game", href="/find-game", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            style={"display": "flex", "align-items": "center"}
        ),
        style={"background-color": "blue", "padding": "10px"}
    )
    '''

    style = Style("""
        body { font-family: Arial, sans-serif; background-color: #13171f; padding: 20px; }
        .container { background-color: black; padding: 20px; margin: 0 auto; max-width: 600px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
        input, textarea, button { display: block; width: 100%; margin: 10px 0; padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 5px; }
    """)
    title = Title("Profile Page")
    
    form = Form(
        Label("Name:", For="name"),
        Input(id="name", name="name", type="text", placeholder="Enter your name"),
        Label("Email:", For="email"),
        Input(id="email", name="email", type="email", placeholder="Enter your email"),
        Label("Bio:", For="bio"),
        Textarea(id="bio", name="bio", placeholder="Tell us about yourself"),
        Label("Top Game 1:", For="game1"),
        Input(id="game1", name="game1", type="text", placeholder="Enter your top game"),
        Label("Top Game 2:", For="game2"),
        Input(id="game2", name="game2", type="text", placeholder="Enter your second top game"),
        Label("Top Game 3:", For="game3"),
        Input(id="game3", name="game3", type="text", placeholder="Enter your third top game"),
        Button("Save Changes", type="submit"),
    )
    
    container = Div(
        H1("Profile Page"),
        form,
        cls="container"
    )

    # Define the page content
    page_content = Div(
        top_bar,  # Include the new top bar
        #nav_bar,  # Navigation bar below the title
        render_nav_bar(current_page="profile"),
        style,
        Container(container),
        style={"background-color": "black", "color": "white", "height": "100vh"}
    )

    # Return the full page
    return title, page_content


#Home page for StatSnap
@rt('/home', methods=["GET"])
def home_page():
    global current_user_id  # Assume this is set when the user logs in

    if current_user_id is None:
        return Redirect("/login")  # Redirect to login if not logged in

    # Define the top bar with title and buttons
    top_bar = Div(
        Div(
            H1("StatSnap Home Page", style={"color": "white", "margin": "0", "font-size": "24px"}),  # Smaller title
            style={"flex-grow": "1"}  # Take up remaining space to push buttons to the right
        ),
        Div(
            A("Friends", href="/friends", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Groups", href="/my-groups", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Your Games", href="/your-games", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Profile", href="/profile", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Log Out", href="/", style={"color": "white", "text-decoration": "none", "font-size": "14px"}),  # Logout button
            style={"display": "flex", "align-items": "center"}  # Align vertically in the center
        ),
        style={
            "display": "flex",
            "justify-content": "space-between",
            "align-items": "center",
            "background-color": "blue",
            "padding": "10px"
        }
    )

    # Define the navigation bar below
    '''
    nav_bar = Div(
        Div(
            A("Home", href="/home", style={"color": "red", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Apex Legends", href="/apex", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Fortnite", href="/fortnite", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Call of Duty: BO6", href="/codbo6", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Warzone", href="/warzone", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Rocket League", href="/rocketleague", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Minecraft", href="/minecraft", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Valorant", href="/valorant", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Dota 2", href="/dota2", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Find Game", href="/find-game", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            style={"display": "flex", "align-items": "center"}
        ),
        style={"background-color": "blue", "padding": "10px"}
    )
    '''

    style = Style("""
        body { font-family: Arial, sans-serif; background-color: #13171f; padding: 20px; }
        .container { background-color: black; padding: 20px; margin: 0 auto; max-width: 600px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
        input, textarea, button { display: block; width: 100%; margin: 10px 0; padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 5px; }
    """)
    title = Title("Home Page")

    # Define the page content
    page_content = Div(
        top_bar,  # Include the new top bar
        #nav_bar,  # Navigation bar below the title
        render_nav_bar(current_page="home"),
        style,
        Div(
            P("Welcome to StatSnap! Use the navigation bar to explore games, manage groups, and more.",
              style={"font-size": "16px", "padding": "20px"}),  # Adjust paragraph text size
        ),
        style={"background-color": "black", "color": "white", "height": "100vh"}
    )

    # Return the full page
    return title, page_content

#Admin home page for StatSnap
@rt('/admin-home', methods=["GET"])
def admin_dashboard():
    global admin_current_user_id  # Assume this is set when the admin user logs in

    if admin_current_user_id is None:
        return Redirect("/admin-login")  # Redirect to admin login if not logged in

    return Titled(
        "Admin Dashboard",
        Hr(), 
        P("Welcome to the Admin Dashboard!"), 
        Br(),
        Div(
            P(A("Remove Users", href="/remove-user-page", style="padding: 10px 20px; background-color: #FF0000; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; margin-right: 10px;")),  # Button 1
            P(A("Manage Games", href="/manage-games", style="padding: 10px 20px; background-color: #008CBA; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;")),  # Button 2
            style="display: flex; align-items: center; justify-content: flex-start;"  # Flexbox styling for side-by-side buttons
        ),
        Br(),
        A("Sign Out", href="/")
    )

@rt('/remove-user-page', methods=["GET"])
def remove_userpage():
    return Titled(
        "Remove Users",
        render_admin_user_list(),
        A("Return to Admin Home", href="/admin-home"),
        Br(),
        A("Sign Out", href="/")
    )



@rt('/remove-user', methods=["POST"])
def remove_user(user_id: str = None):
    if not user_id:
        return Div(Span("User ID is missing or invalid.", style="color: red;"))

    if not admin_current_user_id:
        return Div(Span("Admin not logged in.", style="color: red;"))

    # Attempt to delete the user from the database
    response = supabase.table("StatSnap_Login").delete().eq("id", user_id).execute()

    if response is None or len(response.data) == 0:  # Check if delete was successful
        return Div(
            Span("Failed to remove user. Please try again.", style="color: red;"),
            Button("Retry", type="button", onclick="location.reload()")
        )

    # Return a confirmation to replace the user's entry in the list
    return Div(
        Span("User removed successfully.", style="color: green;"),
        style="margin-bottom: 10px;"
    )

        
#Friends page for StatSnap
@rt('/friends', methods=["GET"])
def friends_page():
    global current_user_id  # Assume this is set when the user logs in

    if current_user_id is None:
        return Redirect("/login")  # Redirect to login if not logged in

    return Titled(
        "StatSnap Friends Page",
        Hr(),
        P("Add New Friends!"),
        render_user_list(current_user_id),  # Display the user list with Add Friend buttons
        #js_supabase_client(current_user_id),     # Pass current_user_id to the JS function
        #add_friend_script(),  # Add the JavaScript function for adding friends
        accept_friend_script(),             # JavaScript function for accepting friend requests
        A("Go back to home", href="/home"),
        Br(),
        Br(),
        A("Sign Out", href="/")
    )

#Post add friend details to process in backend
@rt("/add-friend", methods=["POST"])
def add_friend(friend_id: str):
    global current_user_id  # Use the logged-in user ID

    # Ensure the user is logged in
    if not current_user_id:
        return {"success": False, "message": "User not logged in."}

    # Insert the friend request into the FriendRequests table
    response = supabase.table("FriendRequests").insert({
        "sender_id": current_user_id,
        "receiver_id": friend_id,  # Use friend_id as receiver_id
        "status": "pending"
    }).execute()

    # Check if insertion was successful
    if response.data:
        return Redirect("/friends")  # Redirect to home page on success
    else:
        return Titled(
            "Error",
            P("Failed to send friend request."),
            A("Go back to home", href="/home"),
            A("Sign Out", href="/")
        )

#Post friend actions to process in backend
@rt("/friend-action", methods=["POST"])
def friend_action(friend_id: str):
    global current_user_id  # Use the logged-in user ID

    # Ensure the user is logged in
    if not current_user_id:
        return Redirect("/login")  # Redirect if not logged in

    # Check if there’s a request from friend_id to current_user_id
    request_response = supabase.table("FriendRequests").select("*").match({
        "sender_id": friend_id,
        "receiver_id": current_user_id
    }).execute()

    if request_response.data:  # If a request exists, accept the friend request
        # Update status to "accepted" for both sender and receiver in the FriendRequests table
        supabase.table("FriendRequests").update({
            "status": "accepted"
        }).match({
            "sender_id": friend_id,
            "receiver_id": current_user_id
        }).execute()

        supabase.table("FriendRequests").update({
            "status": "accepted"
        }).match({
            "sender_id": current_user_id,
            "receiver_id": friend_id
        }).execute()

        # Return updated HTML for both users to show "Current Friend"
        return Div(
            Button("Current Friend", type="button", disabled=True, style="background-color: #333;")
        )

    else:  # Otherwise, send a new friend request
        supabase.table("FriendRequests").insert({
            "sender_id": current_user_id,
            "receiver_id": friend_id,
            "status": "sent"
        }).execute()

        # Return HTML that will replace the button with "Friend Request Sent"
        return Div(
            Button("Friend Request Sent", type="button", disabled=True, style="background-color: #333;")
        )

#Create group page for StatSnap
@rt("/create-group", methods=["GET", "POST"])
def create_group_page(group_name=None, friend_ids=None):
    global current_user_id
    if current_user_id is None:
        return Redirect("/login")


    # Print received data for debugging
    print("Received group_name:", group_name)
    print("Received friend_ids:", friend_ids)
    
    # Check if group_name and friend_ids are provided
    if group_name and friend_ids:
        # Create the group
        group_response = supabase.table("Groups").insert({
            "owner_id": current_user_id,
            "name": group_name,
            "created_at": "now()"  # Supabase/Postgres should handle the timestamp
        }).execute()

        if not group_response.data:
            return Titled("Error", P("Failed to create the group."))

        group_id = group_response.data[0]["id"]

        # Add current user as a group member (owner)
        supabase.table("GroupMembers").insert({"group_id": group_id, "user_id": current_user_id, "added_at": "now()"}).execute()

        # Add selected friends as members
        for friend_id in friend_ids:
            if friend_id:  # Ensure friend_id is valid
                supabase.table("GroupMembers").insert({"group_id": group_id, "user_id": friend_id, "added_at": "now()"}).execute()

        # Redirect to the "My Groups" page after creating the group
        return Redirect("/my-groups")

    # Render the group creation form if no data is provided (GET request)
    return Titled(
        "Create New Group",
        P("Create New Groups With Friends!"),
        render_group_creation_form(current_user_id),  # Display the form to create a group
        A("Go to My Groups", href="/my-groups"),
        Br(),
        Br(),
        A("Go back to home", href="/home"),
        Br(),
        Br(),
        A("Sign out", href="/")
    )

#My groups page for StatSnap
@rt("/my-groups", methods=["GET"])
def my_groups_page():
    global current_user_id
    if current_user_id is None:
        return Redirect("/login")

    # Step 1: Get the group IDs the user is a part of as a member
    member_groups_response = supabase.table("GroupMembers").select("group_id").eq("user_id", current_user_id).execute()
    member_groups = member_groups_response.data
    member_group_ids = [group['group_id'] for group in member_groups]

    # Step 2: Get the group IDs where the user is the owner
    owner_groups_response = supabase.table("Groups").select("id").eq("owner_id", current_user_id).execute()
    owner_groups = owner_groups_response.data
    owner_group_ids = [group['id'] for group in owner_groups]

    # Step 3: Combine both sets of group IDs and remove duplicates
    all_group_ids = list(set(member_group_ids + owner_group_ids))

    if not all_group_ids:
        return Titled(
            "My Groups", 
            P("You are not part of any groups yet."),
            A("Go back to Create A Group", href="/create-group"),
            Br(),
            Br(),
            A("Sign out", href="/")
        )

    # Step 4: Fetch the group details using the combined group IDs
    groups_response = supabase.table("Groups").select("*").in_("id", all_group_ids).execute()
    groups = groups_response.data

     # Step 5: Fetch the usernames of all group owners
    owner_ids = list(set(group['owner_id'] for group in groups))
    owners_response = supabase.table("StatSnap_Login").select("id, username").in_("id", owner_ids).execute()
    owners = {owner['id']: owner['username'] for owner in owners_response.data}

    # Render the groups page with the retrieved group information, including owner information
    return Titled(
        "My Groups",
        P("These are the groups you are a member of:"),
        *[Div(
            P(f"Group Name: {group['name']}"), 
            P(f"Created At: {group['created_at']}"), 
            P(f"Owner: {'You' if group['owner_id'] == current_user_id else owners.get(group['owner_id'], 'Unknown User')}")
        ) for group in groups],
        A("Create a New Group", href="/create-group"),
        Br(),
        Br(),
        A("Go back to home", href="/home"),
        Br(),
        Br(),
        A("Sign out", href="/")
    )

#Route for Find Game page
@rt('/find-game', methods=["GET"])
def find_game_page():

    # Define the game list with names and links
    games = [
        {"name": "Apex Legends", "link": "/apex"},
        {"name": "Fortnite", "link": "/fortnite"},
        {"name": "Call of Duty: BO6", "link": "/codbo6"},
        {"name": "Warzone", "link": "/warzone"},
        {"name": "Rocket League", "link": "/rocketleague"},
        {"name": "Minecraft", "link": "/minecraft"},
        {"name": "Valorant", "link": "/valorant"},
        {"name": "Dota 2", "link": "/dota2"},
        {"name": "League of Legends", "link": "/league"},
        {"name": "PUBG", "link": "/pubg"},
        {"name": "Overwatch", "link": "/overwatch"},
        {"name": "Counter-Strike: GO 2", "link": "/csgo"},
        {"name": "Clash Royale", "link": "/clashroyale"},
        {"name": "Clash of Clans", "link": "/clashofclans"},
        {"name": "Pokemon GO", "link": "/pokemongo"}
    ]

    # Generate the game list as <li> elements with clickable links
    game_list_items = [
        Li(
            A(
                game["name"],
                href=game["link"],
                style={
                    "text-decoration": "none",
                    "color": "white",
                    "padding": "10px",
                    "display": "block",
                    "border": "1px solid #444",
                    "border-radius": "5px",
                    "background-color": "#1e1e1e",
                    "text-align": "center"
                }
            ),
            style={"list-style-type": "none", "margin": "5px"}
        )
        for game in games
    ]

    # JavaScript for filtering games
    filter_script = Script("""
        function filterGames() {
            const searchInput = document.getElementById("search-bar").value.toLowerCase();
            const games = document.getElementById("game-list").getElementsByTagName("li");

            for (let i = 0; i < games.length; i++) {
                const gameName = games[i].innerText.toLowerCase();
                if (gameName.includes(searchInput)) {
                    games[i].style.display = ""; // Show matching items
                } else {
                    games[i].style.display = "none"; // Hide non-matching items
                }
            }
        }
    """)

    # Define the top bar with title and buttons
    top_bar = Div(
        Div(
            H1("StatSnap Home Page", style={"color": "white", "margin": "0", "font-size": "24px"}),  # Smaller title
            style={"flex-grow": "1"}  # Take up remaining space to push buttons to the right
        ),
        Div(
            A("Friends", href="/friends", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Groups", href="/my-groups", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Your Games", href="/your-games", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Profile", href="/profile", style={"color": "white", "margin-right": "10px", "text-decoration": "none", "font-size": "14px"}),
            A("Log Out", href="/", style={"color": "white", "text-decoration": "none", "font-size": "14px"}),  # Logout button
            style={"display": "flex", "align-items": "center"}  # Align vertically in the center
        ),
        style={
            "display": "flex",
            "justify-content": "space-between",
            "align-items": "center",
            "background-color": "blue",
            "padding": "10px"
        }
    )

    style = Style("""
        body { font-family: Arial, sans-serif; background-color: #13171f; padding: 20px; }
        .container { background-color: black; padding: 20px; margin: 0 auto; max-width: 600px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
        input, textarea, button { display: block; width: 100%; margin: 10px 0; padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 5px; }
    """)
    title = Title("Find Game Page")

    # Page structure
    page_content = Div(
        Div(
            Div("Find a Game", style={"font-size": "24px", "margin-bottom": "10px"}),
            Input(
                id="search-bar",
                placeholder="Search for a game...",
                onkeyup="filterGames()",
                style={"width": "100%", "padding": "10px", "font-size": "16px", "margin-bottom": "20px"}
            ),
            Ul(
                *game_list_items,
                id="game-list",
                style={"list-style-type": "none", "padding": "0"}
            ),
            style={"padding": "20px"}
        ),
        filter_script,  # JavaScript for filtering
        style={"background-color": "black", "color": "white", "height": "100vh"}
    )

    return title, top_bar, render_nav_bar(current_page="find-game"), style, page_content


@rt('/manage-games', methods=["GET", "POST"])
async def manage_games(request):
    if not admin_current_user_id:  # Ensure only logged-in admins can access
        return Redirect("/admin-login")

    # Extract form data
    if request.method == "POST":
        form_data = await request.form()
        game_id = form_data.get("game_id")
        action = form_data.get("action")
        game_name = form_data.get("game_name")
        game_link = form_data.get("game_link")
        
        print(f"Form data received: game_id={game_id}, action={action}, game_name={game_name}, game_link={game_link}")

        if action == "edit" and game_id:
            # Update game details
            supabase.table("Games").update({
                "name": game_name,
                "link": game_link
            }).eq("id", game_id).execute()
            return Redirect("/manage-games")

        elif action == "remove" and game_id:
            # Remove game from database
            supabase.table("Games").delete().eq("id", game_id).execute()
            return Redirect("/manage-games")

        elif action == "add":
            # Add new game to database
            response = supabase.table("Games").insert({
                "name": game_name,
                "link": game_link
            }).execute()
            print(response)
            return Redirect("/manage-games")

    # Render games list
    games = get_games()

    return Titled(
        "Manage Games",
        Div(
            H2("Add New Game"),
            Form(
                Input(type="text", name="game_name", placeholder="Game Name", required=True),
                Input(type="text", name="game_link", placeholder="Game Link", required=True),
                Input(type="hidden", name="action", value="add"),
                Button("Add Game", type="submit"),
                method="POST",
                style="margin-bottom: 20px;",
            ),
        ),
        *[
            Div(
                P(f"Game: {game['name']}"),
                P(f"Link: {game['link']}"),
                Form(
                    Input(type="hidden", name="game_id", value=game["id"]),
                    Input(type="hidden", name="action", value="edit"),
                    Input(type="text", name="game_name", value=game["name"]),
                    Input(type="text", name="game_link", value=game["link"]),
                    Button("Edit", type="submit"),
                    method="POST",
                    style="display: inline-block; margin-right: 10px;",
                ),
                Form(
                    Input(type="hidden", name="game_id", value=game["id"]),
                    Input(type="hidden", name="action", value="remove"),
                    Button("Remove", type="submit", style="background-color: red; color: white;"),
                    method="POST",
                    style="display: inline-block;",
                ),
                style="margin-bottom: 20px;",
            )
            for game in games
        ],
        Br(),
        A("Go back to admin home", href="/admin-home"),
        Br(),
        A("Sign Out", href="/")
    )


#Route for Apex Legends game page
@rt('/apex', methods=["GET"])
def get():
    return Titled(
        "Apex Legends",
        Apex_render_content(),
        A("Go back to home", href="/home")
    )

#Route for Fortnite game page
@rt('/fortnite', methods=["GET"])
def get():
    return Titled(
        "Fortnite", 
        Fortnite_render_content(),
        A("Go back to home", href="/home")
    )

#Route for Call of Duty Black Ops 6 game page
@rt('/codbo6', methods=["GET"])
def get():
    return Titled(
        "Call of Duty BO: 6", 
        COD_render_content(),
        A("Go back to home", href="/home")
    )

#Route for Call of Duty: Warzone game page
@rt('/warzone', methods=["GET"])
def get():
    return Titled(
        "Call of Duty: Warzone", 
        Warzone_render_content(),
        A("Go back to home", href="/home")
    )

#Route for Rocket League game page
@rt('/rocketleague', methods=["GET"])
def get():
    return Titled(
        "Rocket League",
        RocketLeague_render_content(),
        A("Go back to home", href="/home")
    )

#Route for Minecraft game page
@rt('/minecraft', methods=["GET"])
def get():
    return Titled(
        "Minecraft", 
        Minecraft_render_content(),
        A("Go back to home", href="/home")
    )

#Route for Valorant game page
@rt('/valorant', methods=["GET"])
def get():
    return Titled(
        "Valorant", 
        Valorant_render_content(),
        A("Go back to home", href="/home")
    )

#Route for Dota2 game page
@rt('/dota2', methods=["GET"])
def get():
    return Titled(
        "Dota2", 
        Dota2_render_content(),
        A("Go back to home", href="/home")
    )

serve()

