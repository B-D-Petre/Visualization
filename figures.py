import plotly.graph_objects as go
from dash import dcc, html
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.colors as pcolors

# Load preprocessed spider graph data
spider_csv_path = "assets/spider_graph_data.csv"
spider_data = pd.read_csv(spider_csv_path)

# --- GLOBAL DATA CLEANUP ---
# Ensure track_id is clean (remove 'spotify:track:' prefix if present)
if 'track_id' in spider_data.columns:
    spider_data['track_id'] = spider_data['track_id'].astype(str).str.split(':').str[-1]

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
try:
    genre_counts = pd.read_csv('genre_counts_processed.csv')
except FileNotFoundError:
    genre_counts = pd.DataFrame() # Fallback

try:
    genre_year_counts = pd.read_csv('assets/genre_year_counts.csv')
except FileNotFoundError:
    genre_year_counts = pd.DataFrame(columns=['year', 'playlist_genre', 'count'])


# --- UNIFIED COLOR MAPPING ---
# Calculate global popularity for consistent color assignment
# We use the same filter as draw_genre_trends (1950-2030)
if not genre_year_counts.empty:
    _df_colors = genre_year_counts[(genre_year_counts['year'] >= 1950) & (genre_year_counts['year'] <= 2030)]
    # Popularity order
    _global_top_genres = _df_colors.groupby('playlist_genre')['count'].sum().sort_values(ascending=False).index.tolist()
else:
    _global_top_genres = get_genres()

GENRE_COLOR_MAP = {}
# Cycle Plotly colors to ensure high contrast for top genres, then repeat
_colors = pcolors.qualitative.Plotly * 5 

for _i, _genre in enumerate(_global_top_genres):
    GENRE_COLOR_MAP[_genre] = _colors[_i % len(_colors)]

# Ensure all genres have a color
for _genre in get_genres():
    if _genre not in GENRE_COLOR_MAP:
        # Assign a hash-based color or neutral for anything missing from popularity data
        GENRE_COLOR_MAP[_genre] = '#888888' 


def draw_genre_trends(decade_center=None):
    if genre_year_counts.empty:
        return go.Figure()
        
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
    if genre_year_counts.empty:
        return go.Figure()

    # Specialized version for the honeycomb overlay
    # Transparent background, no title, minimized margins
    
    # Filter years 1950-2030
    df = genre_year_counts[(genre_year_counts['year'] >= 1950) & (genre_year_counts['year'] <= 2030)].copy()
    
    if selected_genre:
        df = df[df['playlist_genre'] == selected_genre]
        
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
    if topbar_tab == "topic-3":
        if song1 and song2:
             figure = draw_spider(current_decade, song1, song2, show_genre1, show_genre2)
        else:
             figure = draw_spider(current_decade) 
             
    elif topbar_tab == "topic-1":
        genes = get_genres() 
        figure = html.Div(
            style={
                "display": "flex", 
                "flexDirection": "row", 
                "width": "100%", 
                "height": "100%", 
                "padding": "20px 20px 80px 20px",
                "boxSizing": "border-box",
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
                                     value=selected_genres if selected_genres is not None else ([get_genres_for_decade(current_decade)[0]] if get_genres_for_decade(current_decade) else None),
                                     placeholder="Select Genres...",
                                     style={'color': 'black'}
                                 )
                             ]
                         ),
                         # Legend for Spider Graph Initials
                         html.Div(
                             id="analysis1-legend-trigger",
                             className="legend-container",
                             n_clicks=0,
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
                                 ], id="analysis1-legend-content", className="legend-tooltip")
                             ],
                             style={
                                 "textAlign": "center", 
                                 "fontSize": "11px", 
                                 "marginBottom": "5px",
                                 "fontFamily": "sans-serif",
                                 "backgroundColor": "rgba(0,0,0,0.3)", 
                                 "padding": "5px",
                                 "borderRadius": "5px",
                                 "cursor": "pointer"
                             }
                         ),
                         # Grid for Spider Graphs
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
                                         "alignContent": "flex-start",
                                         "paddingTop": "40px",
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
                         "border": "2px solid rgba(60, 65, 90, 0.7)", 
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
    category_labels = [c[0] for c in categories]
    label_colors = ["#FF6B6B", "#DA77F2", "#FFD93D", "#6BCB77", "#4D96FF"] 
    
    fig = go.Figure()
    
    base_data = spider_data.copy()
    if selected_genres:
        if 'playlist_genre' in base_data.columns:
            base_data = base_data[base_data['playlist_genre'].isin(selected_genres)]
    
    for decade in decades_list:
        filtered_data = base_data[base_data['decade'] == decade]
        
        if override_color:
            line_color_str = override_color
            if override_color.startswith('#'):
                rgb_tuple = pcolors.hex_to_rgb(override_color)
                fill_color_str = f'rgba({rgb_tuple[0]}, {rgb_tuple[1]}, {rgb_tuple[2]}, 0.2)'
            elif override_color.startswith('rgb'):
                vals = override_color[4:-1].split(',')
                fill_color_str = f'rgba({vals[0]},{vals[1]},{vals[2]},0.2)'
            else:
                fill_color_str = override_color
        else:
            rgb = decade_rgb.get(decade, (128, 128, 128))
            line_color_str = f'rgb({rgb[0]}, {rgb[1]}, {rgb[2]})'
            fill_color_str = f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.2)'
        
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
        
    fig.add_trace(go.Scatterpolar(
        r=[1.45] * 5,
        theta=category_labels,
        mode="text",
        text=category_labels,
        textfont=dict(color=label_colors, size=14, family="Arial Black"),
        hoverinfo="skip",
        showlegend=False,
        cliponaxis=False 
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 1.6], 
                gridcolor="rgba(255, 255, 255, 0.2)",
                linecolor="rgba(255, 255, 255, 0.2)"
            ), 
            bgcolor="rgba(0,0,0,0)",
            gridshape='linear',
            angularaxis=dict(
                rotation=90, 
                direction="clockwise",
                showticklabels=False, 
                gridcolor="rgba(255, 255, 255, 0.2)", 
                linecolor="rgba(255, 255, 255, 0.2)"
            )
        ),
        showlegend=False,
        title=dict(text=f"{current_decade} Average" if not selected_genres else "", font=dict(color="white")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white", size=10),
        autosize=True,
        margin=dict(l=30, r=30, t=40, b=30)
    )
    return fig

def draw_area_plots(decades_list, current_decade, features=["Energy", "Danceability", "Valence", "Acousticness", "Instrumentalness"], opacity=1.0, bin_size=None, selected_genres=None, highlighted_genre=None):
    import plotly.subplots as sp
    
    base_data = spider_data.copy()
    
    if selected_genres:
        loop_genres = selected_genres
        if 'playlist_genre' in base_data.columns:
            base_data = base_data[base_data['playlist_genre'].isin(selected_genres)]
    else:
        loop_genres = get_genres()
        
    available_features = [c for c in features if c in spider_data.columns]
    
    grid_rows = len(available_features)
    grid_cols = 1
    
    fig_line = sp.make_subplots(rows=grid_rows, cols=grid_cols, subplot_titles=available_features, vertical_spacing=0.06, shared_xaxes=True)

    if 'year' not in base_data.columns and 'track_album_release_date' in base_data.columns:
        base_data['year'] = pd.to_datetime(base_data['track_album_release_date'], errors='coerce').dt.year

    if highlighted_genre and highlighted_genre in loop_genres:
        loop_genres = [g for g in loop_genres if g != highlighted_genre] + [highlighted_genre]
    
    for genre in loop_genres: 
        genre_df = base_data[base_data['playlist_genre'] == genre].copy()
        if genre_df.empty:
            continue
            
        color = GENRE_COLOR_MAP.get(genre, '#888888')
        line_width = 2
        line_opacity = 0.6 if highlighted_genre else 1.0 
        
        if highlighted_genre:
             if genre == highlighted_genre:
                 line_width = 5 
                 line_opacity = 1.0
             else:
                 line_opacity = 0.2 
        
        grouped = genre_df.groupby('year')[available_features].mean().reset_index()
        grouped = grouped.sort_values('year')
        
        for i, feature in enumerate(available_features):
            row = i + 1
            col = 1
            
            fig_line.add_trace(
                go.Scatter(
                    x=grouped['year'], 
                    y=grouped[feature], 
                    mode='lines', 
                    name=genre.title(), 
                    line=dict(color=color, width=line_width),
                    opacity=line_opacity,
                    legendgroup=genre, 
                    showlegend=(i == 0) 
                ),
                row=row, col=col
            )

    for i in range(len(available_features)):
        fig_line.update_xaxes(range=[1950, 2030], row=i+1, col=1, title_text='') 
        fig_line.update_yaxes(range=[0, 1], row=i+1, col=1) 
    
    fig_line.update_xaxes(title_text='Year', row=len(available_features), col=1)
    
    fig_line.update_layout(
        height=None, 
        width=None, 
        showlegend=True, 
        title_text="Audio Features Evolution by Genre", 
        autosize=True, 
        margin=dict(t=50, b=30, l=30, r=30),
        title_font=dict(size=14, color="white"),
        legend=dict(orientation="h", y=1.02, xanchor="right", x=1, font=dict(color="white")), 
        paper_bgcolor="rgba(30, 30, 40, 0.7)", 
        plot_bgcolor="rgba(30, 30, 40, 0.7)",
        font=dict(color="white")
    )
    
    fig_line.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.1)")
    fig_line.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.1)")
    fig_line.update_annotations(font=dict(size=10))
    
    return fig_line

def draw_timeline(decade, bin_size="5 months"):
    filtered_data = spider_data[spider_data['decade'] == decade]
    
    if 'track_album_release_date' in filtered_data.columns:
        dates = pd.to_datetime(filtered_data['track_album_release_date'], errors='coerce').dropna()
    else:
        dates = pd.Series() 
    
    if dates.empty:
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
    if bin_size == "1 week":
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
        freq = '5MS' 
        offset = pd.DateOffset(months=5)
        label_suffix = pd.DateOffset(months=5, days=-1)
    
    # Create bins
    bins = pd.date_range(start=min_date, end=max_date + offset, freq=freq)
    
    if len(bins) < 2:
        bins = pd.date_range(start=min_date, periods=2, freq=freq)
    
    # Bin the dates
    binned = pd.cut(dates, bins=bins, right=False, labels=[f"{b.strftime('%Y-%m-%d')}-{ (b + label_suffix).strftime('%Y-%m-%d')}" for b in bins[:-1]])
    
    counts = binned.value_counts().sort_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=counts.index,
        y=counts.values,
        marker_color='white'
    ))
    
    fig.update_layout(
        xaxis=dict(title=f"{bin_size} Bins", tickfont=dict(color='white')),
        yaxis=dict(title="Number of Songs", tickfont=dict(color='white')),
        height=200, 
        autosize=False,
        margin=dict(t=10, b=40, l=40, r=20),
        paper_bgcolor="rgba(0,0,0,0.5)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )
    return fig

# Updated draw_spider to use actual data
def draw_spider(sidebar_tab, song1="6dOtVTDdiauQNBQEDOtlAB", song2="1d7Ptw3qYcfpdLNL5REhtJ", show_genre1=False, show_genre2=False):
    categories = ["Energy", "Danceability", "Valence", "Acousticness", "Instrumentalness"]
    filtered_data = spider_data[spider_data['decade'] == sidebar_tab]

    # Use default values if None (but defaults might not exist in new data!)
    # Better to default to first two songs in that decade if defaults fail
    if not song1 or song1 not in filtered_data['track_id'].values:
        if not filtered_data.empty:
            song1 = filtered_data['track_id'].iloc[0]
            
    if not song2 or song2 not in filtered_data['track_id'].values:
        if not filtered_data.empty and len(filtered_data) > 1:
            song2 = filtered_data['track_id'].iloc[1]
        elif not filtered_data.empty:
             song2 = song1

    song1_row = filtered_data[filtered_data['track_id'] == song1]
    song2_row = filtered_data[filtered_data['track_id'] == song2]
    
    if song1_row.empty or song2_row.empty:
        return go.Figure()

    song1_values = song1_row[categories].values.flatten()
    song1_name = song1_row["track_name"].values.flatten().item()
    song1_genre = song1_row["playlist_genre"].values.flatten().item() if "playlist_genre" in song1_row.columns else "Unknown"
    
    song2_values = song2_row[categories].values.flatten()
    song2_name = song2_row["track_name"].values.flatten().item()
    song2_genre = song2_row["playlist_genre"].values.flatten().item() if "playlist_genre" in song2_row.columns else "Unknown"

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=song1_values,
        theta=categories,
        fill='toself',
        name=f"{song1_name} ({song1_genre})",
        line_color='#636EFA'
    ))

    fig.add_trace(go.Scatterpolar(
        r=song2_values,
        theta=categories,
        fill='toself',
        name=f"{song2_name} ({song2_genre})",
        line_color='#EF553B' 
    ))
    
    if show_genre1:
        genre1_data = filtered_data[filtered_data['playlist_genre'] == song1_genre]
        if not genre1_data.empty:
            genre1_avg = genre1_data[categories].mean().tolist()
            fig.add_trace(go.Scatterpolar(
                r=genre1_avg,
                theta=categories,
                name=f"Avg {song1_genre} ({sidebar_tab})",
                line=dict(dash='dash', color='#636EFA'), 
                fill=None
            ))
            
    if show_genre2:
        genre2_data = filtered_data[filtered_data['playlist_genre'] == song2_genre]
        if not genre2_data.empty:
            genre2_avg = genre2_data[categories].mean().tolist()
            fig.add_trace(go.Scatterpolar(
                r=genre2_avg,
                theta=categories,
                name=f"Avg {song2_genre} ({sidebar_tab})",
                line=dict(dash='dash', color='#EF553B'),
                fill=None
            ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 1],
                gridcolor="rgba(255, 255, 255, 0.1)", 
                linecolor="rgba(255, 255, 255, 0.1)"  
            ),
            angularaxis=dict(
                gridcolor="rgba(255, 255, 255, 0.1)",
                linecolor="rgba(255, 255, 255, 0.1)"
            ),
            bgcolor="rgba(30,30,40,0.7)" 
        ),
        showlegend=True,
        title=dict(text=f"Comparison: {song1_name} vs {song2_name}", font=dict(color="white", size=14)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        autosize=True,
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

    return fig

def get_songs_for_decade(sidebar_tab):
    filtered_data = spider_data[spider_data['decade'] == sidebar_tab].copy()
    
    # We already cleaned track_id globally, so we can just grab it
    # We return Name (Label) and ID (Value)
    if 'track_name' in filtered_data.columns and 'track_id' in filtered_data.columns:
         songs = filtered_data[["track_name", "track_id"]].drop_duplicates().values.tolist()
    else:
         songs = []
    
    return sorted(songs)

#FILIPS PLOTS
# ... (Rest of Filip's code remains unchanged)
PAPER_BG = 'rgba(30, 30, 40, 0.7)'  
INK_COLOR = 'white'
FONT_FAMILY = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"

def style_fig(fig):
    fig.update_layout(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor="rgba(0,0,0,0)", 
        font=dict(family=FONT_FAMILY, color=INK_COLOR),
        title_font=dict(size=20, family=FONT_FAMILY),
        margin=dict(t=50, l=20, r=20, b=20),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.1)")
    )
    return fig

# ... (Decade Info/Card code follows)
DECADE_INFO = {
    '50s': "The decade that gave birth to rock 'n' roll...",
    '60s': "The British Invasion landed...",
    '70s': "A decade of extremes...",
    '80s': "Synthesizers and drum machines...",
    '90s': "Nirvana's Nevermind killed hair metal...",
    '00s': "The digital revolution hit hard...",
    '10s': "Streaming won...",
    '20s': "TikTok became the new radio..."
}

def draw_change(decade, data, direction='desc'):
    delta = data[data['decade'] == decade]
    top5 = delta.sort_values('change', ascending=False).head(5)
    bottom5 = delta.sort_values('change', ascending=True).head(5)
    if direction == "desc":
        fig_change = px.bar(top5, x='playlist_genre',
                               y = 'change',
                               title='Biggest changes in genre popularity this decade',
                               color=top5['change'].apply(lambda x: 'positive' if x >= 0 else 'negative'),
                               color_discrete_map={'positive': '#2E8B57', 'negative': '#FA003F'})
    else:
               fig_change = px.bar(bottom5, x='playlist_genre',
                                   y = 'change',
                                   title='Biggest changes in genre popularity this decade',
                                   color=bottom5['change'].apply(lambda x: 'positive' if x >= 0 else 'negative'),
                                   color_discrete_map={'positive': '#2E8B57', 'negative': '#FA003F'})
        
    style_fig(fig_change)
    return fig_change

DECADE_COLORS = {
    '60s': '#D35400',
    '70s': '#8E44AD',
    '80s': '#2980B9',
    '90s': '#C0392B',
    '00s': '#27AE60',
    '10s': '#F1C40F',
    '20s': '#1ABC9C' 
}
def create_decade_card(decade):
    color = DECADE_COLORS.get(decade, '#333')
    text = DECADE_INFO.get(decade, "Description unavailable.")
    
    return html.Div(style={
        'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        'backgroundColor': 'rgba(30, 30, 40, 0.7)',
        'border': '1px solid rgba(255,255,255,0.1)',
        'maxWidth': '100%', 
        'height': '100%', 
        'display': 'flex', 
        'flexDirection': 'column'
    }, children=[
        html.Div(style={
            'backgroundColor': color,
            'height': '6px',
            'width': '100%',
            'flexShrink': 0
        }),
        html.Div(style={'padding': '25px', 'overflowY': 'auto', 'flex': '1'}, children=[
            html.H2(f"The {decade}", style={
                'marginTop': '0', 
                'borderBottom': f'2px solid {color}',
                'paddingBottom': '10px',
                'color': 'white'
            }),
            html.P(text, style={'fontSize': '1.2em', 'lineHeight': '1.5', 'color': '#eee'}),
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