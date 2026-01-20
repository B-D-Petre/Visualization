from dash import Dash, html, dcc, Input, Output, State, MATCH, ALL, Patch
import dash # Needed of callback_context
import os
import webbrowser
from figures import *
import plotly.express as px
import subprocess
import sys
import json

#Get the correct data run preprocessing
subprocess.run([sys.executable, "preprocess.py"])   


#--------------------------------------------------------------------------#
# Main function to actually draw shit
# This function arranges the plots in an html layout
# change layout to whatever makes sense for your tab
def draw_pane(topbar_tab, decades_list, current_decade, layout="grid", bin_size="5 months", selected_genres=None):
    #----------------------------------------------------------------------------#
    # Topic 1
    if topbar_tab == "topic-1":
        content = draw_figure(topbar_tab, decades_list, current_decade, selected_genres=selected_genres)
        pane = html.Div(
            style={
                "height": "100%", "width": "100%",
                "display": "flex"
            },
            children=[content]
        )
    #----------------------------------------------------------------------------#
    # Topic 3 listeing/comparing tab
    elif topbar_tab == "topic-3":
        if layout == "grid": 
            # Get available songs for the selected decade
            available_songs = get_songs_for_decade(current_decade)
            song_options = [{"label": song_name, "value": track_id} for song_name, track_id in available_songs]
            
            pane = html.Div(
                style={
                    "padding": "30px 30px 20px 30px",
                    "display": "flex",
                    "flexDirection": "row",
                    "gap": "20px",
                    "background": "rgba(0,0,0,0)",
                    "height": "100%",
                    "boxSizing": "border-box"
                },
                children=[
                    # Left Column: Song Selectors
                    html.Div(
                        style={"flex": "1", "display": "flex", "flexDirection": "column", "gap": "20px", "height": "100%"},
                        children=[
                            # Song 1 Selection (Top Left)
                            html.Div(
                                style={"flex": "1", "display": "flex", "flexDirection": "column", "gap": "10px", "background": "rgba(30, 30, 40, 0.7)", "padding": "15px", "boxSizing": "border-box", "borderRadius": "0px", "border": "1px solid rgba(255,255,255,0.05)"},
                                children=[
                                    html.H4("Select Song 1", style={"margin": "0 0 5px 0", "color": "white"}), 
                                    dcc.Dropdown(
                                        id="song-1-dropdown",
                                        options=song_options,
                                        value=available_songs[0][1] if available_songs else None,
                                        style={"color": "black"}
                                    ),
                                    # Checkbox for Genre 1 Average
                                    dcc.Checklist(
                                        id='genre-1-avg-checkbox',
                                        options=[{'label': ' Show Genre Average', 'value': 'show'}],
                                        value=[],
                                        style={"color": "white", "fontSize": "0.9em"}
                                    ),
                                    html.Iframe(
                                        id="player-1",
                                        src="https://open.spotify.com/embed/track/2plbrEY59IikOBgBGLjaoe", 
                                        style={
                                            "height": "80px", 
                                            "width": "100%", 
                                            "flex": "1", # Fill remaining vertical space?
                                            "border": "0",
                                            "borderRadius": "0px"
                                        }
                                    )
                                ]
                            ),
                            
                            # Song 2 Selection (Bottom Left)
                            html.Div(
                                 style={"flex": "1", "display": "flex", "flexDirection": "column", "gap": "10px", "background": "rgba(30, 30, 40, 0.7)", "padding": "15px", "boxSizing": "border-box", "borderRadius": "0px", "border": "1px solid rgba(255,255,255,0.05)"},
                                 children=[
                                    html.H4("Select Song 2", style={"margin": "0 0 5px 0", "color": "white"}),
                                    dcc.Dropdown(
                                        id="song-2-dropdown",
                                        options=song_options,
                                        value=available_songs[1][1] if len(available_songs) > 1 else available_songs[0][1],
                                        style={"color": "black"}
                                    ),
                                    # Checkbox for Genre 2 Average
                                    dcc.Checklist(
                                        id='genre-2-avg-checkbox',
                                        options=[{'label': ' Show Genre Average', 'value': 'show'}],
                                        value=[],
                                        style={"color": "white", "fontSize": "0.9em"}
                                    ),
                                    html.Iframe(
                                        id="player-2",
                                        src="https://open.spotify.com/embed/track/2plbrEY59IikOBgBGLjaoe", 
                                        style={
                                            "height": "80px", 
                                            "width": "100%", 
                                            "flex": "1",
                                            "border": "0",
                                            "borderRadius": "0px"
                                        }
                                    )
                                ]
                            )
                        ]
                    ),
                    
                    # Spider Graph Area (Right Column)
                    html.Div(
                        dcc.Graph(
                            id="spider-graph", 
                            figure=draw_figure(topbar_tab, decades_list, current_decade, song1=available_songs[0][1], song2=available_songs[1][1]),
                            style={"flex": "1", "width": "100%", "height": "100%"}
                        ),
                        style={
                            "flex": "1",
                            "display": "flex",
                            "flexDirection": "column",
                            "height": "100%",
                            "background": "rgba(30, 30, 40, 0.7)",  # Matching background
                            "padding": "20px",
                            "boxSizing": "border-box",  # Fix overflow from padding
                            "borderRadius": "0px",
                            "border": "1px solid rgba(255,255,255,0.05)",
                            "minHeight": "0"
                        },
                    ),
                ],
            )
        else:
            pane = f"You have selected Topbar Tab: {topbar_tab} and Sidebar Tab: {current_decade}, The layout you specified ({layout}) is not yet implemented"
    elif topbar_tab == "topic-4":
        pane = draw_figure(topbar_tab, decades_list, current_decade)
    
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



#---------------------------------------------------------------------------#
# Actual HTML Layout

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
        dcc.Tabs(id="topbar_tabs", value="topic-1", 
            parent_style={"flexDirection": "row", "width": "100%"},
            children=[
            dcc.Tab(label="The Music", value="topic-1", className="top-tab", selected_className="top-tab--selected"),
            dcc.Tab(label="The Charts", value="topic-4", className="top-tab", selected_className="top-tab--selected"),
            dcc.Tab(label="The Spotlight", value="topic-3", className="top-tab", selected_className="top-tab--selected")
        ])
    ], 
             style={"background" : "rgba(20, 22, 35, 0.95)", "flexDirection" : "column", "borderBottom": "1px solid rgba(255,255,255,0.1)", "boxShadow": "0 4px 15px rgba(0,0,0,0.3)", "zIndex": "1001"}), 


    dcc.Store(id='selected_decades', data=[]),
    dcc.Store(id='bin_size', data='5 months'),
    dcc.Store(id='previous_decade', data=None),
    dcc.Store(id='animation_trigger', data=0),
    dcc.Store(id='selected_genres_store', data=None),

    # Horizontal Pane
    html.Div(children = [
        # Main content area
        html.Div(id="content_area", children = "Loading...", style={"flex" : "1", "position": "relative", "overflow": "hidden", "height": "100%"}), # Added height 100%
    ],
    #Options
    style={"display" : "flex", "flexDirection" : "column", "flex" : "1", "minHeight": "0", "overflow": "hidden", "position": "relative"} 
    ),

    # Decade selection (Bottom Bar)
    html.Div(children = [
        dcc.Tabs(id="sidebar_tabs", vertical=False, value="20s", 
            parent_style={"flexDirection": "row", "justifyContent": "center"}, # Center tabs
            children=[
            dcc.Tab(label="50s", value="50s", className="decade-tab", selected_className="decade-tab--selected"),
            dcc.Tab(label="60s", value="60s", className="decade-tab", selected_className="decade-tab--selected"),
            dcc.Tab(label="70s", value="70s", className="decade-tab", selected_className="decade-tab--selected"),
            dcc.Tab(label="80s", value="80s", className="decade-tab", selected_className="decade-tab--selected"),
            dcc.Tab(label="90s", value="90s", className="decade-tab", selected_className="decade-tab--selected"),
            dcc.Tab(label="00s", value="00s", className="decade-tab", selected_className="decade-tab--selected"),
            dcc.Tab(label="10s", value="10s", className="decade-tab", selected_className="decade-tab--selected"),
            dcc.Tab(label="20s", value="20s", className="decade-tab", selected_className="decade-tab--selected"),
        ])
    ], 
    style={
        "width": "100%", 
        "padding": "20px",  
        "background": "rgba(20, 22, 35, 0.95)",
        "borderTop": "1px solid rgba(255,255,255,0.1)",
        "boxShadow": "0 -4px 15px rgba(0,0,0,0.3)",
        "display": "flex",
        "justifyContent": "center",
        "zIndex": "1000",
        "flexShrink": 0,
        "fontSize": "1.5em"
    })
]
#Options
, style={"display" : "flex", "flexDirection" : "column", "height" : "100vh", "width" : "100vw", "backgroundColor": "#011F26"} # Fixed background color
)

#---------------------------------------------------------------------------#
# Callback to update content area based on selected tab
@app.callback(
    Output(component_id="content_area", component_property="children"),
    Output(component_id="root_container", component_property="style"),
    Output(component_id="selected_decades", component_property="data"),
    Output(component_id="previous_decade", component_property="data"),
    Output(component_id="animation_trigger", component_property="data"),
    Input(component_id="topbar_tabs", component_property="value"),
    Input(component_id="sidebar_tabs", component_property="value"),
    #States are pseudo callbacks does not run the callback but instead only provides the data
    #THIS FASTER
    State(component_id="selected_decades", component_property="data"),
    State(component_id="bin_size", component_property="data"),
    State(component_id="previous_decade", component_property="data"),
    State(component_id="animation_trigger", component_property="data"),
    State(component_id="selected_genres_store", component_property="data"),
    allow_duplicate=True
)

# The order of the parameters is always the same as the order of the Inputs
# just keep that in mind if we add more Inputs
def render_content(topbar_tab_value, sidebar_tab_value, selected_decades, bin_size, previous_decade, animation_trigger, selected_genres):
    
    # This function takes the Input value as an argument
    selected_decades = selected_decades or []
    if sidebar_tab_value not in selected_decades:
        selected_decades.append(sidebar_tab_value)

    # Check if decade changed
    decade_changed = sidebar_tab_value != previous_decade
    if decade_changed:
        animation_trigger = (animation_trigger or 0) + 1


    root_style = {
        "display" : "flex", 
        "flexDirection" : "column", 
        "height" : "100vh", 
        "width" : "100vw",
        "backgroundColor": "#01191e"
    }

    return draw_pane(topbar_tab_value, selected_decades, sidebar_tab_value, bin_size=bin_size, selected_genres=selected_genres), root_style, selected_decades, sidebar_tab_value, animation_trigger

# Callback to remember selected genres
@app.callback(
    Output("selected_genres_store", "data"),
    Input("genre-dropdown", "value"),
    prevent_initial_call=True
)
def save_selected_genres(genres):
    return genres

# Callback for genre selector in tab 1. Spider graph and feature line plots
@app.callback(
    Output("spider-graphs-container", "children"),
    Output("analysis1-area", "figure"),
    Output("rate-of-change-barplot", "figure"),
    Input("genre-dropdown", "value"),
    Input("breakdown-checkbox", "value"),
    State("sidebar_tabs", "value"),
)


def update_analysis1(selected_genres, breakdown_value, current_decade):
    show_breakdown = bool(breakdown_value and 'show' in breakdown_value)
    
    #not really used anymore but cba
    bin_size = "1 year"# Need this to display level of aggregation in line plots
    
    
    # Only use the current decade, not accumulated decades
    decades_list = [current_decade]
    
    # Generate list of spider graphs for the grid
    spider_graphs_children = []
    
    if selected_genres:
        
        num_genres = len(selected_genres)
        
        
        base_w = 260
        base_h = 280
        base_m_vert = -20
        base_m_horz = -5
        
        # change spider scale based on number of genres / amount of plots we need to draw so everything fits
        scale = 1.0
        if num_genres > 15:
            scale = 0.55
        elif num_genres > 9:
            scale = 0.65
        elif num_genres > 4:
            scale = 0.8

        s_w = int(base_w * scale)
        s_h = int(base_h * scale)
        s_m_v = int(base_m_vert * scale)
        s_m_h = int(base_m_horz * scale)
        s_font = max(6, int(14 * scale))
        

        # switch background colours between graphs - better readablility
        bg_colors = [
            "rgba(60, 65, 90, 0.7)",
            "rgba(75, 80, 105, 0.7)"
        ]
        
        # insert breaks for 3-2-3-2 pattern
        current_row_len = 0
        target_row_len = 3 # Start with 3 items in first row
        

        # Make colour rotation for plots        
        for i, genre in enumerate(selected_genres):
            # alternating background color
            bg_color = bg_colors[i % len(bg_colors)]
            

            line_color = GENRE_COLOR_MAP.get(genre, '#888888')
            
            cell_style_override = {
                "width": f"{s_w}px",
                "height": f"{s_h}px",
                "margin": f"{s_m_v}px {s_m_h}px",
                "backgroundColor": bg_color
            }

            # Generate spider graph for this specific genre
            # We reuse draw_spider_analysis1 but pass only [genre] to filter, and pass the color
            fig = draw_spider_analysis1(decades_list, current_decade, selected_genres=[genre], override_color=line_color)
            
            fig.update_layout(
                # title=dict(text=f"{genre.title()}", font=dict(size=s_font, color=line_color), y=0.95), 
                margin=dict(l=20*scale, r=20*scale, t=25*scale, b=25*scale),
                height=s_h, # Match container height
                font=dict(size=max(8, 10*scale)) # Scale axis labels too
            )
            
            spider_graphs_children.append(
                html.Div(
                    className="honeycomb-cell",
                    style=cell_style_override,
                    children=[
                        html.Div(f"{genre.title()}", className="honeycomb-title", style={"color": "white"}),
                        dcc.Graph(
                            id={'type': 'spider-genre', 'index': genre},
                            figure=fig, 
                            config={'displayModeBar': False},
                            style={"height": "100%", "width": "100%"}
                        )
                    ]
                )
            )
            
            # Stack graphs. 
            current_row_len += 1
            if current_row_len == target_row_len and i < len(selected_genres) - 1:
                 spider_graphs_children.append(
                     html.Div(style={"flexBasis": "100%", "height": "0", "margin": "0", "padding": "0"})
                 )
                 # pattern: 3 -> 2 -> 3 -> 2
                 target_row_len = 2 if target_row_len == 3 else 3
                 current_row_len = 0
    else:
        # Fallback: Show overall average if no genres selected
        fig = draw_spider_analysis1(decades_list, current_decade)
        fig.update_layout(title="All Genres Average", height=300)
        spider_graphs_children.append(
            html.Div(
                className="honeycomb-cell",
                children=[dcc.Graph(figure=fig, style={"height": "100%", "width": "100%"})]
            )
        )
    
    area_fig = draw_area_plots(
        decades_list, 
        current_decade, 
        features=["Energy", "Danceability", "Loudness", "Acousticness", "Valence", "Duration", "Liveness"],
        bin_size=bin_size,
        selected_genres=selected_genres
    )
    
    barplot_fig = draw_rate_of_change_barplot(current_decade, selected_genres, show_breakdown=show_breakdown)
    
    return spider_graphs_children, area_fig, barplot_fig

# Callback for making spider graphs clickable
@app.callback(
    Output("analysis1-area", "figure", allow_duplicate=True),
    Input({'type': 'spider-genre', 'index': ALL}, 'clickData'),
    State("analysis1-area", "figure"),
    prevent_initial_call=True
)
def update_area_highlight(click_data_list, current_figure):
    # figoure out which graph triggered the click
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    # dont run callback in case no data was cliecked
    if not any(click_data_list):
        return dash.no_update

    # get genre ID
    triggered_prop_id = ctx.triggered[0]['prop_id']
    
    try:
        # prop_id looks like '{"index":"pop","type":"spider-genre"}.clickData'
        prop_id_dict = json.loads(triggered_prop_id.split('.')[0])
        clicked_genre = prop_id_dict['index']
        
        #Makes it faster will run on client
        patched_figure = Patch()
        

        #Highlight the selected genre in line plot
        for i, trace in enumerate(current_figure['data']):
             if 'name' in trace:
                 # Is trace is the one we clicked?
                 if trace['name'] == clicked_genre.title():
                     patched_figure['data'][i]['line']['width'] = 5
                     patched_figure['data'][i]['opacity'] = 1.0
                 else:
                     patched_figure['data'][i]['line']['width'] = 2
                     patched_figure['data'][i]['opacity'] = 0.2
                     
        return patched_figure
            
    except Exception as e:
        print(f"Error in update_area_highlight: {e}")
        return dash.no_update

#------------------------------------------------------------------------#
# Listen/Spider Tab
@app.callback(
    Output(component_id="spider-graph", component_property="figure"),
    Input(component_id="song-1-dropdown", component_property="value"),
    Input(component_id="song-2-dropdown", component_property="value"),
    Input(component_id="genre-1-avg-checkbox", component_property="value"),
    Input(component_id="genre-2-avg-checkbox", component_property="value"),
    State(component_id="sidebar_tabs", component_property="value"),
)
def update_spider_graph(song1, song2, show_genre1_list, show_genre2_list, decade):
    show_genre1 = bool(show_genre1_list)
    show_genre2 = bool(show_genre2_list)
    if song1 and song2:
        figure = draw_spider(decade, song1, song2, show_genre1, show_genre2)
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

# Callback for timeline tab2
@app.callback(
    Output("timeline-graph", "figure"),
    Input("bin-size-dropdown", "value"),
    Input("sidebar_tabs", "value"),
)
def update_timeline(bin_size, decade):
    return draw_timeline(decade, bin_size)

# Callback bin size
@app.callback(
    Output("bin_size", "data"),
    Input("bin-size-dropdown", "value")
)
def update_bin_size(value):
    return value

# Callback line plots
@app.callback(
    Output('area-plots-graph', 'figure'),
    Input('bin-size-dropdown', 'value'),
    Input('sidebar_tabs', 'value'),
    State('selected_decades', 'data')
)
def update_area_opacity(bin_size, decade, selected_decades):
    figure = draw_area_plots(selected_decades, decade, features=["Energy", "Danceability", "Loudness", "Acousticness", "Valence", "Duration", "Liveness"], bin_size=bin_size)
    return figure

# Callback Analysis 1 Legend Toggle
@app.callback(
    Output("analysis1-legend-content", "style"),
    Input("analysis1-legend-trigger", "n_clicks"),
    prevent_initial_call=True
)
def toggle_legend(n_clicks):
    if n_clicks and n_clicks % 2 == 1:
        # Expanded State: Relative positioning forces the parent container to expand
        return {
            "visibility": "visible", 
            "opacity": 1,
            "display": "block",
            "position": "relative", 
            "top": "0", 
            "left": "0", 
            "transform": "none", 
            "width": "100%", 
            "marginTop": "10px",
            "boxShadow": "none",
            "border": "none",
            "backgroundColor": "transparent" # Blend in with the container
        }
    else:
        return {
            "display": "none"
        }


if __name__ == "__main__":
    app.run(debug=True, port = 8052)
