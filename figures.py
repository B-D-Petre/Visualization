import plotly.graph_objects as go
from dash import dcc, html
import pandas as pd
import plotly.express as px
import numpy as np


# Load preprocessed spider graph data
spider_csv_path = "assets/spider_graph_data.csv"
spider_data = pd.read_csv(spider_csv_path)

def get_genres():
    if 'playlist_genre' in spider_data.columns:
        return sorted(spider_data['playlist_genre'].dropna().unique().tolist())
    return []

def get_genres_for_decade(decade):
    """Get genres that have data for a specific decade."""
    if 'playlist_genre' in spider_data.columns and 'decade' in spider_data.columns:
        decade_data = spider_data[spider_data['decade'] == decade]
        return sorted(decade_data['playlist_genre'].dropna().unique().tolist())
    return get_genres()

# Load Filip's data
genre_counts = pd.read_csv('genre_counts_processed.csv')
genre_year_counts = pd.read_csv('assets/genre_year_counts.csv')

# --- UNIFIED COLOR MAPPING ---
import plotly.colors as pcolors

# Calculate global popularity for consistent color assignment
# We use the same filter as draw_genre_trends (1950-2030)
_df_colors = genre_year_counts[(genre_year_counts['year'] >= 1950) & (genre_year_counts['year'] <= 2030)]
# Popularity order
_global_top_genres = _df_colors.groupby('playlist_genre')['count'].sum().sort_values(ascending=False).index.tolist()

GENRE_COLOR_MAP = {}
# Cycle Plotly colors to ensure high contrast for top genres, then repeat
_colors = pcolors.qualitative.Plotly * 5 

for _i, _genre in enumerate(_global_top_genres):
    GENRE_COLOR_MAP[_genre] = _colors[_i % len(_colors)]

# Ensure all 35 genres have a color
for _genre in get_genres():
    if _genre not in GENRE_COLOR_MAP:
        # Assign a hash-based color or neutral for anything missing from popularity data
        GENRE_COLOR_MAP[_genre] = '#888888' 

# This draws the actual plots 
# it takes the selected topbar and produces the figure accordingly
# adjusts the figure based on the sidebar selection as well
# In figures.py

def draw_genre_trends(decade_center=None):
    # Filter years 1950-2030
    df = genre_year_counts[(genre_year_counts['year'] >= 1950) & (genre_year_counts['year'] <= 2030)].copy()
    
    # Sort genres by total count to stabilize legend order if needed
    top_genres = df.groupby('playlist_genre')['count'].sum().sort_values(ascending=False).index
    
    fig = px.line(df, x='year', y='count', color='playlist_genre', 
                  category_orders={"playlist_genre": top_genres},
                  title="Genre Popularity Over Time (1950-2030)",
                  color_discrete_map=GENRE_COLOR_MAP)
    
    fig.update_layout(
         paper_bgcolor="rgba(0,0,0,0.6)", # Semi-transparent background
         plot_bgcolor="rgba(0,0,0,0)",
         font=dict(color="white"),
         xaxis=dict(showgrid=False),
         yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
         autosize=True,
         margin=dict(l=40, r=40, t=50, b=40)
    )
    
    # Add vertical marker for current decade if provided
    if decade_center:
        decade_centers = {
            '50s': 1955, '60s': 1965, '70s': 1975, '80s': 1985, '90s': 1995, '00s': 2005, '10s': 2015, '20s': 2025
        }
        center_year = decade_centers.get(decade_center)
        if center_year:
             fig.add_vline(x=center_year, line_width=2, line_dash="dash", line_color="white")
             
    style_fig(fig)
    return fig

def draw_genre_trends_overlay(decade_center=None, selected_genre=None):
    # Specialized version for the honeycomb overlay
    # Transparent background, no title, minimized margins
    
    # Filter years 1950-2030
    df = genre_year_counts[(genre_year_counts['year'] >= 1950) & (genre_year_counts['year'] <= 2030)].copy()
    
    if selected_genre:
        df = df[df['playlist_genre'] == selected_genre]
        # Ensure color consistency
        # We need to map genre to color if we want specific colors
        # But Plotly handles it if we map 'playlist_genre' to color
        
    top_genres = df.groupby('playlist_genre')['count'].sum().sort_values(ascending=False).index
    
    fig = px.line(df, x='year', y='count', color='playlist_genre', 
                  category_orders={"playlist_genre": top_genres},
                  color_discrete_map=GENRE_COLOR_MAP) # No title
    
    fig.update_layout(
         paper_bgcolor="rgba(0,0,0,0)", 
         plot_bgcolor="rgba(0,0,0,0)",
         font=dict(color="white"),
         xaxis=dict(
             showgrid=False, 
             showticklabels=True,
             tickfont=dict(size=10)
         ),
         yaxis=dict(
             showgrid=True, 
             gridcolor="rgba(255,255,255,0.1)",
             showticklabels=False # Hide y-axis labels to save width/clutter
         ),
         showlegend=False, # Hide legend in small cells
         margin=dict(l=10, r=10, t=5, b=20)
    )
    
    if decade_center:
        decade_centers = {
            '50s': 1955, '60s': 1965, '70s': 1975, '80s': 1985, '90s': 1995, '00s': 2005, '10s': 2015, '20s': 2025
        }
        center_year = decade_centers.get(decade_center)
        if center_year:
             fig.add_vline(x=center_year, line_width=2, line_dash="dash", line_color="#4D96FF") # Electric Blue marker
             
    return fig

# Update the signature to accept optional song arguments
def draw_figure(topbar_tab, decades_list, current_decade, song1=None, song2=None, selected_genres=None, show_genre1=False, show_genre2=False):
    decade_colors = {
        '50s': 'red',
        '60s': 'orange',
        '70s': 'yellow',
        '80s': 'green',
        '90s': 'blue',
        '00s': 'indigo',
        '10s': 'violet',
        '20s': 'purple'
    }
    decade_rgb = {
        '50s': (255, 0, 0),
        '60s': (255, 165, 0),
        '70s': (255, 255, 0),
        '80s': (0, 128, 0),
        '90s': (0, 0, 255),
        '00s': (75, 0, 130),
        '10s': (238, 130, 238),
        '20s': (128, 0, 128)
    }
    if topbar_tab == "topic-3":
        # Pass the songs down to draw_spider
        # If song1/song2 are None (which shouldn't happen with the fix above), 
        # draw_spider will use its defaults (which might still crash, but we fixed the input).
        
        if song1 and song2:
             figure = draw_spider(current_decade, song1, song2, show_genre1, show_genre2)
        else:
             # Fallback if called without songs (e.g. initial load if logic is slightly off)
             # This is a safety measure
             figure = draw_spider(current_decade) 
             
    elif topbar_tab == "topic-1":
        # --- Analysis 1 Tab ---
        # Note: We now control content via callback in app.py to handle genre filtering
        # But draw_pane calls this to get initial content.
        
        genes = get_genres() 
        
        figure = html.Div(
            style={
                "display": "flex", 
                "flexDirection": "row", 
                "width": "100%", 
                "height": "100%", 
                "padding": "20px 20px 80px 20px", # Added bottom padding for timeline controls
                "boxSizing": "border-box",
                # "gap": "20px" # REMOVE GAP
            }, 
            children=[
                 # Left Column: Spider Graphs
                 html.Div(
                     style={"flex": "1", "display": "flex", "flexDirection": "column", "minWidth": "0", "height": "100%", "overflow": "hidden", "position": "relative"},
                     children=[
                         # Genre Dropdown
                         html.Div(
                             style={'marginBottom': '10px'},
                             children=[
                                 dcc.Dropdown(
                                     id='genre-dropdown',
                                     options=[{'label': g.title(), 'value': g} for g in get_genres()],
                                     multi=True,
                                     value=selected_genres if selected_genres is not None else ([get_genres_for_decade(current_decade)[0]] if get_genres_for_decade(current_decade) else None), # Use persisted selection or default
                                     placeholder="Select Genres...",
                                     style={'color': 'black'}
                                 )
                             ]
                         ),
                         # Legend for Spider Graph Initials
                         html.Div(
                             id="analysis1-legend-trigger", # Added ID for click interaction
                             className="legend-container",
                             n_clicks=0,
                             # E: Energy, D: Danceability, V: Valence, A: Acousticness, I: Instrumentalness
                             children=[
                                 html.Div([
                                     html.Span("E: Energy", style={"marginRight": "10px", "color": "#FF6B6B", "fontWeight": "bold"}),
                                     html.Span("D: Danceability", style={"marginRight": "10px", "color": "#DA77F2", "fontWeight": "bold"}),
                                     html.Span("V: Valence", style={"marginRight": "10px", "color": "#FFD93D", "fontWeight": "bold"}),
                                     html.Span("A: Acousticness", style={"marginRight": "10px", "color": "#6BCB77", "fontWeight": "bold"}),
                                     html.Span("I: Instrumentalness", style={"color": "#4D96FF", "fontWeight": "bold"})
                                 ]),
                                 # Tooltip Content
                                 html.Div([
                                     html.Div([
                                         # Column 1
                                         html.Div([
                                             html.Div([html.Strong("Energy", style={"color": "#FF6B6B", "display": "block", "marginBottom": "2px", "fontSize": "1.1em"}), html.Span("Intensity, speed, and noise level", style={"color": "white", "fontSize": "0.9em"})], style={"marginBottom": "12px"}),
                                             html.Div([html.Strong("Danceability", style={"color": "#DA77F2", "display": "block", "marginBottom": "2px", "fontSize": "1.1em"}), html.Span("Rhythm stability and beat strength", style={"color": "white", "fontSize": "0.9em"})])
                                         ], style={"flex": "1", "padding": "0 10px"}),
                                         
                                         # Column 2
                                         html.Div([
                                             html.Div([html.Strong("Valence", style={"color": "#FFD93D", "display": "block", "marginBottom": "2px", "fontSize": "1.1em"}), html.Span("Musical positiveness (Happy vs Sad)", style={"color": "white", "fontSize": "0.9em"})], style={"marginBottom": "12px"}),
                                             html.Div([html.Strong("Acousticness", style={"color": "#6BCB77", "display": "block", "marginBottom": "2px", "fontSize": "1.1em"}), html.Span("Presence of acoustic instruments", style={"color": "white", "fontSize": "0.9em"})])
                                         ], style={"flex": "1", "padding": "0 10px", "borderLeft": "1px solid rgba(255,255,255,0.1)", "borderRight": "1px solid rgba(255,255,255,0.1)"}),
                                         
                                         # Column 3
                                         html.Div([
                                             html.Div([html.Strong("Instrumentalness", style={"color": "#4D96FF", "display": "block", "marginBottom": "2px", "fontSize": "1.1em"}), html.Span("Likelihood of no vocal content", style={"color": "white", "fontSize": "0.9em"})])
                                         ], style={"flex": "1", "padding": "0 10px"})
                                     ], style={"display": "flex", "flexDirection": "row", "justifyContent": "space-between", "textAlign": "left", "paddingTop": "5px"})
                                 ], id="analysis1-legend-content", className="legend-tooltip") # Added ID for callback target
                             ],
                             style={
                                 "textAlign": "center", 
                                 "fontSize": "11px", 
                                 "marginBottom": "5px",
                                 "fontFamily": "sans-serif",
                                 "backgroundColor": "rgba(0,0,0,0.3)", # Added bg for better contrast
                                 "padding": "5px",
                                 "borderRadius": "5px",
                                 "cursor": "pointer" # Changed to pointer to indicate clickability
                             }
                         ),
                         # Grid for Spider Graphs (container) - Top 66%
                         html.Div(
                             style={"flex": "2", "position": "relative", "minHeight": "0", "display": "flex", "flexDirection": "column"}, 
                             children=[
                                 html.Div(
                                     id='spider-graphs-container',
                                     className='honeycomb-grid',
                                     style={
                                         "flex": "1",
                                         "overflowY": "auto", 
                                         "overflowX": "hidden",
                                         "width": "100%",
                                         "alignContent": "flex-start", # Changed from center to avoid top clipping
                                         "paddingTop": "40px", # Compensate for negative margins
                                         "paddingBottom": "20px"
                                     },
                                     children=[] 
                                 ),

                             ]
                         ),
                         
                         # Bottom 33% - Genre Trends Overlay
                         html.Div(
                            style={"flex": "1", "minHeight": "0", "borderTop": "1px solid rgba(255,255,255,0.1)", "marginTop": "10px"},
                            children=[
                                dcc.Graph(
                                    figure=draw_genre_trends_overlay(current_decade),
                                    style={"height": "100%", "width": "100%"},
                                    config={'displayModeBar': False}
                                )
                            ]
                         )
                     ]
                 ),
                 
                 # Right Column: Area Plots
                 html.Div(
                     style={
                         "flex": "1", 
                         "display": "flex", 
                         "flexDirection": "column", 
                         "minWidth": "0",
                         "border": "2px solid rgba(60, 65, 90, 0.7)", # Border matching honeycomb tone
                         "borderRadius": "10px",
                         "overflow": "hidden"
                     },
                     children=[
                         # Area Plots Graph
                         html.Div(
                             dcc.Graph(
                                 id='analysis1-area', 
                                 figure=draw_area_plots(decades_list, current_decade, ["Energy", "Tempo", "Danceability", "Loudness", "Liveness", "Valence", "Speechiness", "Acousticness", "Instrumentalness"], bin_size="1 year"),
                                 style={"height": "100%", "width": "100%"}
                             ),
                             style={"flex": "1", "minHeight": "0"} 
                         )
                     ]
                 )
            ]
        )
    elif topbar_tab == "topic-4":  # Filip's changes tab
        # Use a flex column layout to strictly control vertical space
        figure = html.Div(
            style={
                "display": "flex",
                "flexDirection": "column",
                "height": "100%",
                "width": "100%",
                "padding": "20px",
                "boxSizing": "border-box",
                "gap": "10px"
            },
            children=[
                 # Top Section: Genre Trends (40%)
                 html.Div(
                     dcc.Graph(
                         figure=draw_genre_trends(current_decade), 
                         config={'responsive': True, 'displayModeBar': False},
                         style={"height": "100%", "width": "100%"}
                     ),
                     style={"flex": "4", "minHeight": "0", "width": "100%"}
                 ),
                 
                 # Bottom Section: Changes & Card (60%)
                 html.Div(
                     style={"display": "flex", "flexDirection": "row", "gap": "20px", "flex": "6", "minHeight": "0", "width": "100%"},
                     children=[
                         # Left: Asc/Desc Changes (Two graphs stacked)
                         html.Div(
                            children=[
                                html.Div(
                                    dcc.Graph(
                                        figure=draw_change(current_decade, genre_counts, "desc"),
                                        config={'responsive': True, 'displayModeBar': False},
                                        style={"height": "100%", "width": "100%"}
                                    ),
                                    style={"flex": "1", "minHeight": "0"}
                                ),
                                html.Div(
                                    dcc.Graph(
                                        figure=draw_change(current_decade, genre_counts, "asc"),
                                        config={'responsive': True, 'displayModeBar': False},
                                        style={"height": "100%", "width": "100%"}
                                    ),
                                    style={"flex": "1", "minHeight": "0"}
                                )
                            ],
                            style={"flex": "1", "display": "flex", "flexDirection": "column", "gap": "10px", "height": "100%"}
                         ),
                         # Right: Decade Card
                         html.Div(
                             create_decade_card(current_decade),
                             style={"flex": "1", "overflowY": "auto"}
                         )
                     ]
                 )
            ]
        )
    else:
        placeholder_figure = f"This is where {topbar_tab} / {current_decade} figure will be drawn"
        figure = placeholder_figure

    return figure


# New functions for Prototype Dashboard
def draw_spider_analysis1(decades_list, current_decade, selected_genres=None, override_color=None):
    decade_rgb = {
        '50s': (255, 0, 0),
        '60s': (255, 165, 0),
        '70s': (255, 255, 0),
        '80s': (0, 128, 0),
        '90s': (0, 0, 255),
        '00s': (75, 0, 130),
        '10s': (238, 130, 238),
        '20s': (128, 0, 128)
    }
    categories = ["Energy", "Danceability", "Valence", "Acousticness", "Instrumentalness"]
    # Use initials for labels to avoid cutoff
    category_labels = [c[0] for c in categories]
    label_colors = ["#FF6B6B", "#DA77F2", "#FFD93D", "#6BCB77", "#4D96FF"] # Colors matching legend
    
    fig = go.Figure()
    
    # Filter by genre if provided
    base_data = spider_data.copy()
    if selected_genres:
        if 'playlist_genre' in base_data.columns:
            base_data = base_data[base_data['playlist_genre'].isin(selected_genres)]
    
    import plotly.colors as pcolors

    for decade in decades_list:
        filtered_data = base_data[base_data['decade'] == decade]
        
        if override_color:
            line_color_str = override_color
            # Calculate fill color (semi-transparent version of override_color)
            if override_color.startswith('#'):
                rgb_tuple = pcolors.hex_to_rgb(override_color)
                fill_color_str = f'rgba({rgb_tuple[0]}, {rgb_tuple[1]}, {rgb_tuple[2]}, 0.2)'
            elif override_color.startswith('rgb'):
                # Assumes format "rgb(r, g, b)"
                vals = override_color[4:-1].split(',')
                fill_color_str = f'rgba({vals[0]},{vals[1]},{vals[2]},0.2)'
            else:
                fill_color_str = override_color # Fallback
        else:
            rgb = decade_rgb.get(decade, (128, 128, 128))
            line_color_str = f'rgb({rgb[0]}, {rgb[1]}, {rgb[2]})'
            fill_color_str = f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.2)' # 20% opacity
        
        if filtered_data.empty:
            avg_values = [None] * len(categories)
        else:
            avg_values = [filtered_data[cat].mean() for cat in categories]
            
        fig.add_trace(go.Scatterpolar(
            r=avg_values,
            theta=category_labels,
            fill='toself' if not filtered_data.empty else None,
            name=f"Average {decade}",
            line=dict(color=line_color_str),
            fillcolor=fill_color_str
        ))
        
    # Add colored labels manually using a "text" trace to override default monochrome axis labels
    # We place markers at r=1.45 (strictly outside) to act as labels
    fig.add_trace(go.Scatterpolar(
        r=[1.45] * 5, # Move further out to avoid overlap
        theta=category_labels,
        mode="text",
        text=category_labels,
        textfont=dict(color=label_colors, size=14, family="Arial Black"), # Bold colored font
        hoverinfo="skip",
        showlegend=False,
        cliponaxis=False # Allow drawing outside margin if needed
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 1.6], # Increased range to accommodate labels
                gridcolor="rgba(255, 255, 255, 0.2)", # Less intense grid
                linecolor="rgba(255, 255, 255, 0.2)"
            ), 
            bgcolor="rgba(0,0,0,0)",
            gridshape='linear',
            angularaxis=dict(
                rotation=90,  # Ensure first vertex (Energy) is at the top (12 o'clock)
                direction="clockwise",
                showticklabels=False, # Hide default labels
                gridcolor="rgba(255, 255, 255, 0.2)", # Less intense angular grid
                linecolor="rgba(255, 255, 255, 0.2)"
            )
        ),
        showlegend=False,
        title=dict(text=f"{current_decade} Average" if not selected_genres else "", font=dict(color="white")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white", size=10),
        autosize=True,
        margin=dict(l=30, r=30, t=40, b=30) # Adjusted for Hexagon
    )
    return fig

def draw_feature_explanations():
    features = [
        ("Acousticness", "Confidence measure of whether the track is acoustic."),
        ("Danceability", "How suitable a track is for dancing based on tempo, rhythm stability, beat strength, and overall regularity."),
        ("Energy", "Perceptual measure of intensity and activity. High energy tracks feel fast, loud, and noisy."),
        ("Instrumentalness", "Predicts whether a track contains no vocals."),
        ("Liveness", "Detects the presence of an audience in the recording."),
        ("Loudness", "The overall loudness of a track in decibels (dB)."),
        ("Speechiness", "Detects the presence of spoken words in a track."),
        ("Tempo", "The overall estimated tempo of a track in beats per minute (BPM)."),
        ("Valence", "Musical positiveness. High valence tracks sound more positive (happy, cheerful, euphoric).")
    ]
    
    return html.Div(
        style={
            "display": "grid",
            "gridTemplateColumns": "repeat(auto-fill, minmax(280px, 1fr))", # Responsive grid
            "gap": "10px", # Tighter gap
            "padding": "15px",
            "overflowY": "auto",
            "height": "100%",
            "color": "white",
            "fontFamily": "'Segoe UI', sans-serif"
        },
        children=[
            html.Div(
                className="feature-card",
                children=[
                    html.H4(
                        children=[
                            html.Span(name),
                            html.Span("+", className="toggle-icon")
                        ]
                    ),
                    html.P(desc)
                ]
            ) for name, desc in features
        ]
    )

def draw_area_plots(decades_list, current_decade, features=["Energy", "Danceability", "Valence", "Acousticness", "Instrumentalness"], opacity=1.0, bin_size=None, selected_genres=None, highlighted_genre=None):
    # Use Plotly qualitative colors directly for genres
    import plotly.colors as pcolors
    import plotly.subplots as sp

    # If no selected_genres specifically, default to list of available genres or just don't filter immediately
    # If no genres are selected, we might want to default to ALL or first few?
    # Logic in app.py seems to pass valid list or None.
    # If None, let's treat it as all genres (or handle gracefully)
    
    base_data = spider_data.copy()
    
    # Genres to process
    if selected_genres:
        loop_genres = selected_genres
        # Filter base data to only relevant genres for efficiency
        if 'playlist_genre' in base_data.columns:
            base_data = base_data[base_data['playlist_genre'].isin(selected_genres)]
    else:
        # If None, use all genres found in data (this might be heavy, but fallback)
        loop_genres = get_genres()
        
    available_features = [c for c in features if c in spider_data.columns]
    
    grid_rows = len(available_features)
    grid_cols = 1
    
    fig_line = sp.make_subplots(rows=grid_rows, cols=grid_cols, subplot_titles=available_features, vertical_spacing=0.06, shared_xaxes=True)

    # DO NOT filter by decades - always show full timeline data
    # The line plots should display all data across all decades
        
    # Standardize time column: 'year'
    # The previous logic had a complex binning, but user requested fixed "year" binning.
    # We can just use the 'year' column if available, or extract year from release date.
    if 'year' not in base_data.columns and 'track_album_release_date' in base_data.columns:
        base_data['year'] = pd.to_datetime(base_data['track_album_release_date'], errors='coerce').dt.year

    # Loop through genres to create a trace for each genre line
    # (Removed local colors_cycle, using global GENRE_COLOR_MAP)
    
    # Sort loop_genres so that highlighted_genre is last (drawn on top)
    if highlighted_genre and highlighted_genre in loop_genres:
        loop_genres = [g for g in loop_genres if g != highlighted_genre] + [highlighted_genre]
    
    for genre in loop_genres: 
        
        genre_df = base_data[base_data['playlist_genre'] == genre].copy()
        
        if genre_df.empty:
            continue
            
        color = GENRE_COLOR_MAP.get(genre, '#888888')
        
        # Determine style based on highlight
        line_width = 2
        line_opacity = 0.6 if highlighted_genre else 1.0 # Dim others if one is highlighted
        
        if highlighted_genre:
             if genre == highlighted_genre:
                 line_width = 5 # Make thicker
                 line_opacity = 1.0
             else:
                 line_opacity = 0.2 # Fade out non-highlighted significantly
        
        # Group by year for this genre
        # We calculate the mean of each feature per year
        grouped = genre_df.groupby('year')[available_features].mean().reset_index()
        grouped = grouped.sort_values('year')
        
        # Add trace for each feature
        for i, feature in enumerate(available_features):
            row = i + 1
            col = 1
            
            # Add trace
            fig_line.add_trace(
                go.Scatter(
                    x=grouped['year'], 
                    y=grouped[feature], 
                    mode='lines', 
                    name=genre.title(), # Name appears in legend
                    line=dict(color=color, width=line_width),
                    opacity=line_opacity,
                    legendgroup=genre, # Group legends so toggling one toggles all for that genre
                    showlegend=(i == 0) # Only show legend for first subplot to avoid duplicates
                ),
                row=row, col=col
            )

    # Cleaning axes
    # Fix x-axis range to cover the entire dataset period (e.g., 1950-2030) regardless of selected genre data
    for i in range(len(available_features)):
        fig_line.update_xaxes(range=[1950, 2030], row=i+1, col=1, title_text='') # Clean x-labels and fix range
        fig_line.update_yaxes(range=[0, 1], row=i+1, col=1) # Fix y-axis range to [0, 1]
    
    # Add shared X-axis title at bottom
    fig_line.update_xaxes(title_text='Year', row=len(available_features), col=1)
    
    fig_line.update_layout(
        height=None, 
        width=None, 
        showlegend=True, # We want legend now for genres
        title_text="Audio Features Evolution by Genre", 
        autosize=True, 
        margin=dict(t=50, b=30, l=30, r=30),
        title_font=dict(size=14, color="white"),
        legend=dict(orientation="h", y=1.02, xanchor="right", x=1, font=dict(color="white")), # Horizontal legend top right
        paper_bgcolor="rgba(30, 30, 40, 0.7)", # Match Spider Graph Background
        plot_bgcolor="rgba(30, 30, 40, 0.7)",
        font=dict(color="white")
    )
    
    # Update axes to match dark theme
    fig_line.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.1)")
    fig_line.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.1)")
    
    # Decrease subplot title font size
    fig_line.update_annotations(font=dict(size=10))
    
    return fig_line


# New function for timeline
def draw_timeline(decade, bin_size="5 months"):
    filtered_data = spider_data[spider_data['decade'] == decade]
    
    if 'track_album_release_date' in filtered_data.columns:
        dates = pd.to_datetime(filtered_data['track_album_release_date'], errors='coerce').dropna()
    else:
        dates = pd.Series()  # empty
    
    if dates.empty:
        # fallback
        fig = go.Figure()
        fig.add_trace(go.Bar(x=[], y=[]))
        fig.update_layout(
            xaxis=dict(title="Time Bins", tickfont=dict(color='white')),
            yaxis=dict(title="Number of Songs", tickfont=dict(color='white')),
            height=200,
            autosize=True,
            margin=dict(t=10, b=40, l=40, r=20),
            paper_bgcolor="rgba(0,0,0,0.5)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        return fig
    
    if bin_size == "No bins":
        total_songs = len(dates)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["Total"],
            y=[total_songs],
            marker_color='white'
        ))
        fig.update_layout(
            xaxis=dict(title="", tickfont=dict(color='white')),
            yaxis=dict(title="Number of Songs", tickfont=dict(color='white')),
            height=200,
            autosize=True,
            margin=dict(t=10, b=40, l=40, r=20),
            paper_bgcolor="rgba(0,0,0,0.5)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        return fig
    
    min_date = dates.min()
    max_date = dates.max()
    
    # Set freq based on bin_size
    if bin_size == "No bins":
        freq = 'YS'
        offset = pd.DateOffset(years=1)
        label_suffix = pd.DateOffset(years=1, days=-1)
    elif bin_size == "1 week":
        freq = 'W'
        offset = pd.DateOffset(weeks=1)
        label_suffix = pd.DateOffset(weeks=1, days=-1)
    elif bin_size == "1 month":
        freq = 'MS'
        offset = pd.DateOffset(months=1)
        label_suffix = pd.DateOffset(months=1, days=-1)
    elif bin_size == "5 months":
        freq = '5MS'
        offset = pd.DateOffset(months=5)
        label_suffix = pd.DateOffset(months=5, days=-1)
    else:
        freq = '5MS'  # default
        offset = pd.DateOffset(months=5)
        label_suffix = pd.DateOffset(months=5, days=-1)
    
    # Create bins
    bins = pd.date_range(start=min_date, end=max_date + offset, freq=freq)
    
    if len(bins) < 2:
        bins = pd.date_range(start=min_date, periods=2, freq=freq)
    
    # Bin the dates
    binned = pd.cut(dates, bins=bins, right=False, labels=[f"{b.strftime('%Y-%m-%d')}-{ (b + label_suffix).strftime('%Y-%m-%d')}" for b in bins[:-1]])
    
    # Count per bin
    counts = binned.value_counts().sort_index()
    
    # For plotting, x as the bin labels, y as counts
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=counts.index,
        y=counts.values,
        marker_color='white'
    ))
    
    fig.update_layout(
        xaxis=dict(
            title=f"{bin_size} Bins",
            tickfont=dict(color='white')
        ),
        yaxis=dict(
            title="Number of Songs",
            tickfont=dict(color='white')
        ),
        height=200,  # adjust height for better visibility
        autosize=False,
        margin=dict(t=10, b=40, l=40, r=20),
        paper_bgcolor="rgba(0,0,0,0.5)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )
    return fig


# Updated draw_spider to use actual data
def draw_spider(sidebar_tab, song1="6dOtVTDdiauQNBQEDOtlAB", song2="1d7Ptw3qYcfpdLNL5REhtJ", show_genre1=False, show_genre2=False):
    # Define categories for the spider graph
    categories = ["Energy", "Danceability", "Valence", "Acousticness", "Instrumentalness"]

    # Filter data for the selected decade
    filtered_data = spider_data[spider_data['decade'] == sidebar_tab]

    # --------------------------------------------------------------
    # SAFETY CHECK to make sure callbacks were fast enough
    song1_row = filtered_data[filtered_data['track_id'] == song1]
    song2_row = filtered_data[filtered_data['track_id'] == song2]
    
    if song1_row.empty or song2_row.empty:
        # Return an empty figure or a message saying "Loading..."
        # This prevents the crash while waiting for the dropdowns to update
        return go.Figure()
    # --------------------------------------------------------------

    # Get values for the two songs
    song1_values = song1_row[categories].values.flatten()
    song1_name = song1_row["track_name"].values.flatten().item()
    song1_genre = song1_row["playlist_genre"].values.flatten().item() if "playlist_genre" in song1_row.columns else "Unknown"
    
    song2_values = song2_row[categories].values.flatten()
    song2_name = song2_row["track_name"].values.flatten().item()
    song2_genre = song2_row["playlist_genre"].values.flatten().item() if "playlist_genre" in song2_row.columns else "Unknown"

    # Create the spider graph
    fig = go.Figure()

    # Add song1 data
    fig.add_trace(go.Scatterpolar(
        r=song1_values,
        theta=categories,
        fill='toself',
        name=f"{song1_name} ({song1_genre})", # Show genre in legend
        line_color='#636EFA' # Plotly Blue
    ))

    # Add song2 data
    fig.add_trace(go.Scatterpolar(
        r=song2_values,
        theta=categories,
        fill='toself',
        name=f"{song2_name} ({song2_genre})",
        line_color='#EF553B' # Plotly Red
    ))
    
    # Add Genre 1 Average if requested
    if show_genre1:
        genre1_data = filtered_data[filtered_data['playlist_genre'] == song1_genre]
        if not genre1_data.empty:
            genre1_avg = genre1_data[categories].mean().tolist()
            fig.add_trace(go.Scatterpolar(
                r=genre1_avg,
                theta=categories,
                name=f"Avg {song1_genre} ({sidebar_tab})",
                line=dict(dash='dash', color='#636EFA'), # Dashed blue
                fill=None
            ))
            
    # Add Genre 2 Average if requested
    if show_genre2:
        genre2_data = filtered_data[filtered_data['playlist_genre'] == song2_genre]
        if not genre2_data.empty:
            genre2_avg = genre2_data[categories].mean().tolist()
            fig.add_trace(go.Scatterpolar(
                r=genre2_avg,
                theta=categories,
                name=f"Avg {song2_genre} ({sidebar_tab})",
                line=dict(dash='dash', color='#EF553B'), # Dashed red
                fill=None
            ))

    # Update layout with transparent background and larger plot
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 1],
                gridcolor="rgba(255, 255, 255, 0.1)", # Less intense white grid
                linecolor="rgba(255, 255, 255, 0.1)"  # Less intense axis lines
            ),
            angularaxis=dict(
                gridcolor="rgba(255, 255, 255, 0.1)", # Less intense angular grid
                linecolor="rgba(255, 255, 255, 0.1)"
            ),
            bgcolor="rgba(30,30,40,0.7)"  # Dark theme background like analysis 1
        ),
        showlegend=True,
        title=dict(text=f"Comparison: {song1_name} vs {song2_name}", font=dict(color="white", size=14)),
        paper_bgcolor="rgba(0,0,0,0)",  # Transparent canvas background
        plot_bgcolor="rgba(0,0,0,0)",  # Transparent plot area
        font=dict(color="white"),  # White text for visibility
        autosize=True, # Allow autosize but margin controls actual size within container
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="white")
        )
    )

    # Return the figure object directly
    return fig

def get_songs_for_decade(sidebar_tab):
    #Get unique song names and IDs for a given decade
    filtered_data = spider_data[spider_data['decade'] == sidebar_tab].copy()
    filtered_data["track_id"] = filtered_data["track_id"].str.split(":").str[-1]
    # (Assuming your column is named 'track_id')
    songs = filtered_data[["track_name", "track_id"]].drop_duplicates().values.tolist()
    
    return sorted(songs)
#FILIPS PLOTS=============================================================================================D
#paper esthetic
PAPER_BG = 'rgba(30, 30, 40, 0.7)'  # Dark theme background
INK_COLOR = 'white' # White text
FONT_FAMILY = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"

# Custom visual theme function for Plotly
def style_fig(fig):
    fig.update_layout(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor="rgba(0,0,0,0)", # Transparent plot area
        font=dict(family=FONT_FAMILY, color=INK_COLOR),
        title_font=dict(size=20, family=FONT_FAMILY),
        margin=dict(t=50, l=20, r=20, b=20),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.1)")
    )
    return fig
#my data
genre_counts = pd.read_csv('genre_counts_processed.csv')
DECADE_INFO = {
    '50s': "The decade that gave birth to rock 'n' roll. Elvis Presley, Chuck Berry, and Little Richard electrified teenagers while their parents clutched their pearls. Doo-wop harmonies filled street corners, and the electric guitar became the sound of rebellion. Music wasn't just entertainment anymore: it was identity.",
    
    '60s': "The British Invasion landed when The Beatles conquered America, and nothing was ever the same. Motown gave us timeless soul, Dylan went electric and sparked outrage, and Woodstock became a generational moment. By decade's end, psychedelic rock had stretched what popular music could even be.",
    
    '70s': "A decade of extremes. Disco packed dance floors while punk burned them down. Led Zeppelin and Black Sabbath built the temple of heavy metal. Funk got political with Parliament and Sly Stone. The Walkman arrived in 1979, and suddenly music became portable and personal.",
    
    '80s': "Synthesizers and drum machines took over everything. MTV launched in 1981 and turned musicians into visual stars: Michael Jackson and Madonna ruled this new world. Hip-hop emerged from New York block parties to reshape popular culture. Hair metal, new wave, and synth-pop defined the excess.",
    
    '90s': "Nirvana's Nevermind killed hair metal overnight and grunge took over. Hip-hop went mainstream and split into coasts. Boy bands and Britney brought pop back. Napster arrived in 1999 and terrified the entire industry: file sharing was about to change everything.",
    
    '00s': "The digital revolution hit hard. The iPod and iTunes reshaped how we bought music while piracy ran rampant. Hip-hop dominated the charts. Emo and pop-punk gave angst a new voice. By decade's end, streaming was emerging and the album format was losing its grip.",
    
    '10s': "Streaming won. Spotify and Apple Music made everything available everywhere. EDM exploded into mainstream festivals. Latin pop went global with reggaeton and Despacito. SoundCloud launched careers. The lines between genres blurred as algorithms started shaping what we heard.",
    
    '20s': "TikTok became the new radio: 15 seconds can make a song explode or resurface a forgotten classic. Hyperpop pushed boundaries while bedroom producers competed with major labels. AI entered the conversation. Vinyl sales somehow keep climbing as listeners crave something physical again."
}

#plot for genre popularity changes-----------------
def draw_change(decade, data, direction='desc'):#the parameter should be a column of changes in popularity in an aggregate dataframe, direction says whether to show positive or negative growth
    delta = data[data['decade'] == decade]
    top5 = delta.sort_values('change', ascending=False).head(5)
    bottom5 = delta.sort_values('change', ascending=True).head(5)
    if direction == "desc":
        fig_change = px.bar(top5, x='playlist_genre',
                               y = 'change',#for now in absolute numbers, should change to percent
                               title='Biggest changes in genre popularity this decade',
                               color=top5['change'].apply(lambda x: 'positive' if x >= 0 else 'negative'),
                               color_discrete_map={'positive': '#2E8B57', 'negative': '#FA003F'})
    else:
               fig_change = px.bar(bottom5, x='playlist_genre',
                                   y = 'change',#for now in absolute numbers, should change to percent
                                   title='Biggest changes in genre popularity this decade',
                                   color=bottom5['change'].apply(lambda x: 'positive' if x >= 0 else 'negative'),
                                   color_discrete_map={'positive': '#2E8B57', 'negative': '#FA003F'})
        
        
                        
    style_fig(fig_change)
    return fig_change
#DECADE CARD
DECADE_COLORS = {
    '60s': '#D35400', # Burnt Orange
    '70s': '#8E44AD', # Purple
    '80s': '#2980B9', # Blue
    '90s': '#C0392B', # Red
    '00s': '#27AE60', # Green
    '10s': '#F1C40F', # Gold
    '20s': '#1ABC9C'  # Teal
}
def create_decade_card(decade):
    color = DECADE_COLORS.get(decade, '#333')
    text = DECADE_INFO.get(decade, "Description unavailable.")
    
    return html.Div(style={
        'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        'backgroundColor': 'rgba(30, 30, 40, 0.7)',
        'border': '1px solid rgba(255,255,255,0.1)',
        'maxWidth': '100%', # Allow it to fill the flex container
        'height': '100%',   # Ensure it fills height
        'display': 'flex',  # Use flex to manage internal scrolling
        'flexDirection': 'column'
    }, children=[
        
        # A. The Colored Header (The "Tab")
        html.Div(style={
            'backgroundColor': color,
            'height': '6px',
            'width': '100%',
            'flexShrink': 0
        }),
        
        # B. The Content Window
        html.Div(style={'padding': '25px', 'overflowY': 'auto', 'flex': '1'}, children=[
            # Title
            html.H2(f"The {decade}", style={
                'marginTop': '0', 
                'borderBottom': f'2px solid {color}',
                'paddingBottom': '10px',
                'color': 'white'
            }),
            
            # The Text Description
            html.P(text, style={'fontSize': '1.2em', 'lineHeight': '1.5', 'color': '#eee'}),
            
            # The Hallmark Image
            html.Div(style={
                'marginTop': '20px',
                'display': 'flex',
                'justifyContent': 'center',
            }, children=[
                html.Img(
                    src=f'assets/imgs/{decade}.jpg',
                    style={
                        'maxWidth': '100%',
                        'maxHeight': '250px',
                        'objectFit': 'contain'
                    }
                )
            ])
        ])
    ])