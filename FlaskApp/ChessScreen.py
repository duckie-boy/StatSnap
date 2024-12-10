from fasthtml.common import *

app, rt = fast_app()

def render_content():
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
                name = "gamemode",
                placeholder = "Game Mode",
                required = True
            ),
            Input(
                type = "number",
                name = "startingTime",
                placeholder = "Starting Time",
                required = True
            ),
            Input(
                type = "number",
                name = "timeLeft",
                placeholder = "Time Left",
                required = True
            ),
            Input(
                type = "number",
                name = "brilliantMoves",
                placeholder = "Brilliant Moves"
            ),
            Input(
                type = "number",
                name = "blunders",
                placeholder = "Blunders"
            ),
            Input(
                type = "number",
                name = "openingPercent",
                placeholder = "Percent of Opening Played to Book"
            ),
            Button("Submit", type = "submit")
        )
    )
    return Div(
        form
    )

@rt("/")
def get():
    return Titled("Chess", render_content()) 

serve()