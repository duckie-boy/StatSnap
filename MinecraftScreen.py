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

@rt("/")
def get():
    return Titled("Minecraft", render_content()) 

serve()