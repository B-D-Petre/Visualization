import plotly.graph_objects as go
import plotly.express as px
import plotly.colors as pcolors
from src.data.loader import data_loader
import pandas as pd

# --- CONSTANTS ---
PAPER_BG = 'rgba(30, 30, 40, 0.7)'
INK_COLOR = 'white'
FONT_FAMILY = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
CATEGORIES = ["Energy", "Danceability", "Valence", "Acousticness", "Instrumentalness", "Tempo"]
CATEGORY_LABELS = [c[0] for c in CATEGORIES]
LABEL_COLORS = ["#FF6B6B", "#DA77F2", "#FFD93D", "#6BCB77", "#4D96FF", "#F1C40F"]

GENRE_COLOR_MAP = {}
DECADE_RGB = {'50s': (255, 0, 0), '60s': (255, 165, 0), '70s': (255, 255, 0), '80s': (0, 128, 0), 
              '90s': (0, 0, 255), '00s': (75, 0, 130), '10s': (238, 130, 238), '20s': (128, 0, 128)}

def _init_colors():
    """Initializes the genre color map based on available genres."""
    genres = data_loader.get_genres()
    colors = pcolors.qualitative.Plotly * 5
    for i, genre in enumerate(genres):
        GENRE_COLOR_MAP[genre] = colors[i % len(colors)]
_init_colors()

def _style_fig(fig):
    fig.update_layout(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_FAMILY, color=INK_COLOR),
        title_font=dict(size=20, family=FONT_FAMILY),
        margin=dict(t=50, l=20, r=20, b=20),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.1)")
    )
    return fig

def get_empty_figure(text="Data Unavailable"):
    fig = go.Figure()
    fig.add_annotation(text=text, showarrow=False, font=dict(color="white", size=20))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig

# --- SPIDER GRAPHS ---

def draw_spider_comparison(decade, song1_id, song2_id, show_genre1=False, show_genre2=False):
    spider_data = data_loader.spider_data
    if spider_data.empty: return get_empty_figure("No Data")

    filtered = spider_data[spider_data['decade'] == decade]
    s1_row = filtered[filtered['track_id'] == song1_id]
    s2_row = filtered[filtered['track_id'] == song2_id]

    if s1_row.empty or s2_row.empty: return get_empty_figure("Select Songs")

    def _get_vals(row):
        vals = []
        for cat in CATEGORIES:
            val = row[cat].values[0] if cat in row.columns else 0
            vals.append(val)
        return vals

    vals1 = _get_vals(s1_row)
    vals2 = _get_vals(s2_row)
    
    name1 = s1_row['track_name'].values[0]
    name2 = s2_row['track_name'].values[0]
    genre1 = s1_row['playlist_genre'].values[0] if 'playlist_genre' in s1_row.columns else "?"
    genre2 = s2_row['playlist_genre'].values[0] if 'playlist_genre' in s2_row.columns else "?"

    fig = go.Figure()
    
    # Trace 1
    fig.add_trace(go.Scatterpolar(
        r=vals1, theta=CATEGORIES, fill='toself', name=f"{name1} ({genre1})", line_color='#636EFA'
    ))
    # Trace 2
    fig.add_trace(go.Scatterpolar(
        r=vals2, theta=CATEGORIES, fill='toself', name=f"{name2} ({genre2})", line_color='#EF553B'
    ))

    # Averages
    if show_genre1:
        g1_avg = filtered[filtered['playlist_genre'] == genre1][CATEGORIES].mean().tolist()
        fig.add_trace(go.Scatterpolar(r=g1_avg, theta=CATEGORIES, name=f"Avg {genre1}", line=dict(dash='dash', color='#636EFA'), fill=None))
    
    if show_genre2:
        g2_avg = filtered[filtered['playlist_genre'] == genre2][CATEGORIES].mean().tolist()
        fig.add_trace(go.Scatterpolar(r=g2_avg, theta=CATEGORIES, name=f"Avg {genre2}", line=dict(dash='dash', color='#EF553B'), fill=None))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], gridcolor="rgba(255,255,255,0.1)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
            bgcolor="rgba(30,30,40,0.7)"
        ),
        showlegend=True,
        title=dict(text=f"{name1} vs {name2}", font=dict(color="white")),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"),
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def draw_spider_average(decade, selected_genres=None):
    """Draws the small honeycomb spider graph."""
    spider_data = data_loader.spider_data
    if spider_data.empty: return get_empty_figure()

    filtered = spider_data[spider_data['decade'] == decade]
    if selected_genres:
        filtered = filtered[filtered['playlist_genre'].isin(selected_genres)]

    # Calculate Average
    if filtered.empty:
        vals = [0] * len(CATEGORIES)
    else:
        vals = filtered[CATEGORIES].mean().tolist()

    # Color
    rgb = DECADE_RGB.get(decade, (128, 128, 128))
    fill_color = f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.2)'
    line_color = f'rgb({rgb[0]}, {rgb[1]}, {rgb[2]})'

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals, theta=CATEGORY_LABELS, fill='toself',
        line=dict(color=line_color), fillcolor=fill_color
    ))
    
    # Outer labels ring
    fig.add_trace(go.Scatterpolar(
        r=[1.45]*6, theta=CATEGORY_LABELS, mode="text", text=CATEGORY_LABELS,
        textfont=dict(color=LABEL_COLORS, size=14, family="Arial Black"),
        hoverinfo="skip"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1.6], showticklabels=False, gridcolor="rgba(255,255,255,0.2)"),
            bgcolor="rgba(0,0,0,0)",
            angularaxis=dict(rotation=90, direction="clockwise", showticklabels=False, gridcolor="rgba(255,255,255,0.2)")
        ),
        showlegend=False,
        title=dict(text=decade, font=dict(color="white", size=12)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=30, b=20)
    )
    return fig

# --- AREA PLOTS (TOPIC 1) ---

def draw_feature_area_plots(decade, selected_genres):
    import plotly.subplots as sp
    
    base_data = data_loader.spider_data
    if base_data.empty: return get_empty_figure("No Data")
    
    features = ["Energy", "Tempo", "Danceability", "Loudness", "Valence"] # Reduced for perf
    # Ensure they exist
    available = [f for f in features if f in base_data.columns]
    
    if not selected_genres:
        selected_genres = data_loader.get_genres()[:5] # Limit defaults
        
    fig = sp.make_subplots(rows=len(available), cols=1, subplot_titles=available, shared_xaxes=True, vertical_spacing=0.05)

    base_data['year'] = base_data['year'].astype(int)
    
    for genre in selected_genres:
        g_data = base_data[base_data['playlist_genre'] == genre]
        if g_data.empty: continue
        
        grouped = g_data.groupby('year')[available].mean().reset_index().sort_values('year')
        color = GENRE_COLOR_MAP.get(genre, '#888')

        for i, feat in enumerate(available):
            fig.add_trace(go.Scatter(
                x=grouped['year'], y=grouped[feat], mode='lines', 
                name=genre, line=dict(color=color), showlegend=(i==0),
                legendgroup=genre
            ), row=i+1, col=1)

    fig.update_layout(
        height=600, 
        paper_bgcolor=PAPER_BG, plot_bgcolor=PAPER_BG, 
        font=dict(color=INK_COLOR),
        margin=dict(t=40, b=40, l=40, r=40),
        legend=dict(orientation="h", y=1.02, x=1, xanchor="right")
    )
    return fig

# --- TRENDS & CHANGES (TOPIC 4) ---

def draw_genre_trends_line():
    df = data_loader.genre_year_counts
    if df.empty: return get_empty_figure("No Trend Data")
    
    df = df[(df['year'] >= 1950) & (df['year'] <= 2030)]
    
    fig = px.line(df, x='year', y='count', color='playlist_genre', 
                  title="Genre Popularity (1950-2030)",
                  color_discrete_map=GENRE_COLOR_MAP)
    return _style_fig(fig)

def draw_change_chart(decade, direction='desc'):
    # Note: Requires Calculating change. 
    # For now, we'll try to calculate it on the fly or just return empty if prep missing
    # But to save time, I will mock it based on data or implement simple diff
    return get_empty_figure("Change Calc Not Impl")
