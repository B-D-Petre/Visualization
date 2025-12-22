from dash import Dash, html, dcc, Input, Output, State
import os
import webbrowser
from figures import *

 
# This function arranges the plots in an html layout
def draw_pane(topbar_tab, decades_list, current_decade, layout="grid"):
    if topbar_tab == "topic-1":
        pane = draw_figure(topbar_tab, decades_list, current_decade)
    elif topbar_tab == "topic-3":
        if layout == "grid":
            # Get available songs for the selected decade
            available_songs = get_songs_for_decade(current_decade)
            song_options = [{"label": song_name, "value": track_id} for song_name, track_id in available_songs]
            
            pane = html.Div(
                style={
                    "padding": "30px",
                    "display": "grid",
                    "gridTemplateColumns": "1fr  1fr",  # Columns 1 and 3 are wider
                    "gridTemplateRows": "1fr 1fr auto",  # First row is fixed, second row fills available space
                    "gridGap": "30px",
                    "background": "rgba(0,0,0,0)"  # Transparent background for the grid
                },
                children=[
                    html.Div(
                        dcc.Dropdown(
                            id="song-1-dropdown",
                            options=song_options,
                            value=available_songs[0][1] if available_songs else None,
                            style={"color": "black"}
                        ),
                        style={"background": "rgba(0,0,0,0)", "padding": "20px"}
                    ),
                    html.Div(
                        html.Iframe(
                        id="player-1",  # We need an ID to target this with a callback
                        src="https://open.spotify.com/embed/track/2plbrEY59IikOBgBGLjaoe", # Initial song (some bruno mars bs)
                        style={
                            "height": "80px", # Spotify compact players look good at 80px or 152px
                            "width": "100%", 
                            "border": "0",    # Removes the ugly default border
                            "borderRadius": "12px" # makes it look modern
                            }
                            )

                    ),
                    html.Div(
                        dcc.Dropdown(
                            id="song-2-dropdown",
                            options=song_options,
                            value=available_songs[1][1] if len(available_songs) > 1 else available_songs[0][1],
                            style={"color": "black"}
                        ),
                        style={"background": "rgba(0,0,0,0)", "padding": "20px"}
                    ),
                    html.Div(
                        html.Iframe(
                        id="player-2",  # We need an ID to target this with a callback
                        src="https://open.spotify.com/embed/track/2plbrEY59IikOBgBGLjaoe", # Initial song (some bruno mars bs)
                        style={
                            "height": "80px", # Spotify compact players look good at 80px or 152px
                            "width": "100%", 
                            "border": "0",    # Removes the ugly default border
                            "borderRadius": "12px" # makes it look modern
                            }
                            )
                    ),
                    html.Div(
                        dcc.Graph(id="spider-graph", figure=draw_figure(topbar_tab, decades_list, current_decade, song1=available_songs[0][1], song2=available_songs[1][1])),
                        style={
                            "background": "rgba(0,0,0,0)",  # Transparent background for the graph container
                            "padding": "20px",
                            "gridColumn": "1 / -1",  # Span across all columns in the second row
                        },
                    ),
                ],
            )
        else:
            pane = f"You have selected Topbar Tab: {topbar_tab} and Sidebar Tab: {current_decade}, The layout you specified ({layout}) is not yet implemented"
    elif topbar_tab == "topic-4":
        if layout == "grid":
            pane = html.Div(
                style={
                    "padding": "30px",
                    "display": "grid",
                    "gridTemplateColumns": "1fr 1fr",
                    "gridTemplateRows": "1fr 1fr",
                    "gridGap": "30px",
                    "background": "rgba(0,0,0,0)"
                },
                children=[
                    html.Div(create_decade_card(current_decade), style={"background": "rgba(0,0,0,0)", "padding": "20px"}),
                    html.Div("Future visualization", style={"background": "rgba(0,0,0,0)", "padding": "20px"}),
                    html.Div(dcc.Graph(figure=draw_change(current_decade, genre_counts, "asc")), style={"background": "rgba(0,0,0,0)", "padding": "20px"}),
                    html.Div(dcc.Graph(figure=draw_change(current_decade, genre_counts, "desc")), style={"background": "rgba(0,0,0,0)", "padding": "20px"}),
                ],
            )
        else:
            pane = f"Layout {layout} not implemented for topic-4"
    else:
        if layout == "grid":
            pane = html.Div(
                style={
                    "padding": "30px",
                    "display": "grid",
                    "gridTemplateColumns": "1fr 1fr",  # 2 equal columns
                    "gridTemplateRows": "1fr 1fr",  # 2 equal rows
                    "gridGap": "30px",
                    "background": "rgba(0,0,0,0)"  # Transparent background for the grid
                },
                children=[
                    html.Div(draw_figure(topbar_tab, decades_list, current_decade), style={"background": "rgba(0,0,0,0)", "padding": "20px"})  # Transparent
                    for i in range(4)
                ],
            )
        else:
            pane = f"You have selected Topbar Tab: {topbar_tab} and Sidebar Tab: {current_decade}, The layout you specified ({layout}) is not yet implemented"
    
    return pane





# Initialize the app
app = Dash(__name__, suppress_callback_exceptions=True) #carefull for debugging we might need to remove this later

# app.layout is the container for everything visual
# Ill try to get the tabbed layout working
# sidebar and topbar too
# The goal is to make a dashboard that scales seemlessly.


# Issue currently. There is some margin the browser seems to add by default
# Need to find a way to remove that margin
# so we wont have a scrollbar
# This is a css issue will add css config in assets folder


## This class takes a list of children/components
app.layout = html.Div(id = "root_container", children=[
    
    #Topbar
    html.Div(children = [
        dcc.Tabs(id="topbar_tabs", value="topic-1", children=[
            dcc.Tab(label="Analysis 1", value="topic-1"),
            dcc.Tab(label="Analysis 2", value="topic-2"),
            dcc.Tab(label="Compare/Listen", value="topic-3"),
            dcc.Tab(label="Changes", value="topic-4")
        ])
    ], #TODO fix the dimensions of the tabs this can be done by disabeling mobile mode
             style={"background" : "#3D2C2C", "flexDirection" : "column"}), #careful height topbar depends on height of dcc.tabs

    dcc.Store(id='selected_decades', data=[]),

    # Horizontal Pane
    html.Div(children = [
        #Sidebar
        html.Div(children = [
            dcc.Tabs(id="sidebar_tabs", vertical = True, value="20s", children=[
                dcc.Tab(label="50s", value="50s"),
                dcc.Tab(label="60s", value="60s"),
                dcc.Tab(label="70s", value="70s"),
                dcc.Tab(label="80s", value="80s"),
                dcc.Tab(label="90s", value="90s"),
                dcc.Tab(label="00s", value="00s"),
                dcc.Tab(label="10s", value="10s"),
                dcc.Tab(label="20s", value="20s"),
            ])
    ], 
             style={"background" : "#3D2C2C", "height": "100vh"}), #Sidebar style
        
        #Main content area
        html.Div(id="content_area", children = "Here we will put the Main content area", style={"flex" : "1"}) #Flex 1 to take up all remaining space,
    ],
    #Options
    style={"display" : "flex", "flexDirection" : "row", "flex" : "1" } #flex 1 take up all remaining space but will not overrule total size of root container
    ),

    #Bottom bar (Credits logos and so on)
    html.Div("Here we will put the Bottom bar", style = {"background" : "#5B5757"})
]
#Options
, style={"display" : "flex", "flexDirection" : "column", "height" : "100vh", "width" : "100vw" } #currently takes 100% of avaialble viewport height This might be stupid
)

#---------------------------------------------------------------------------#
# Callback to update content area based on selected tab
@app.callback(
    Output(component_id="content_area", component_property="children"),
    Output(component_id="root_container", component_property="style"),
    Output(component_id="selected_decades", component_property="data"),
    Input(component_id="topbar_tabs", component_property="value"),
    Input(component_id="sidebar_tabs", component_property="value"),
    State(component_id="selected_decades", component_property="data"),
)

# The order of the parameters is always the same as the order of the Inputs
# just keep that in mind if you add more Inputs
def render_content(topbar_tab_value, sidebar_tab_value, selected_decades):
    # This function takes the Input value as an argument

    selected_decades = selected_decades or []
    if sidebar_tab_value not in selected_decades:
        selected_decades.append(sidebar_tab_value)

    #This is for changing the background image depending on what decade is selected
    filename = sidebar_tab_value + ".png"
    root_style = {"display" : "flex", "flexDirection" : "column", "height" : "100vh", "width" : "100vw", 
                  "backgroundImage": f"url('/assets/{filename}')", 
                  "background-size": "cover",
                  "background-position": "center",
                  "background-repeat": "no-repeat"
                 }
    
    return draw_pane(topbar_tab_value, selected_decades, sidebar_tab_value), root_style, selected_decades

#------------------------------------------------------------------------#
# Listen/Spider Tab
@app.callback(
    Output(component_id="spider-graph", component_property="figure"),
    Input(component_id="song-1-dropdown", component_property="value"),
    Input(component_id="song-2-dropdown", component_property="value"),
    Input(component_id="sidebar_tabs", component_property="value"),
)
def update_spider_graph(song1, song2, decade):
    if song1 and song2:
        figure = draw_spider(decade, song1, song2)
        return figure
    return {}

@app.callback(
    Output(component_id="player-1", component_property="src"),
    Input(component_id="song-1-dropdown", component_property="value")
)
def update_player_1(track_id):
    if not track_id:
        return "" # Return empty if no song selected
    
    # Spotify embed structure: https://open.spotify.com/embed/track/{ID}
    return f"https://open.spotify.com/embed/track/{track_id}"

@app.callback(
    Output(component_id="player-2", component_property="src"),
    Input(component_id="song-2-dropdown", component_property="value")
)
def update_player_2(track_id):
    if not track_id:
        return "" # Return empty if no song selected
    
    # Spotify embed structure: https://open.spotify.com/embed/track/{ID}
    return f"https://open.spotify.com/embed/track/{track_id}"

# Run the app
if __name__ == "__main__":
    app.run(debug=True, port = 8052)
