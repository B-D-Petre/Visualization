import plotly.graph_objects as go
from dash import dcc
import pandas as pd

# Load preprocessed spider graph data
spider_csv_path = "assets/spider_graph_data.csv"
spider_data = pd.read_csv(spider_csv_path)

# This draws the actual plots 
# it takes the selected topbar and produces the figure accordingly
# adjusts the figure based on the sidebar selection as well
def draw_figure(topbar_tab, sidebar_tab):
    if topbar_tab == "topic-3":
        figure = draw_spider(sidebar_tab)  # Pass song names as needed
    else:
        placeholder_figure = f"This is where {topbar_tab} / {sidebar_tab} figure will be drawn"
        figure = placeholder_figure

    return figure


# Updated draw_spider to use actual data
def draw_spider(sidebar_tab, song1="Die With A Smile", song2="BIRDS OF A FEATHER"):
    # Define categories for the spider graph
    categories = ["Energy", "Danceability", "Valence", "Acousticness", "Instrumentalness"]

    # Filter data for the selected decade
    filtered_data = spider_data[spider_data['decade'] == sidebar_tab]

    # Get values for the two songs
    song1_values = filtered_data[filtered_data['track_name'] == song1][categories].values.flatten()
    song2_values = filtered_data[filtered_data['track_name'] == song2][categories].values.flatten()

    # Create the spider graph
    fig = go.Figure()

    # Add song1 data
    fig.add_trace(go.Scatterpolar(
        r=song1_values,
        theta=categories,
        fill='toself',
        name=song1
    ))

    # Add song2 data
    fig.add_trace(go.Scatterpolar(
        r=song2_values,
        theta=categories,
        fill='toself',
        name=song2
    ))

    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1])  # Normalized range
        ),
        showlegend=True,
        title=f"Spider Graph for {song1} and {song2} ({sidebar_tab})"
    )

    # Return the figure as a Plotly HTML div
    return dcc.Graph(figure=fig)

def get_songs_for_decade(sidebar_tab):
    """Get unique song names for a given decade"""
    filtered_data = spider_data[spider_data['decade'] == sidebar_tab]
    songs = filtered_data['track_name'].unique().tolist()
    return sorted(songs)