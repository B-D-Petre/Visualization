import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd
import os
import re

print("--- Running regenerate_csv.py ---")
print("Loading assets/main_data_kaggle.csv...")

try:
    main_data = pd.read_csv("assets/main_data_kaggle.csv")
except FileNotFoundError:
    print("Error: assets/main_data_kaggle.csv not found.")
    exit(1)

# --- COLUMN MAPPING FIXES ---
# Ensure we have the standard column names expected by the rest of the app:
# ID -> 'track_id'
# Name -> 'track_name'

# 1. Handle ID Column (uri -> track_id)
if 'track_id' not in main_data.columns:
    if 'uri' in main_data.columns:
        print("Renaming 'uri' column to 'track_id'...")
        main_data.rename(columns={'uri': 'track_id'}, inplace=True)
    else:
        print("Error: Could not find 'track_id' or 'uri' column.")
        exit(1)

# 2. Handle Name Column
if 'track_name' not in main_data.columns:
    print("Error: 'track_name' column missing.")
    exit(1)

print(f"Columns validated. Processing {len(main_data)} rows...")

# Preprocess Dates
main_data["track_album_release_date"] = pd.to_datetime(main_data["track_album_release_date"], format="mixed", errors='coerce')
main_data['year'] = main_data['track_album_release_date'].dt.year

# --- FIX RE-RELEASE DATES ---
def clean_track_name(name):
    if not isinstance(name, str): return str(name)
    # Be aggressive in cleaning remaster/version info
    name = re.sub(r' - .*Remaster.*', '', name, flags=re.IGNORECASE)
    name = re.sub(r' \(.*Remaster.*\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r' - .*Version.*', '', name, flags=re.IGNORECASE)
    name = re.sub(r' \(.*Version.*\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r' - .*Mix.*', '', name, flags=re.IGNORECASE)
    return name.strip()

# Apply to track_name
main_data['clean_name'] = main_data['track_name'].apply(clean_track_name)

# Find the minimum year for each (clean_name, artist) pair
# Note: Using 'track_artist' (from your new dataset)
group_cols = ['clean_name', 'track_artist']
min_years = main_data.groupby(group_cols)['year'].min().reset_index()
min_years = min_years.rename(columns={'year': 'original_year'})

# Merge back to original dataframe
main_data = pd.merge(main_data, min_years, on=group_cols, how='left')

# Update year and create decade from original_year
main_data['year'] = main_data['original_year'].fillna(main_data['year'])
main_data['year'] = main_data['year'].astype('Int64')

# Compute decade while preserving missing values
def _compute_decade(year_val):
    if pd.isna(year_val):
        return pd.NA
    return (int(year_val) // 10) * 10

main_data['decade'] = main_data['year'].apply(_compute_decade).astype('Int64')
# ----------------------------

# Define features
raw_features = ["energy", "danceability", "valence", "acousticness", "instrumentalness"]

# Create subset
# We explicitly select 'track_id' (the renamed uri) and 'track_name'
metadata_cols = ['track_name', 'track_artist', 'decade', 'track_id', 'year', 'track_album_release_date', 'playlist_genre']

# Verify all columns exist before selecting
missing_cols = [c for c in metadata_cols + raw_features if c not in main_data.columns]
if missing_cols:
    print(f"Error: The following required columns are missing after processing: {missing_cols}")
    exit(1)

df_spider = main_data[metadata_cols + raw_features].copy()

# Normalize Features
for col in raw_features:
    min_val = df_spider[col].min()
    max_val = df_spider[col].max()
    df_spider[col] = (df_spider[col] - min_val) / (max_val - min_val)

# Format decade (e.g., 2020 -> "20s")
def format_decade(year_int):
    if pd.isna(year_int):
        return 'Unknown'
    year_str = str(int(year_int))
    return year_str[-2:] + "s"

df_spider['decade'] = df_spider['decade'].apply(format_decade)

# Rename feature columns (Capitalize)
df_spider.rename(columns={c: c.capitalize() for c in raw_features}, inplace=True)

# Deduplicate
# IMPORTANT: We deduplicate by 'track_id' (the unique URI). 
# Deduplicating by 'track_name' is dangerous as it deletes different songs with the same title.
df_spider = df_spider.drop_duplicates(subset=['track_id'], keep='first')

# Save
output_dir = "assets"
os.makedirs(output_dir, exist_ok=True)
spider_csv_path = os.path.join(output_dir, "spider_graph_data.csv")
df_spider.to_csv(spider_csv_path, index=False)

print(f"Success! Spider graph data saved to {spider_csv_path}")
print(df_spider.head())