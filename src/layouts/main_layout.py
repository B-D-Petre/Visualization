from dash import html, dcc

def create_main_layout():
    return html.Div(
        style={
            "display": "flex", "flexDirection": "row", 
            "height": "100vh", "width": "100vw", 
            "overflow": "hidden", "backgroundColor": "#121212"
        },
        children=[
            # --- SIDEBAR (Decade Selector) ---
            html.Div(
                id="sidebar",
                style={
                    "width": "200px", "height": "100%", "backgroundColor": "#181818", 
                    "display": "flex", "flexDirection": "column", "padding": "20px", "boxSizing": "border-box",
                    "borderRight": "1px solid #333"
                },
                children=[
                    html.H3("Decades", style={"color": "white", "textAlign": "center", "marginBottom": "20px"}),
                    dcc.RadioItems(
                        id="decade-selector",
                        options=[
                            {'label': '1950s', 'value': '50s'},
                            {'label': '1960s', 'value': '60s'},
                            {'label': '1970s', 'value': '70s'},
                            {'label': '1980s', 'value': '80s'},
                            {'label': '1990s', 'value': '90s'},
                            {'label': '2000s', 'value': '00s'},
                            {'label': '2010s', 'value': '10s'},
                            {'label': '2020s', 'value': '20s'},
                        ],
                        value='10s', # Default
                        labelStyle={'display': 'block', 'padding': '10px', 'color': '#ccc', 'cursor': 'pointer'},
                        style={"flex": "1"}
                    )
                ]
            ),
            
            # --- MAIN CONTENT ---
            html.Div(
                style={"flex": "1", "display": "flex", "flexDirection": "column", "height": "100%"},
                children=[
                    # Top Navigation
                    html.Div(
                        style={"height": "60px", "backgroundColor": "#1E1E24", "display": "flex", "justifyContent": "center", "alignItems": "center"},
                        children=[
                            dcc.Tabs(
                                id="main-tabs",
                                value="topic-3",
                                children=[
                                    dcc.Tab(label="Analysis", value="topic-1", style=tab_style, selected_style=tab_selected_style),
                                    dcc.Tab(label="Compare Songs", value="topic-3", style=tab_style, selected_style=tab_selected_style),
                                    dcc.Tab(label="Trends", value="topic-4", style=tab_style, selected_style=tab_selected_style),
                                ],
                                style={"height": "100%", "width": "500px"}
                            )
                        ]
                    ),
                    
                    # Page Content
                    dcc.Loading(
                        id="loading-content",
                        type="circle",
                        children=html.Div(id="page-content", style={"flex": "1", "padding": "10px", "overflow": "hidden"})
                    )
                ]
            )
        ]
    )

# Styles
tab_style = {
    'backgroundColor': '#1E1E24', 'color': '#888', 'border': 'none', 
    'padding': '15px', 'fontSize': '16px'
}
tab_selected_style = {
    'backgroundColor': '#2A2A35', 'color': 'white', 'borderBottom': '3px solid #636EFA', 
    'padding': '15px', 'fontSize': '16px', 'fontWeight': 'bold'
}
