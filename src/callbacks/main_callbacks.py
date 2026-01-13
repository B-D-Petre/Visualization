from dash.dependencies import Input, Output, State
from dash import dcc, html, ALL
from dash import ctx

from src.data.loader import data_loader
from src.components import figures, cards
from src.layouts import topic_1, topic_3, topic_4

def register_callbacks(app):
    
    # --- ROUTING ---
    @app.callback(
        Output("page-content", "children"),
        Input("main-tabs", "value")
    )
    def render_content(tab):
        if tab == "topic-1":
            return topic_1.get_layout()
        elif tab == "topic-3":
            return topic_3.get_layout()
        elif tab == "topic-4":
            return topic_4.get_layout()
        return html.Div("404")

    # --- TOPIC 3: COMPARISON ---
    
    # Update Song Dropdowns based on Decade
    @app.callback(
        [Output("song-dropdown-1", "options"), Output("song-dropdown-2", "options")],
        Input("decade-selector", "value")
    )
    def update_song_options(decade):
        options = data_loader.get_songs_for_decade(decade)
        return options, options

    # Update Spider Graph
    @app.callback(
        Output("spider-comparison-graph", "figure"),
        [Input("decade-selector", "value"),
         Input("song-dropdown-1", "value"),
         Input("song-dropdown-2", "value"),
         Input("show-genre-1", "value"),
         Input("show-genre-2", "value")]
    )
    def update_comparison(decade, s1, s2, show_g1, show_g2):
        # Handle Checkbox list for show_genre (can be None or list)
        g1 = bool(show_g1)
        g2 = bool(show_g2)
        return figures.draw_spider_comparison(decade, s1, s2, g1, g2)

    # --- TOPIC 1: ANALYSIS ---
    
    @app.callback(
        [Output("honeycomb-container", "children"),
         Output("area-plots-graph", "figure"),
         Output("overlay-trend-graph", "figure")],
        [Input("decade-selector", "value"),
         Input("analysis-genre-dropdown", "value")]
    )
    def update_analysis(decade, selected_genres):
        # 1. Honeycomb
        # We generate small spider graphs for previous decades + current
        decades = ['50s', '60s', '70s', '80s', '90s', '00s', '10s', '20s']
        
        # Determine strict list of decades to show in honeycomb
        # Maybe show all? Let's show all for context
        honeycomb_graphs = []
        for d in decades:
             # Highlight current
             style = {"width": "180px", "height": "180px", "margin": "5px"}
             if d == decade:
                 style["border"] = "2px solid #636EFA"
                 style["borderRadius"] = "50%"

             honeycomb_graphs.append(html.Div(
                 dcc.Graph(
                     figure=figures.draw_spider_average(d, selected_genres),
                     config={'displayModeBar': False},
                     style={"width": "100%", "height": "100%"}
                 ),
                 style=style
             ))

        # 2. Area Plots
        area_fig = figures.draw_feature_area_plots(decade, selected_genres)
        
        # 3. Overview Trend
        # Simplistic overlay for now
        overlay_fig = figures.draw_genre_trends_line()
        # Add marker for current decade
        # (This logic handled inside figure function or could be added here)
        
        return honeycomb_graphs, area_fig, overlay_fig

    # --- TOPIC 4: TRENDS ---
    
    @app.callback(
        [Output("trends-main-graph", "figure"),
         Output("decade-card-container", "children"),
         Output("change-graph-desc", "figure")],
        Input("decade-selector", "value")
    )
    def update_trends(decade):
        trend_fig = figures.draw_genre_trends_line()
        
        card = cards.create_decade_card(decade)
        
        change_fig = figures.draw_change_chart(decade)
        
        return trend_fig, card, change_fig
