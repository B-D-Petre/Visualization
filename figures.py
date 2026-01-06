import plotly.graph_objects as go
from dash import dcc, html
import pandas as pd
import plotly.express as px


# Load preprocessed spider graph data
spider_csv_path = "assets/spider_graph_data.csv"
spider_data = pd.read_csv(spider_csv_path)
# Load Filip's data
genre_counts = pd.read_csv('genre_counts_processed.csv')

# This draws the actual plots 
# it takes the selected topbar and produces the figure accordingly
# adjusts the figure based on the sidebar selection as well
# In figures.py

# Update the signature to accept optional song arguments
def draw_figure(topbar_tab, decades_list, current_decade, song1=None, song2=None):
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
             figure = draw_spider(current_decade, song1, song2)
        else:
             # Fallback if called without songs (e.g. initial load if logic is slightly off)
             # This is a safety measure
             figure = draw_spider(current_decade) 
             
    elif topbar_tab == "topic-1":
        # --- Analysis 1 Tab ---
        # Large spider graph for the decade average
        fig = draw_spider_analysis1(decades_list, current_decade)
        # Area Plots for the right side (single column, 9 rows)
        timeseries_features = ["Energy", "Tempo", "Danceability", "Loudness", "Liveness", "Valence", "Speechiness", "Acousticness", "Instrumentalness"]
        fig_area = draw_area_plots(decades_list, current_decade, timeseries_features)
        # Compose the layout: spider graph left, area plots right
        figure = html.Div(style={"display": "flex", "flexDirection": "row", "width": "100%"}, children=[
            html.Div(dcc.Graph(figure=fig), style={"flex": "1", "padding": "20px"}),
            html.Div(dcc.Graph(figure=fig_area), style={"flex": "1", "padding": "20px"})
        ])
    elif topbar_tab == "topic-4":  # Filip's changes tab
        figure = html.Div([
            dcc.Graph(figure=draw_change(current_decade, genre_counts, "desc")),
            dcc.Graph(figure=draw_change(current_decade, genre_counts, "asc")),
            create_decade_card(current_decade)
        ])
    else:
        placeholder_figure = f"This is where {topbar_tab} / {current_decade} figure will be drawn"
        figure = placeholder_figure

    return figure


# New functions for Prototype Dashboard
def draw_spider_analysis1(decades_list, current_decade):
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
    categories = ["Energy", "Danceability", "Valence", "Acousticness", "Instrumentalness"]
    fig = go.Figure()
    for decade in decades_list:
        filtered_data = spider_data[spider_data['decade'] == decade]
        avg_values = [filtered_data[cat].mean() for cat in categories]
        color = decade_colors.get(decade, 'grey')
        fig.add_trace(go.Scatterpolar(
            r=avg_values,
            theta=categories,
            fill='toself',
            name=f"Average {decade}",
            line=dict(color=color),
            fillcolor=color
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1]), bgcolor="rgba(0,0,0,0)"),
        showlegend=True,
        title=f"Average Audio Features",
        paper_bgcolor="rgba(0,0,0,0.5)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        autosize=True,
        margin=dict(l=80, r=80, t=100, b=80)
    )
    return fig

def draw_area_plots(decades_list, current_decade, features=["Energy", "Danceability", "Valence", "Acousticness", "Instrumentalness"], opacity=1.0, bin_size=None):
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
    available_features = [c for c in features if c in spider_data.columns]
    import plotly.subplots as sp
    grid_rows = len(available_features)
    grid_cols = 1
    fig_area = sp.make_subplots(rows=grid_rows, cols=grid_cols, subplot_titles=available_features, vertical_spacing=0.08)
    for decade in decades_list:
        norm_df = spider_data[spider_data['decade'] == decade].copy()
        for feature in available_features:
            col = norm_df[feature]
            if col.max() != col.min():
                norm_df[feature] = (col - col.min()) / (col.max() - col.min())
            else:
                norm_df[feature] = 0
        # Bin logic
        if bin_size and bin_size != "No bins":
            if 'track_album_release_date' in norm_df.columns:
                norm_df['track_album_release_date'] = pd.to_datetime(norm_df['track_album_release_date'], errors='coerce')
                if bin_size == "1 week":
                    freq = 'W'
                elif bin_size == "1 month":
                    freq = 'MS'
                elif bin_size == "5 months":
                    freq = '5MS'
                else:
                    freq = 'YS'
                norm_df = norm_df.set_index('track_album_release_date')
                # Only aggregate numeric columns to avoid TypeError
                numeric_cols = norm_df.select_dtypes(include='number').columns
                norm_df = norm_df.groupby(pd.Grouper(freq=freq))[numeric_cols].mean().reset_index()
                x_axis = 'track_album_release_date'
            elif 'year' in norm_df.columns:
                x_axis = 'year'
            else:
                norm_df['index'] = norm_df.index
                x_axis = 'index'
        else:
            if 'track_album_release_date' in norm_df.columns:
                x_axis = 'track_album_release_date'
            elif 'year' in norm_df.columns:
                x_axis = 'year'
            else:
                norm_df['index'] = norm_df.index
                x_axis = 'index'
        for i, feature in enumerate(available_features):
            row = i + 1
            col = 1
            ts = norm_df.copy()
            if x_axis == 'track_album_release_date' and not pd.api.types.is_datetime64_any_dtype(ts[x_axis]):
                ts[x_axis] = pd.to_datetime(ts[x_axis], errors='coerce')
            ts = ts.sort_values(x_axis)
            color_rgb = decade_rgb.get(decade, (128, 128, 128))
            line_color = f'rgba({color_rgb[0]}, {color_rgb[1]}, {color_rgb[2]}, {opacity})'
            fill_color = f'rgba({color_rgb[0]}, {color_rgb[1]}, {color_rgb[2]}, {opacity * 0.5})'
            # Convert datetime x-axis to year for consistent x-axis labeling
            if x_axis == 'track_album_release_date':
                ts['year_for_x'] = ts[x_axis].dt.year
                plot_x = 'year_for_x'
            else:
                plot_x = x_axis
            fig_area.add_trace(
                go.Scatter(x=ts[plot_x], y=ts[feature], fill='tozeroy', mode='lines', name=f"{feature} {decade}", line=dict(color=line_color), fillcolor=fill_color),
                row=row, col=col
            )

        # Set x-axis range for all subplots and add vertical line at the center of the selected decade
        decade_centers = {
            '50s': 1955, '60s': 1965, '70s': 1975, '80s': 1985, '90s': 1995, '00s': 2005, '10s': 2015, '20s': 2025
        }
        center_year = decade_centers.get(current_decade, 1980)
        for i in range(len(available_features)):
            fig_area.update_xaxes(range=[1950, 2030], row=i+1, col=1, title_text='Year')
            # Add vertical line at the center of the selected decade
            fig_area.add_vline(
                x=center_year,
                line_width=3,
                line_dash="dash",
                line_color="red",
                row=i+1,
                col=1,
            )
    fig_area.update_layout(height=None, width=None, showlegend=False, title_text="Area Plots of Normalized Audio Features", autosize=True, margin=dict(t=30, b=30, l=30, r=30), title_font=dict(size=12))
    return fig_area


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
def draw_spider(sidebar_tab, song1="6dOtVTDdiauQNBQEDOtlAB", song2="1d7Ptw3qYcfpdLNL5REhtJ"):
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
    song1_values = filtered_data[filtered_data['track_id'] == song1][categories].values.flatten()
    song1_name = filtered_data[filtered_data['track_id'] == song1]["track_name"].values.flatten().item()
    song2_values = filtered_data[filtered_data['track_id'] == song2][categories].values.flatten()
    song2_name = filtered_data[filtered_data['track_id'] == song2]["track_name"].values.flatten().item()

    # Create the spider graph
    fig = go.Figure()

    # Add song1 data
    fig.add_trace(go.Scatterpolar(
        r=song1_values,
        theta=categories,
        fill='toself',
        name=song1_name #use actual song name
    ))

    # Add song2 data
    fig.add_trace(go.Scatterpolar(
        r=song2_values,
        theta=categories,
        fill='toself',
        name=song2_name
    ))

    # Update layout with transparent background and larger plot
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1]),  # Normalized range
            bgcolor="rgba(0,0,0,0)"  # Transparent polar background
        ),
        showlegend=True,
        title=f"Spider Graph for {song1_name} and {song2_name} ({sidebar_tab})",
        paper_bgcolor="rgba(0,0,0,0.5)",  # Transparent canvas background
        plot_bgcolor="rgba(0,0,0,0)",  # Transparent plot area
        font=dict(color="white"),  # White text for visibility
        autosize=True,
        margin=dict(l=80, r=80, t=100, b=80)  # Larger margins for the plot
    )

    # Return the figure object directly
    return fig

def get_songs_for_decade(sidebar_tab):
    #Get unique song names and IDs for a given decade
    filtered_data = spider_data[spider_data['decade'] == sidebar_tab]
    # 2. Use .values.tolist() to convert the DataFrame into a list of [name, id] pairs
    songs = filtered_data[["track_name", "track_id"]].drop_duplicates().values.tolist()
    
    return sorted(songs)
#FILIPS PLOTS=============================================================================================D
#paper esthetic
PAPER_BG = '#f0e6d2'  # Old paper color
INK_COLOR = '#2c2c2c' # Dark grey/black for text
FONT_FAMILY = "Garamond, 'Helvetica', serif"

# Custom visual theme function for Plotly
def style_fig(fig):
    fig.update_layout(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PAPER_BG,
        font=dict(family=FONT_FAMILY, color=INK_COLOR),
        title_font=dict(size=20, family=FONT_FAMILY),
        margin=dict(t=50, l=20, r=20, b=20)
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
        'fontFamily': "Garamond, 'Times New Roman', serif",
        'backgroundColor': '#fff',
        'border': '1px solid #ccc',
        'boxShadow': '5px 5px 10px rgba(0,0,0,0.1)',
        'maxWidth': '500px',
        'margin': '20px auto'
    }, children=[
        
        # A. The Colored Header (The "Tab")
        html.Div(style={
            'backgroundColor': color,
            'height': '15px',
            'width': '100%'
        }),
        
        # B. The Content Window
        html.Div(style={'padding': '25px'}, children=[
            # Title
            html.H2(f"The {decade}", style={
                'marginTop': '0', 
                'borderBottom': f'2px solid {color}',
                'paddingBottom': '10px',
                'color': '#2c2c2c'
            }),
            
            # The Text Description
            html.P(text, style={'fontSize': '1.2em', 'lineHeight': '1.5', 'color': '#333'}),
            
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