from dash import html, dcc
from src.components.cards import create_legend
from src.data.loader import data_loader

def get_layout():
    # Helper to get initial genres
    genres = data_loader.get_genres()
    
    return html.Div(
        style={"display": "flex", "flexDirection": "row", "height": "100%", "width": "100%", "padding": "10px", "gap": "10px"}, 
        children=[
             # Left Column: Honeycomb
             html.Div(
                 style={"flex": "1", "display": "flex", "flexDirection": "column", "minWidth": "0"},
                 children=[
                     dcc.Dropdown(
                         id='analysis-genre-dropdown',
                         options=[{'label': g.title(), 'value': g} for g in genres],
                         multi=True,
                         placeholder="Filter Genres...",
                         style={'color': 'black', 'marginBottom': '10px'}
                     ),
                     create_legend(),
                     html.Div(
                         id='honeycomb-container',
                         style={"flex": "1", "overflowY": "auto", "display": "flex", "flexWrap": "wrap", "justifyContent": "center"}
                     ),
                     # Overlay
                     html.Div(
                         style={"height": "150px", "marginTop": "10px"},
                         children=dcc.Graph(id='overlay-trend-graph', config={'displayModeBar': False}, style={"height": "100%"})
                     )
                 ]
             ),
             
             # Right Column: Area Plots
             html.Div(
                 style={"flex": "1", "display": "flex", "flexDirection": "column", "borderLeft": "1px solid #333", "paddingLeft": "10px"},
                 children=[
                     dcc.Graph(id='area-plots-graph', style={"height": "100%", "width": "100%"})
                 ]
             )
        ]
    )
