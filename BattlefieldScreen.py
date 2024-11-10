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

@rt("/")
def get():
    return Titled("Battlefield", render_content()) 

serve()