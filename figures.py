import plotly.graph_objects as go
from dash import dcc

# This draws the actual plots 
# it takes the selected topbar and produces the figure accordingly
# adjusts the figure based on the sidebar selection as well
def draw_figure(topbar_tab, sidebar_tab):
    if topbar_tab == "topic-3":
        figure = draw_spider(sidebar_tab, "Song A", "Song B")  # Pass song names as needed
    else:
        placeholder_figure = f"This is where {topbar_tab} / {sidebar_tab} figure will be drawn"
        figure = placeholder_figure

    return figure


# Updated draw_spider to create an actual spider graph
def draw_spider(sidebar_tab, song1="Song 1", song2="Song 2"):
    # Define categories for the spider graph
    categories = ["Energy", "Danceability", "Valence", "Acousticness", "Instrumentalness"]
    
    # Placeholder data for the two songs
    song1_values = [70, 85, 60, 40, 30]  # Default values for song1
    song2_values = [50, 65, 80, 55, 45]  # Default values for song2

    # Apply themes based on the selected decade
    if sidebar_tab == "50s":
        theme_color = "#FF5733"  # Example color for the 50s
        song1_values = [60, 70, 50, 30, 20]
        song2_values = [40, 60, 70, 50, 30]
    elif sidebar_tab == "60s":
        theme_color = "#33FF57"  # Example color for the 60s
        song1_values = [80, 90, 70, 50, 40]
        song2_values = [70, 80, 60, 40, 30]
    elif sidebar_tab == "70s":
        theme_color = "#5733FF"  # Example color for the 70s
        song1_values = [90, 85, 75, 65, 55]
        song2_values = [80, 75, 65, 55, 45]
    else:
        theme_color = "#FFC300"  # Default color for other decades

    # Create the spider graph
    fig = go.Figure()

    # Add song1 data
    fig.add_trace(go.Scatterpolar(
        r=song1_values,
        theta=categories,
        fill='toself',
        name=song1,
        line=dict(color=theme_color)  # Apply theme color
    ))

    # Add song2 data
    fig.add_trace(go.Scatterpolar(
        r=song2_values,
        theta=categories,
        fill='toself',
        name=song2,
        line=dict(color="#C70039")  # Secondary color
    ))

    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])  # Set range for the axes
        ),
        showlegend=True,
        title=f"Spider Graph for {song1} and {song2} ({sidebar_tab})",
        plot_bgcolor="rgba(0,0,0,0)",  # Transparent plot background
        paper_bgcolor="rgba(0,0,0,0)",  # Transparent overall background
    )

    # Return the figure as a Plotly HTML div
    return dcc.Graph(figure=fig)