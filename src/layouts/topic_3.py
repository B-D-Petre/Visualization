from dash import html, dcc
from src.components.figures import get_empty_figure

def get_layout():
    return html.Div(
        style={"display": "flex", "height": "90%", "width": "100%", "padding": "20px", "gap": "20px"},
        children=[
            # Control Panel
            html.Div(
                style={"flex": "1", "backgroundColor": "rgba(255,255,255,0.05)", "padding": "20px", "borderRadius": "10px"},
                children=[
                    html.H4("Compare Songs", style={"color": "white"}),
                    
                    html.Label("Song 1", style={"color": "#636EFA"}),
                    dcc.Dropdown(id="song-dropdown-1", style={"color": "black", "marginBottom": "10px"}),
                    dcc.Checklist(
                        id="show-genre-1",
                        options=[{'label': ' Show Genre Average', 'value': 'show'}],
                        style={"color": "white", "marginBottom": "20px"}
                    ),
                    
                    html.Label("Song 2", style={"color": "#EF553B"}),
                    dcc.Dropdown(id="song-dropdown-2", style={"color": "black", "marginBottom": "10px"}),
                    dcc.Checklist(
                        id="show-genre-2",
                        options=[{'label': ' Show Genre Average', 'value': 'show'}],
                        style={"color": "white", "marginBottom": "20px"}
                    ),
                ]
            ),
            
            # Graph Area
            html.Div(
                style={"flex": "3", "backgroundColor": "rgba(0,0,0,0.2)", "borderRadius": "10px", "position": "relative"},
                children=[
                    dcc.Graph(id="spider-comparison-graph", style={"height": "100%", "width": "100%"})
                ]
            )
        ]
    )
