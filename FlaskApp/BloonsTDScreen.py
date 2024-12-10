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
            Input(
                type = "text",
                name = "map",
                placeholder = "Map",
                required = True
            ),
            Input(
                type = "text",
                name = "hero",
                placeholder = "Hero",
                required = True
            ),
            Input(
                type = "number",
                name = "towersPlaced",
                placeholder = "Towers Placed",
                required = True
            ),
            Input(
                type = "text",
                name = "mvpTower",
                placeholder = "MVP Tower",
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
                name = "popCount",
                placeholder = "Pop Count",
                required = True
            ),
            Input(
                type = "number",
                name = "continues",
                placeholder = "Continues",
                required = True
            ),
            Input(
                type = "number",
                name = "score",
                placeholder = "Score",
                required = True
            ),
            Button("Submit", type = "submit")
        )
    )
    return Div(
        form
    )

@rt("/")
def get():
    return Titled("Bloons Tower Defense", render_content()) 

serve()