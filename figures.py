# This draws the actual plots 
# it takes the selected topbar and produces the figure accordingly
# adjusts the figure based on the sidebar selection as well
def draw_figure(topbar_tab, sidebar_tab):
    if topbar_tab == "topic-3":
        figure = draw_spider(sidebar_tab)  # Use the draw_spider function for topic-3
    else:
        placeholder_figure = f"This is where {topbar_tab} / {sidebar_tab} figure will be drawn"
        figure = placeholder_figure

    return figure


# Spider graph placeholder
def draw_spider(sidebar_tab):
    return f"Placeholder spider graph for {sidebar_tab}"