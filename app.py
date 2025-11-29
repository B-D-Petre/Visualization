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
        html.Div("Here we will put the Sidebar", style={"background" : "#1C0D0D", "width" : "200px"}), #Fixed width sidebar
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







# Run the app
if __name__ == "__main__":
    app.run(debug=True)