import plotly.graph_objects as go
from dash import dcc, html
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.colors as pcolors
import os

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

GENRE_COLOR_MAP = {
    'rock': '#636EFA',   # Blue
    'electronic': '#EF553B', # Red
    'pop': '#00CC96',    # Green
    'hip hop': '#AB63FA', # Purple
    'r&b': '#FFA15A',    # Orange
    'unknown': '#19D3F3', # Cyan
    'country': '#FF6692', # Pink
    'jazz': '#B6E880',   # Light Green
    'rap': '#FF97FF',    # Magenta
    'latin': '#FECB52',  # Yellow
    'classical': '#17BECF',
    'metal': '#7F7F7F',
    'reggae': '#BCBD22'
}

# Cycle Plotly colors types for any missing genres
_colors = pcolors.qualitative.Plotly * 5 

for _i, _genre in enumerate(_global_top_genres):
    # Only fill if not already hardcoded
    if _genre not in GENRE_COLOR_MAP and _genre.lower() not in GENRE_COLOR_MAP:
         GENRE_COLOR_MAP[_genre] = _colors[_i % len(_colors)]

# Ensure all genres have a color (fallback)
for _genre in get_genres():
    if _genre not in GENRE_COLOR_MAP:
         if _genre.lower() in GENRE_COLOR_MAP:
              GENRE_COLOR_MAP[_genre] = GENRE_COLOR_MAP[_genre.lower()]
         else:
              GENRE_COLOR_MAP[_genre] = '#888888' 


def draw_genre_trends(decade_center=None):
    if genre_year_counts.empty:
        return go.Figure()
        
    # Filter years 1950-2030
    df = genre_year_counts[(genre_year_counts['year'] >= 1950) & (genre_year_counts['year'] <= 2030)].copy()

    # Determine dominant genre for the selected decade if available
    dominant_genre = None
    if decade_center:
        # Determine strict year range for the decade
        start_year = int(decade_center.replace('s', '19')) if decade_center != '00s' and decade_center != '10s' and decade_center != '20s' else int('20' + decade_center[:-1] + '0')
        end_year = start_year + 9
        
        # Handle 19xx for 50-90, 20xx for 00-20
        # Correction for simplified parsing above which is risky
        if decade_center == '50s': start_year, end_year = 1950, 1959
        elif decade_center == '60s': start_year, end_year = 1960, 1969
        elif decade_center == '70s': start_year, end_year = 1970, 1979
        elif decade_center == '80s': start_year, end_year = 1980, 1989
        elif decade_center == '90s': start_year, end_year = 1990, 1999
        elif decade_center == '00s': start_year, end_year = 2000, 2009
        elif decade_center == '10s': start_year, end_year = 2010, 2019
        elif decade_center == '20s': start_year, end_year = 2020, 2029
        
        decade_data = df[(df['year'] >= start_year) & (df['year'] <= end_year)]
        if not decade_data.empty:
             # Sum counts by genre in this decade
             dominant_genre = decade_data.groupby('playlist_genre')['count'].sum().idxmax()
    
    # Sort genres based on '2020s' or global popularity if needed, but legend order matters less if greyed
    top_genres = df.groupby('playlist_genre')['count'].sum().sort_values(ascending=False).index

    # Build color map for this specific plot instance
    plot_colors = {}
    for g in top_genres:
        if dominant_genre and g != dominant_genre:
            plot_colors[g] = '#555555' # Grey for non-dominant
        else:
            plot_colors[g] = GENRE_COLOR_MAP.get(g, '#ffffff')

    # If we have a dominant genre, we want that trace to be on top? 
    # Plotly draws in order. We should make sure dominant is plotted last? No, sorting category_orders usually handles legend.
    # To handle 'click to color again', we rely on Plotly Legend Interaction (which effectively hides/shows).
    # But user wants 'click to highlight'. Standard legend click = Hide. Double click = Isolate.
    # To get "Grey -> Color", we would need two traces per genre: One Grey (Visible), One Color (Hidden).
    # Clicking "Color" in legend would show it ON TOP of Grey.
    # But that creates a double legend.
    
    # Creating a simplified version adhering to "display the most popular genre... in colour and others in grey"
    # The "click to highlight" is interpreted as standard isolation or visibility toggling, 
    # OR we can assume interaction is limited without complex callbacks.
    # However, to allow "restoring" color, we can set the 'greyed' traces to 'legendonly' initially? No, that hides them.
    
    # Compromise: We render ALL lines. The dominant is colored. Others are grey.
    # The user says "clicking them it should be possible to then highlight that genre in colour again".
    # This might mean clicking the GREY line turns it COLORED. That needs a custom callback.
    # GIVEN constraints (I can't easily add a new callback to the app structure without seeing main_callbacks fully/messing scope),
    # I will stick to the visual request first.
    
    # Actually, we can do this: define TWO traces for each genre.
    # 1. The "Background" (Grey). Always Visible (or maybe not?). name=f"{genre} (bg)"? No.
    # 2. The "Highlight" (Color). Visible=True for Dominant, Visible='legendonly' for others.
    # When user clicks the legend item (which is 'legendonly' i.e. greyed out in legend), it Becomes Visible and Colored.
    # But we still need the Grey line to be visible when the Color one is Hidden.
    # Plotly doesn't support "Alternative" visibility natively.
    
    # Let's try: Trace for EVERY genre in COLOUR.
    # But set visible='legendonly' for all except Dominant.
    # ADDITIONALLY, add a single "All Others" grey trace? No, each genre has its own curve.
    
    # REVISED STRATEGY:
    # 1. Create a "Background" Grey trace for EVERY genre. (ShowLegend=False)
    # 2. Create a "Foreground" Colored trace for EVERY genre. 
    #    - For Dominant: visible=True
    #    - For Others: visible='legendonly'
    # Result:
    # - User sees 1 colored line + many grey lines.
    # - Legend shows all genres (colored entries). Dominant is active. Others are 'off'.
    # - If user clicks a legend item (currently off), the colored line appears ON TOP of the grey one.
    # - If user clicks Dominant (currently on), it turns off (revealing the grey background underneath).
    
    fig = go.Figure()
    
    for genre in top_genres:
        g_data = df[df['playlist_genre'] == genre].sort_values('year')
        
        # 1. Background (Grey) Trace - Always visible, no legend
        # Making it slightly transparent so overlaps aren't total blocks
        fig.add_trace(go.Scatter(
            x=g_data['year'], 
            y=g_data['count'],
            mode='lines',
            line=dict(color='rgba(150, 150, 150, 0.3)', width=2),
            name=genre,
            showlegend=False,
            hoverinfo='skip' # Don't clutter hover
        ))
        
        # 2. Foreground (Color) Trace - Controlled by Legend
        is_dominant = (genre == dominant_genre) if dominant_genre else False
        
        fig.add_trace(go.Scatter(
            x=g_data['year'], 
            y=g_data['count'],
            mode='lines',
            line=dict(color=GENRE_COLOR_MAP.get(genre, '#ffffff'), width=4 if is_dominant else 3),
            name=genre.title(), # Capitalize for Legend
            visible=True if is_dominant or not dominant_genre else 'legendonly'
        ))

    fig.update_layout(
         title="Genre Popularity Over Time (1950-2030)",
         paper_bgcolor='rgba(30, 30, 40, 0.7)', 
         plot_bgcolor="rgba(0,0,0,0)",
         font=dict(color="white"),
         xaxis=dict(showgrid=False),
         yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
         autosize=True,
         margin=dict(l=40, r=40, t=50, b=40),
         legend=dict(
             font=dict(size=10),
             itemclick="toggle",
             itemdoubleclick="toggleothers"
         )
    )
    
    # Add vertical marker for current decade if provided
    if decade_center:
        decade_centers = {
            '50s': 1955, '60s': 1965, '70s': 1975, '80s': 1985, '90s': 1995, '00s': 2005, '10s': 2015, '20s': 2025
        }
        center_year = decade_centers.get(decade_center)
        if center_year:
             fig.add_vline(x=center_year, line_width=2, line_dash="dash", line_color="white")
             
    # style_fig(fig) # Custom styling function might overwrite my layout, so I'll skip or ensure it's safe. 
    # Usually better to rely on manual layout here since we did custom work.
    return fig

def draw_rate_of_change_barplot(current_decade, selected_genres=None, show_breakdown=False):
    ordered_decades = ['50s', '60s', '70s', '80s', '90s', '00s', '10s', '20s']
    if current_decade not in ordered_decades:
        return go.Figure()

    idx = ordered_decades.index(current_decade)
    if idx == 0:
        # No previous decade
        fig = go.Figure()
        fig.update_layout(
             title=dict(text="No Previous Decade", font=dict(color="white", size=10)),
             paper_bgcolor="rgba(0,0,0,0)",
             plot_bgcolor="rgba(0,0,0,0)",
             xaxis=dict(visible=False), yaxis=dict(visible=False, gridcolor="rgba(255,255,255,0.1)"),
             margin=dict(l=10, r=10, t=20, b=20)
        )
        return fig

    prev_decade = ordered_decades[idx - 1]

    # Updated Categories: Energy, Danceability, Loudness, Acousticness, Valence, Duration
    categories = ["Energy", "Danceability", "Loudness", "Acousticness", "Valence", "Duration"]
    
    # Filter Data
    current_data = spider_data[spider_data['decade'] == current_decade].copy()
    prev_data = spider_data[spider_data['decade'] == prev_decade].copy()

    if selected_genres:
        # User selected specific genres
        loop_genres = selected_genres
    else:
        # If no selection, either show all or show nothing?
        # The prompt says "as many bars as there are genres selcted in the dropdown menu"
        # If the dropdown is empty, usually we might show a default or total.
        # But let's check input. Spider graph usually defaults to one genre if none.
        # We'll use all genres present in the current decade if none specified, 
        # OR handle the case where "selected_genres" comes from the dropdown which might be None
        loop_genres = get_genres() 
        # Intersection with what's actually in data
        loop_genres = [g for g in loop_genres if g in current_data['playlist_genre'].unique()]

    change_data = []
    
    for genre in loop_genres:
        # Filter for genre
        c_g = current_data[current_data['playlist_genre'] == genre]
        p_g = prev_data[prev_data['playlist_genre'] == genre]

        # Ignore genre if it didn't exist in previous decade (based on a minimal threshold)
        # Using 5 as threshold to avoid misleading "change" from noise
        if len(p_g) < 5:
            continue

        if c_g.empty or p_g.empty:
            continue
            
        c_means = c_g[categories].mean()
        p_means = p_g[categories].mean()
        
        # Calculate per-feature change
        feature_changes = (c_means - p_means).abs()
        
        row_data = {'genre': genre, 'total_change': feature_changes.sum()}
        for cat in categories:
            row_data[cat] = feature_changes[cat]
            
        change_data.append(row_data)
        
    if not change_data:
        return go.Figure().update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(visible=False), yaxis=dict(visible=False))

    df_plot = pd.DataFrame(change_data)
    
    fig = go.Figure()

    if show_breakdown:
        # Stacked Bar Chart (Breakdown)
        # Strategy: Use the genre's color (solid), but separate segments with white outline.
        # Label: Full Feature Name if segment is large enough.
        
        # 1. Pre-calculate colors and texts
        colors_for_feature = {cat: [] for cat in categories}
        text_for_feature = {cat: [] for cat in categories}

        for i, row in df_plot.iterrows():
            genre = row['genre']
            # Strict adherence to GENRE_COLOR_MAP
            base_hex = GENRE_COLOR_MAP.get(genre, '#888888')
            
            # Convert to RBGA with opacity 0.6
            if base_hex.startswith('#'):
                 base_rgb = pcolors.hex_to_rgb(base_hex)
            elif base_hex.startswith('rgb'):
                 vals = base_hex[4:-1].split(',')
                 base_rgb = (int(vals[0]), int(vals[1]), int(vals[2]))
            else:
                 base_rgb = (200, 200, 200)

            rgba_str = f'rgba({base_rgb[0]}, {base_rgb[1]}, {base_rgb[2]}, 0.6)'
            
            # Use same color for all features of this genre
            for cat in categories:
                colors_for_feature[cat].append(rgba_str)
                
                # Text: Feature Name if value is significant
                val = row[cat]
                # Lower threshold to show more text, and prefer full name
                if val > 0.05:
                    text_for_feature[cat].append(cat)
                else:
                    text_for_feature[cat].append("")

        for cat in categories:
            fig.add_trace(go.Bar(
                name=cat,
                x=df_plot['genre'],
                y=df_plot[cat],
                marker_color=colors_for_feature[cat],
                marker_line=dict(width=1, color='rgba(255, 255, 255, 0.5)'), # White outline to separate stack
                text=text_for_feature[cat],
                textposition='inside', # Force inside to avoid clutter
                insidetextfont=dict(color='white', size=10), 
                hovertemplate=f"<b>%{{x}}</b><br>{cat}: %{{y:.2f}}<extra></extra>"
            ))
            
        barmode = 'stack'
        show_legend = False # Colors mean Genre, not feature. Legend would be redundant with x-axis.
        
    else:
        # Simple Bar Chart (Total Change)
        # Colored by Genre to match context
        colors = [GENRE_COLOR_MAP.get(g, '#ffffff') for g in df_plot['genre']]
        
        fig.add_trace(go.Bar(
            x=df_plot['genre'],
            y=df_plot['total_change'],
            marker_color=colors,
            text=df_plot['total_change'].apply(lambda x: f"{x:.2f}"),
            textposition='auto',
            hovertemplate="<b>%{x}</b><br>Total Change: %{y:.2f}<extra></extra>"
        ))
        
        barmode = 'group'
        show_legend = False
    
    fig.update_layout(
         barmode=barmode,
         title=dict(text=f"Feature Change vs {prev_decade}", font=dict(color="white", size=11)),
         paper_bgcolor="rgba(0,0,0,0)", 
         plot_bgcolor="rgba(0,0,0,0)",
         font=dict(color="white"),
         xaxis=dict(
             showgrid=False, 
             showticklabels=True, 
             tickfont=dict(size=9, color='white'),
             title=None
         ),
         yaxis=dict(
             showgrid=True, 
             gridcolor="rgba(255,255,255,0.1)",
             showticklabels=True,
             tickfont=dict(size=9, color='white'),
             title=None
         ),
         showlegend=show_legend,
         legend=dict(
             orientation="h",
             yanchor="bottom",
             y=1.02,
             xanchor="right",
             x=1,
             font=dict(size=8),
             bgcolor="rgba(0,0,0,0)"
         ),
         margin=dict(l=30, r=10, t=30, b=20),
         autosize=True
    )
             

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
                "padding": "20px 20px 40px 20px",
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
                                     html.Span("E: Energy", style={"marginRight": "10px", "color": "#E0E0E0", "fontWeight": "bold"}),
                                     html.Span("D: Danceability", style={"marginRight": "10px", "color": "#E0E0E0", "fontWeight": "bold"}),
                                     html.Span("L: Loudness", style={"marginRight": "10px", "color": "#E0E0E0", "fontWeight": "bold"}),
                                     html.Span("A: Acousticness", style={"marginRight": "10px", "color": "#E0E0E0", "fontWeight": "bold"}),
                                     html.Span("V: Valence", style={"marginRight": "10px", "color": "#E0E0E0", "fontWeight": "bold"}),
                                     html.Span("Dur: Duration", style={"color": "#E0E0E0", "fontWeight": "bold"})
                                 ]),
                                 # Tooltip Content
                                 html.Div([
                                     html.Div([
                                         # Column 1
                                         html.Div([
                                             html.Div([html.Strong("Energy", style={"color": "#E0E0E0", "display": "block", "marginBottom": "2px", "fontSize": "1.1em"}), html.Span("Intensity, speed, and noise level", style={"color": "white", "fontSize": "0.9em"})], style={"marginBottom": "12px"}),
                                             html.Div([html.Strong("Danceability", style={"color": "#E0E0E0", "display": "block", "marginBottom": "2px", "fontSize": "1.1em"}), html.Span("Rhythm stability and beat strength", style={"color": "white", "fontSize": "0.9em"})])
                                         ], style={"flex": "1", "padding": "0 10px"}),
                                         
                                         # Column 2
                                         html.Div([
                                             html.Div([html.Strong("Loudness", style={"color": "#E0E0E0", "display": "block", "marginBottom": "2px", "fontSize": "1.1em"}), html.Span("Overall volume (dB)", style={"color": "white", "fontSize": "0.9em"})], style={"marginBottom": "12px"}),
                                             html.Div([html.Strong("Acousticness", style={"color": "#E0E0E0", "display": "block", "marginBottom": "2px", "fontSize": "1.1em"}), html.Span("Presence of acoustic instruments", style={"color": "white", "fontSize": "0.9em"})])
                                         ], style={"flex": "1", "padding": "0 10px", "borderLeft": "1px solid rgba(255,255,255,0.1)", "borderRight": "1px solid rgba(255,255,255,0.1)"}),
                                         
                                         # Column 3
                                         html.Div([
                                             html.Div([html.Strong("Valence", style={"color": "#E0E0E0", "display": "block", "marginBottom": "2px", "fontSize": "1.1em"}), html.Span("Musical positiveness/happiness", style={"color": "white", "fontSize": "0.9em"})], style={"marginBottom": "12px"}),
                                             html.Div([html.Strong("Duration", style={"color": "#E0E0E0", "display": "block", "marginBottom": "2px", "fontSize": "1.1em"}), html.Span("Length of the track", style={"color": "white", "fontSize": "0.9em"})])
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
                                 "borderRadius": "0px",
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
                            style={"flex": "1", "minHeight": "0", "borderTop": "1px solid rgba(255,255,255,0.1)", "marginTop": "10px", "position": "relative"},
                            children=[
                                 # Checkbox for Breakdown
                                html.Div(
                                    dcc.Checklist(
                                        id='breakdown-checkbox',
                                        options=[{'label': ' Show Feature Breakdown', 'value': 'show'}],
                                        value=[],
                                        style={"color": "#E0E0E0", "fontSize": "0.8em"}
                                    ),
                                    style={"position": "absolute", "top": "5px", "right": "10px", "zIndex": "10"}
                                ),
                                dcc.Graph(
                                    id='rate-of-change-barplot',
                                    figure=draw_rate_of_change_barplot(current_decade, selected_genres),
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
                         "borderRadius": "0px",
                         "overflow": "hidden"
                     },
                     children=[
                         # Area Plots Graph
                         html.Div(
                             dcc.Graph(
                                 id='analysis1-area', 
                                 figure=draw_area_plots(decades_list, current_decade, ["Energy", "Danceability", "Loudness", "Acousticness", "Valence", "Duration", "Liveness"], bin_size="1 year"),
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
                "padding": "20px 20px 50px 20px", # Added bottom padding for decade selector
                "boxSizing": "border-box",
                "gap": "10px"
            },
            children=[
                 # Top Section: Changes & Card (50%)
                 html.Div(
                     style={"display": "flex", "flexDirection": "row", "gap": "20px", "flex": "1", "minHeight": "0", "width": "100%"},
                     children=[
                         # Left: Biggest Changes (Asc/Desc Changes)
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
                             style={"flex": "1", "overflow": "hidden"}
                         )
                     ]
                 ),
                 
                 # Bottom Section: Genre Trends (50%)
                 html.Div(
                     dcc.Graph(
                         figure=draw_genre_trends(current_decade), 
                         config={'responsive': True, 'displayModeBar': False},
                         style={"height": "100%", "width": "100%"}
                     ),
                     style={"flex": "1", "minHeight": "0", "width": "100%"}
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
    ordered_decades = ['50s', '60s', '70s', '80s', '90s', '00s', '10s', '20s']

    # Updated Categories: Energy, Danceability, Loudness, Acousticness, Valence, Duration
    categories = ["Energy", "Danceability", "Loudness", "Acousticness", "Valence", "Duration"]
    category_labels = [c[0] if c != "Duration" else "Dur" for c in categories]
    label_colors = ["#E0E0E0"] * 6 # Monochromatic white-ish for labels to distinguish from genres 
    
    fig = go.Figure()
    
    base_data = spider_data.copy()
    if selected_genres:
        if 'playlist_genre' in base_data.columns:
            base_data = base_data[base_data['playlist_genre'].isin(selected_genres)]
    
    for decade in decades_list:
        # --- 2. Current Decade ---
        filtered_data = base_data[base_data['decade'] == decade]
        
        if override_color:
            line_color_str = override_color
            if override_color.startswith('#'):
                rgb_tuple = pcolors.hex_to_rgb(override_color)
                # Ensure opacity 0.4 for "lighten up"
                fill_color_str = f'rgba({rgb_tuple[0]}, {rgb_tuple[1]}, {rgb_tuple[2]}, 0.4)'
            elif override_color.startswith('rgb'):
                vals = override_color[4:-1].split(',')
                fill_color_str = f'rgba({vals[0]},{vals[1]},{vals[2]},0.4)'
            else:
                fill_color_str = override_color
        else:
            rgb = decade_rgb.get(decade, (128, 128, 128))
            line_color_str = f'rgb({rgb[0]}, {rgb[1]}, {rgb[2]})'
            fill_color_str = f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.4)'
        
        if filtered_data.empty:
            avg_values = [None] * len(categories)
            theta_values = category_labels
        else:
            avg_values = [filtered_data[cat].mean() for cat in categories]
            # Close the loop
            avg_values.append(avg_values[0])
            theta_values = category_labels + [category_labels[0]]
            
        fig.add_trace(go.Scatterpolar(
            r=avg_values,
            theta=theta_values,
            fill='toself' if not filtered_data.empty else None,
            name=f"Average {decade}",
            line=dict(color=line_color_str, width=3), # Thicker line for main
            fillcolor=fill_color_str
        ))

        # --- 1. Previous Decade (Shadow) ---
        if decade in ordered_decades:
            curr_idx = ordered_decades.index(decade)
            if curr_idx > 0:
                prev_decade = ordered_decades[curr_idx - 1]
                prev_data = base_data[base_data['decade'] == prev_decade]
                
                if not prev_data.empty:
                    prev_means = [prev_data[cat].mean() for cat in categories]
                    # Close the loop
                    prev_means.append(prev_means[0])
                    prev_theta = category_labels + [category_labels[0]]
                    
                    # We override everything to be white and dashed, no fill
                    line_color_prev = 'white'
                    fill_color_prev = None 

                    fig.add_trace(go.Scatterpolar(
                        r=prev_means,
                        theta=prev_theta,
                        fill=None,
                        name=f"{prev_decade}",
                        line=dict(color=line_color_prev, dash='dash'),
                        hoverinfo='name+r'
                    ))
        
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 1.0], 
                gridcolor="rgba(255, 255, 255, 0.2)",
                linecolor="rgba(255, 255, 255, 0.2)"
            ), 
            bgcolor="rgba(0,0,0,0)",
            gridshape='linear',
            angularaxis=dict(
                rotation=90, 
                direction="clockwise",
                showticklabels=True,
                tickfont=dict(color="#E0E0E0", size=14, family="Arial Black"), 
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
        margin=dict(l=55, r=55, t=40, b=30)
    )
    return fig

def draw_area_plots(decades_list, current_decade, features=["Energy", "Danceability", "Loudness", "Acousticness", "Valence"], opacity=1.0, bin_size=None, selected_genres=None, highlighted_genre=None):
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
    
    if current_decade:
        decade_centers = {
            '50s': 1955, '60s': 1965, '70s': 1975, '80s': 1985, '90s': 1995, '00s': 2005, '10s': 2015, '20s': 2025
        }
        center_year = decade_centers.get(current_decade)
        if center_year:
             fig_line.add_vline(x=center_year, line_width=2, line_dash="dash", line_color="#4D96FF")

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
    # Updated Categories to match Analysis 1
    categories = ["Energy", "Danceability", "Loudness", "Acousticness", "Valence", "Duration"]
    category_labels = [c[0] if c != "Duration" else "Dur" for c in categories]

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

    song1_values = song1_row[categories].values.flatten().tolist()
    song1_name = song1_row["track_name"].values.flatten().item()
    song1_genre = song1_row["playlist_genre"].values.flatten().item() if "playlist_genre" in song1_row.columns else "Unknown"
    song1_values = [float(x) for x in song1_values]
    
    song2_values = song2_row[categories].values.flatten().tolist()
    song2_name = song2_row["track_name"].values.flatten().item()
    song2_genre = song2_row["playlist_genre"].values.flatten().item() if "playlist_genre" in song2_row.columns else "Unknown"
    song2_values = [float(x) for x in song2_values]

    # Close the loops
    song1_values.append(song1_values[0])
    song2_values.append(song2_values[0])
    categories_closed = categories + [categories[0]] # For logic if needed
    labels_closed = category_labels + [category_labels[0]] # For display

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=song1_values,
        theta=labels_closed,
        fill='toself',
        name=f"{song1_name}",
        line_color='#636EFA',
        hoverinfo='text',
        hovertext=[f"{c}: {v:.2f}" for c, v in zip(categories_closed, song1_values)]
    ))

    fig.add_trace(go.Scatterpolar(
        r=song2_values,
        theta=labels_closed,
        fill='toself',
        name=f"{song2_name}",
        line_color='#EF553B',
        hoverinfo='text',
        hovertext=[f"{c}: {v:.2f}" for c, v in zip(categories_closed, song2_values)]
    ))
    
    if show_genre1:
        genre1_data = filtered_data[filtered_data['playlist_genre'] == song1_genre]
        if not genre1_data.empty:
            genre1_avg = genre1_data[categories].mean().tolist()
            genre1_avg.append(genre1_avg[0]) # Close loop
            fig.add_trace(go.Scatterpolar(
                r=genre1_avg,
                theta=labels_closed,
                name=f"Avg {song1_genre.title()}",
                line=dict(dash='dash', color='#636EFA'), 
                fill=None,
                hoverinfo='text',
                hovertext=[f"Avg {song1_genre.title()}: {v:.2f}" for v in genre1_avg]
            ))
            
    if show_genre2:
        genre2_data = filtered_data[filtered_data['playlist_genre'] == song2_genre]
        if not genre2_data.empty:
            genre2_avg = genre2_data[categories].mean().tolist()
            genre2_avg.append(genre2_avg[0]) # Close loop
            # Avoid duplicate trace if same genre and showing both
            if not (show_genre1 and song1_genre == song2_genre):
                fig.add_trace(go.Scatterpolar(
                    r=genre2_avg,
                    theta=labels_closed,
                    name=f"Avg {song2_genre.title()}",
                    line=dict(dash='dash', color='#EF553B'),
                    fill=None,
                    hoverinfo='text',
                    hovertext=[f"Avg {song2_genre.title()}: {v:.2f}" for v in genre2_avg]
                ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 1.0], 
                gridcolor="rgba(255, 255, 255, 0.2)",
                linecolor="rgba(255, 255, 255, 0.2)"
            ), 
            bgcolor="rgba(0,0,0,0)",
            gridshape='linear',
            angularaxis=dict(
                rotation=90, 
                direction="clockwise",
                showticklabels=True,
                tickfont=dict(color="#E0E0E0", size=14, family="Arial Black"), 
                gridcolor="rgba(255, 255, 255, 0.2)", 
                linecolor="rgba(255, 255, 255, 0.2)"
            )
        ),
        showlegend=True,
        title=dict(
            text=f"Comparison: {song1_name} vs {song2_name}", 
            font=dict(color="white", size=14),
            y=0.98, 
            x=0.5,
            xanchor='center',
            yanchor='top'
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        autosize=True,
        margin=dict(l=80, r=80, t=100, b=100), 
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.1,    
            xanchor="center",
            x=0.5,
            font=dict(color="white", size=11)
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
    '50s': "The 1950s birthed Rock 'n' Roll, shaking up the music world with rebellious energy. Elvis Presley, the King of Rock and Roll, became a global icon with his electrifying performances.",
    '60s': "The 1960s were defined by counterculture and the British Invasion. The Beatles revolutionized popular music with their innovative songwriting and studio experimentation.",
    '70s': "The 1970s explored new sonic territories with progressive rock and massive stadium tours. Pink Floyd created immersive concept albums that pushed the boundaries of what music could be.",
    '80s': "The 1980s brought the sound of synthesizers and the rise of the music video era. Michael Jackson, the King of Pop, dominated the charts with his groundbreaking dance moves and hits.",
    '90s': "The 1990s saw a shift towards raw, emotional sound with the grunge movement. Nirvana and Kurt Cobain defined a generation, bringing alternative rock to the mainstream.",
    '00s': "The 2000s marked the digital revolution and the rise of R&B and pop powerhouses. Beyoncé emerged as a solo superstar, influencing culture with her powerful vocals and performances.",
    '10s': "The 2010s saw the dominance of streaming and the evolution of country-pop crossovers. Taylor Swift became a global phenomenon, celebrated for her storytelling and genre-spanning reinventions.",
    '20s': "The 2020s are shaped by viral hits and moody, atmospheric pop production. The Weeknd defines the modern sound with his cinematic blend of R&B, pop, and 80s nostalgia."
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
    default_color = DECADE_COLORS.get(decade, '#333')
    
    # Map decade artist to their primary genre
    artist_genre_map = {
        '50s': 'rock',   # Elvis
        '60s': 'rock',   # Beatles
        '70s': 'rock',   # Pink Floyd
        '80s': 'pop',    # Michael Jackson
        '90s': 'rock',   # Nirvana
        '00s': 'r&b',    # Beyoncé
        '10s': 'pop',    # Taylor Swift
        '20s': 'pop'     # The Weeknd
    }
    
    target_genre = artist_genre_map.get(decade)
    color = GENRE_COLOR_MAP.get(target_genre, default_color)

    text = DECADE_INFO.get(decade, "Description unavailable.")
    
    # Determine image path dynamically
    img_src = f'assets/imgs/artists/{decade}.jpg' # Fallback
    # Check common extensions
    for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
         # Check relative to execution directory
         if os.path.exists(f'assets/imgs/artists/{decade}{ext}'):
             img_src = f'assets/imgs/artists/{decade}{ext}'
             break
    
    return html.Div(style={
        'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        'backgroundColor': 'rgba(30, 30, 40, 0.7)',
        'border': '1px solid rgba(255,255,255,0.1)',
        'width': '100%', 
        'height': '100%', 
        'display': 'flex', 
        'flexDirection': 'column',
        'boxSizing': 'border-box'
    }, children=[
        # Top color accent
        html.Div(style={
            'backgroundColor': color,
            'height': '6px',
            'width': '100%',
            'flexShrink': 0
        }),
        # Content Row
        html.Div(style={
            'display': 'flex',
            'flexDirection': 'row',
            'flex': '1',
            'minHeight': '0', # Allows child to shrink below content size if needed
            'padding': '15px',
            'gap': '15px'
        }, children=[
            # Left: Text Content
            html.Div(style={
                'flex': '3', # Give text more space
                'display': 'flex',
                'flexDirection': 'column',
                'justifyContent': 'flex-start',
                'overflow': 'hidden', # Prevent expansion
            }, children=[
                html.H2(f"The {decade}", style={
                    'marginTop': '0', 
                    'marginBottom': '10px',
                    'borderBottom': f'2px solid {color}',
                    'paddingBottom': '5px',
                    'color': 'white',
                    'fontSize': '1.8em',
                    'whiteSpace': 'nowrap'
                }),
                html.P(text, style={
                    'fontSize': '1.1em', 
                    'lineHeight': '1.4', 
                    'color': '#eee',
                    'margin': '0'
                })
            ]),
            
            # Right: Image
            html.Div(style={
                'flex': '2',
                'display': 'flex',
                'justifyContent': 'center',
                'alignItems': 'center',
                'height': '100%',
                'overflow': 'hidden'
            }, children=[
                html.Img(
                    src=img_src,
                    style={
                        'maxWidth': '100%',
                        'maxHeight': '100%',
                        'objectFit': 'contain',
                        'borderRadius': '6px'
                    }
                )
            ])
        ])
    ])