from dash import html
from src.components.figures import PAPER_BG, DECADE_RGB

DECADE_INFO = {
    '50s': "The decade that gave birth to rock 'n' roll...",
    '60s': "The British Invasion landed when The Beatles conquered America...",
    '70s': "A decade of extremes. Disco packed dance floors while punk burned them down...",
    '80s': "Synthesizers and drum machines took over everything...",
    '90s': "Nirvana's Nevermind killed hair metal overnight...",
    '00s': "The digital revolution hit hard...",
    '10s': "Streaming won. Spotify and Apple Music made everything available...",
    '20s': "TikTok became the new radio..."
}

def create_decade_card(decade):
    """Creates the informational card for the selected decade."""
    # Convert RGB tuple to Hex for CSS if needed, or just use mapped colors
    # We'll use a simple mapping for now
    color_map = {'50s': '#E74C3C', '60s': '#D35400', '70s': '#8E44AD', '80s': '#2980B9', 
                 '90s': '#C0392B', '00s': '#27AE60', '10s': '#F1C40F', '20s': '#1ABC9C'}
    color = color_map.get(decade, '#333')
    text = DECADE_INFO.get(decade, "Description unavailable.")
    
    return html.Div(style={
        'fontFamily': 'sans-serif', 'backgroundColor': PAPER_BG, 
        'border': '1px solid rgba(255,255,255,0.1)', 'borderRadius': '8px',
        'height': '100%', 'display': 'flex', 'flexDirection': 'column', 'overflow': 'hidden'
    }, children=[
        html.Div(style={'backgroundColor': color, 'height': '6px', 'width': '100%', 'flexShrink': 0}),
        html.Div(style={'padding': '20px', 'overflowY': 'auto', 'flex': '1'}, children=[
            html.H2(f"The {decade}", style={'marginTop': '0', 'borderBottom': f'2px solid {color}', 'paddingBottom': '10px', 'color': 'white'}),
            html.P(text, style={'fontSize': '1.1em', 'lineHeight': '1.5', 'color': '#eee'}),
            # Image placeholder - removing to avoid broken images if they don't exist
            # html.Img(src=f'assets/imgs/{decade}.jpg', ...) 
        ])
    ])

def create_legend():
    """Returns the legend for the spider graph dimensions."""
    return html.Div(
        className="legend-container",
        children=[
             html.Span("E: Energy", style={"marginRight": "10px", "color": "#FF6B6B"}),
             html.Span("D: Danceability", style={"marginRight": "10px", "color": "#DA77F2"}),
             html.Span("V: Valence", style={"marginRight": "10px", "color": "#FFD93D"}),
             html.Span("A: Acousticness", style={"marginRight": "10px", "color": "#6BCB77"}),
             html.Span("I: Instrumentalness", style={"color": "#4D96FF"})
        ],
        style={
            "textAlign": "center", "fontSize": "12px", "padding": "10px",
            "backgroundColor": "rgba(0,0,0,0.3)", "borderRadius": "5px", "color": "white"
        }
    )
