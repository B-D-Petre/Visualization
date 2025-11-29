from dash import Dash, html, dcc, Input, Output


# Initialize the app
app = Dash(__name__)

# app.layout is the container for everything visual
# Ill try to get the tabbed layout working
# sidebar and topbar too
# The goal is to make a dashboard that scales seemlessly.


# Issue currently. There is some margin the browser seems to add by default
# Need to find a way to remove that margin
# so we wont have a scrollbar
# This is a css issue will add css config in assets folder


## This class takes a list of children/components
app.layout = html.Div(children=[
    
    #Topbar
    html.Div(children = [
        dcc.Tabs(id="topbar_tabs", value="topic-1", children=[
            dcc.Tab(label="Home", value="topic-1"),
            dcc.Tab(label="Compare", value="topic-2"),
            dcc.Tab(label="Listen", value="topic-3"),
        ])
    ], #TODO fix the dimensions of the tabs this can be done by disabeling mobile mode
             style={"background" : "#3D2C2C", "flexDirection" : "column"}), #careful height topbar depends on height of dcc.tabs

    # Horizontal Pane
    html.Div(children = [
        #Sidebar
        html.Div(children = [
            dcc.Tabs(id="sidebar_tabs", value="80s", children=[
                dcc.Tab(label="80s", value="80s"),
                dcc.Tab(label="90s", value="90s"),
                dcc.Tab(label="00s", value="00s"),
                dcc.Tab(label="10s", value="10s"),
            ])
    ], 
             style={"background" : "#3D2C2C", "flexDirection" : "row"}), #Sidebar style
        
        #Main content area
        html.Div(id="content_area", children = "Here we will put the Main content area", style={"background" : "#5B5757", "flex" : "1"}) #Flex 1 to take up all remaining space,
    ],
    #Options
    style={"display" : "flex", "flexDirection" : "row", "flex" : "1" } #flex 1 take up all remaining space but will not overrule total size of root container
    ),

    #Bottom bar (Credits logos and so on)
    html.Div("Here we will put the Bottom bar")
]
#Options
, style={"display" : "flex", "flexDirection" : "column", "height" : "100vh", "width" : "100vw" } #currently takes 100% of avaialble viewport height This might be stupid
)


# Callback to update content area based on selected tab
@app.callback(
    Output(component_id="content_area", component_property="children"),
    Input(component_id="topbar_tabs", component_property="value"),
    Input(component_id="sidebar_tabs", component_property="value"),
)
# If I remeber correctly the order of the parameters is the same as the order of the Inputs
# Its a bit stupid
def render_content(topbar_tab_value, sidebar_tab_value):
    # This function takes the Input value as an argument
    return f"You selected Topbar Tab: {topbar_tab_value} and Sidebar Tab: {sidebar_tab_value}"








# Run the app
if __name__ == "__main__":
    app.run(debug=True)
