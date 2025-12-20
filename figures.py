import plotly.graph_objects as go
from dash import dcc
import pandas as pd

# Load preprocessed spider graph data
spider_csv_path = "assets/spider_graph_data.csv"
spider_data = pd.read_csv(spider_csv_path)

# This draws the actual plots 
# it takes the selected topbar and produces the figure accordingly
# adjusts the figure based on the sidebar selection as well
# In figures.py

# Update the signature to accept optional song arguments
def draw_figure(topbar_tab, sidebar_tab, song1=None, song2=None):
    if topbar_tab == "topic-3":
        # Pass the songs down to draw_spider
        # If song1/song2 are None (which shouldn't happen with the fix above), 
        # draw_spider will use its defaults (which might still crash, but we fixed the input).
        
        if song1 and song2:
             figure = draw_spider(sidebar_tab, song1, song2)
        else:
             # Fallback if called without songs (e.g. initial load if logic is slightly off)
             # This is a safety measure
             figure = draw_spider(sidebar_tab) 
             
    else:
        placeholder_figure = f"This is where {topbar_tab} / {sidebar_tab} figure will be drawn"
        figure = placeholder_figure

    return figure


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
        height=600,  # Make graph taller
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