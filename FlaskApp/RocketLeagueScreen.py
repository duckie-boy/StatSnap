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

@rt("/")
def get():
    return Titled("Rocket League", render_content()) 

serve()