from dash import html, dcc
from src.components.figures import get_empty_figure

def get_layout():
    return html.Div(
        style={"display": "flex", "height": "90%", "width": "100%", "padding": "20px", "gap": "20px"},
        children=[
            # Left Column: Song Selectors (Split Top/Bottom)
            html.Div(
                style={"flex": "1", "display": "flex", "flexDirection": "column", "gap": "20px"},
                children=[
                    # Top Left: Song 1
                    html.Div(
                        style={
                            "flex": "1", 
                            "backgroundColor": "rgba(255,255,255,0.05)", 
                            "padding": "20px", 
                            "borderRadius": "10px",
                            "display": "flex", "flexDirection": "column", "justifyContent": "center"
                        },
                        children=[
                            html.H4("Song 1", style={"color": "#636EFA", "marginTop": "0"}),
                            dcc.Dropdown(id="song-dropdown-1", style={"color": "black", "marginBottom": "15px"}),
                            dcc.Checklist(
                                id="show-genre-1",
                                options=[{'label': ' Show Genre Average', 'value': 'show'}],
                                style={"color": "white"}
                            ),
                        ]
                    ),
                    
                    # Bottom Left: Song 2
                    html.Div(
                        style={
                            "flex": "1", 
                            "backgroundColor": "rgba(255,255,255,0.05)", 
                            "padding": "20px", 
                            "borderRadius": "10px",
                            "display": "flex", "flexDirection": "column", "justifyContent": "center"
                        },
                        children=[
                            html.H4("Song 2", style={"color": "#EF553B", "marginTop": "0"}),
                            dcc.Dropdown(id="song-dropdown-2", style={"color": "black", "marginBottom": "15px"}),
                            dcc.Checklist(
                                id="show-genre-2",
                                options=[{'label': ' Show Genre Average', 'value': 'show'}],
                                style={"color": "white"}
                            ),
                        ]
                    )
                ]
            ),
            
            # Right Column: Graph Area (Occupies right half)
            html.Div(
                style={"flex": "1", "backgroundColor": "rgba(0,0,0,0.2)", "borderRadius": "10px", "position": "relative"},
                children=[
                    dcc.Graph(id="spider-comparison-graph", style={"height": "100%", "width": "100%"})
                ]
            )
        ]
    )
