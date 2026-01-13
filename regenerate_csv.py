import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd
import os

# Load data
file_paths = ["high_popularity_spotify_data.csv", "low_popularity_spotify_data.csv"]
database = []

for file_path in file_paths:
    df = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        "solomonameh/spotify-music-dataset",
        file_path,
    )
    database.append(df)

spotify_combined = pd.concat(database, ignore_index=True)

# Preprocess
spotify_combined["track_album_release_date"] = pd.to_datetime(spotify_combined["track_album_release_date"], format="mixed", errors='coerce')
spotify_combined['year'] = spotify_combined['track_album_release_date'].dt.year

# --- FIX RE-RELEASE DATES ---
import re
def clean_track_name(name):
    if not isinstance(name, str): return str(name)
    # Be aggressive in cleaning remaster/version info
    name = re.sub(r' - .*Remaster.*', '', name, flags=re.IGNORECASE)
    name = re.sub(r' \(.*Remaster.*\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r' - .*Version.*', '', name, flags=re.IGNORECASE)
    name = re.sub(r' \(.*Version.*\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r' - .*Mix.*', '', name, flags=re.IGNORECASE)
    return name.strip()

spotify_combined['clean_name'] = spotify_combined['track_name'].apply(clean_track_name)

# Find the minimum year for each (clean_name, artist) pair
min_years = spotify_combined.groupby(['clean_name', 'track_artist'])['year'].min().reset_index()
min_years = min_years.rename(columns={'year': 'original_year'})

# Merge back to original dataframe
spotify_combined = pd.merge(spotify_combined, min_years, on=['clean_name', 'track_artist'], how='left')

# Update year and create decade from original_year
# If original_year is NaN (shouldn't be), fallback to year
spotify_combined['year'] = spotify_combined['original_year'].fillna(spotify_combined['year']).astype(int)
spotify_combined['decade'] = (spotify_combined['year'] // 10) * 10
# ----------------------------

# Define features
raw_features = ["energy", "danceability", "valence", "acousticness", "instrumentalness"]

# Create subset
metadata_cols = ['track_name', 'track_artist', 'decade', 'track_id', 'year', 'track_album_release_date', 'playlist_genre']
df_spider = spotify_combined[metadata_cols + raw_features].copy()

# Normalize
for col in raw_features:
    min_val = df_spider[col].min()
    max_val = df_spider[col].max()
    df_spider[col] = (df_spider[col] - min_val) / (max_val - min_val)

# Format decade
def format_decade(year_int):
    return str(year_int)[-2:] + "s"

df_spider['decade'] = df_spider['decade'].apply(format_decade)

# Rename columns
df_spider.rename(columns={c: c.capitalize() for c in raw_features}, inplace=True)
df_spider = df_spider.drop_duplicates(subset=['track_id'], keep='first')

# Save
output_dir = "assets"
os.makedirs(output_dir, exist_ok=True)
spider_csv_path = os.path.join(output_dir, "spider_graph_data.csv")
df_spider.to_csv(spider_csv_path, index=False)

print(f"Success! Spider graph data saved to {spider_csv_path}")
print(df_spider.head())
