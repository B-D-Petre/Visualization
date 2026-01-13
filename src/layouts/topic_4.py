from dash import html, dcc

def get_layout():
    return html.Div(
        style={"display": "flex", "flexDirection": "column", "height": "100%", "padding": "20px"},
        children=[
            # Top: Main Trends
            html.Div(
                style={"flex": "1", "marginBottom": "20px"},
                children=dcc.Graph(id="trends-main-graph", style={"height": "100%"})
            ),
            
            # Bottom: Info
            html.Div(
                style={"flex": "1", "display": "flex", "gap": "20px"},
                children=[
                    html.Div(
                        style={"flex": "1", "border": "1px solid #333"},
                        children=dcc.Graph(id="change-graph-desc", style={"height": "100%"}) # Changes Graph 1
                    ),
                    html.Div(
                        id="decade-card-container",
                        style={"flex": "1"}
                    )
                ]
            )
        ]
    )
