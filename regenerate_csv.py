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
spotify_combined["track_album_release_date"] = pd.to_datetime(spotify_combined["track_album_release_date"], format="mixed")
spotify_combined['year'] = spotify_combined['track_album_release_date'].dt.year
spotify_combined['decade'] = (spotify_combined['year'] // 10) * 10

# Define features
raw_features = ["energy", "danceability", "valence", "acousticness", "instrumentalness"]

# Create subset
metadata_cols = ['track_name', 'track_artist', 'decade', 'track_id', 'year', 'track_album_release_date']
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
