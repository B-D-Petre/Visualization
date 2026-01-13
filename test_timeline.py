import pandas as pd
import plotly.graph_objects as go

# Load data
spider_csv_path = "assets/spider_graph_data.csv"
spider_data = pd.read_csv(spider_csv_path)

def draw_timeline(decade):
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
    
    min_date = dates.min()
    max_date = dates.max()
    
    # Create bins every 5 months
    bins = pd.date_range(start=min_date, end=max_date + pd.DateOffset(months=5), freq='5MS')
    
    if len(bins) < 2:
        bins = pd.date_range(start=min_date, periods=2, freq='5MS')
    
    # Bin the dates
    binned = pd.cut(dates, bins=bins, right=False, labels=[f"{b.strftime('%Y-%m')}-{ (b + pd.DateOffset(months=5) - pd.DateOffset(days=1)).strftime('%Y-%m')}" for b in bins[:-1]])
    
    # Count per bin
    counts = binned.value_counts().sort_index()
    
    print(f"Decade: {decade}, Min date: {min_date}, Max date: {max_date}")
    print(f"Bins: {bins}")
    print(f"Counts: {counts}")
    
    # For plotting, x as the bin labels, y as counts
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=counts.index,
        y=counts.values,
        marker_color='white'
    ))
    
    fig.update_layout(
        xaxis=dict(
            title="5-Month Bins",
            tickfont=dict(color='white')
        ),
        yaxis=dict(
            title="Number of Songs",
            tickfont=dict(color='white')
        ),
        height=200,  # adjust height for better visibility
        autosize=True,
        margin=dict(t=10, b=40, l=40, r=20),
        paper_bgcolor="rgba(0,0,0,0.5)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )
    return fig

# Test for 20s
fig = draw_timeline('20s')
# fig.show()
print("Test completed")
