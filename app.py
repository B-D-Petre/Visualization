from dash import Dash, html, dcc, Input, Output
from figures import *

 
# This function arranges the plots in an html layout
def draw_pane(topbar_tab, sidebar_tab, layout="grid"):
    # Here we would have the logic to draw different content based on the selected tabs

    if layout == "grid":
        pane = html.Div(
            style={
                "padding": "30px",
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr", #2 equal columns
                "gridTemplateRows": "1fr 1fr", #2 equal rows
                "gridGap": "30px",
            },
            children=[
                html.Div(f"{draw_figure(topbar_tab, sidebar_tab)}", style={"background": "#ccc", "padding": "20px"})
                for i in range(4)
            ],
        )
    else:
        pane = f"You have selected Topbar Tab: {topbar_tab} and Sidebar Tab: {sidebar_tab}"
    return pane





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
app.layout = html.Div(id = "root_container", children=[
    
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
            dcc.Tabs(id="sidebar_tabs", value="20s", children=[
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
    Output(component_id="root_container", component_property="style"),
    Input(component_id="topbar_tabs", component_property="value"),
    Input(component_id="sidebar_tabs", component_property="value"),
)

# The order of the parameters is always the same as the order of the Inputs
# just keep that in mind if you add more Inputs
def render_content(topbar_tab_value, sidebar_tab_value):
    # This function takes the Input value as an argument
    return draw_pane(topbar_tab_value, sidebar_tab_value)



# Run the app
if __name__ == "__main__":
    app.run(debug=True)
