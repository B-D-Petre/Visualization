import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd
import os


main_data = pd.read_csv("assets/main_data_kaggle.csv")
main_data.head()

# Preprocess
main_data["track_album_release_date"] = pd.to_datetime(main_data["track_album_release_date"], format="mixed", errors='coerce')
main_data['year'] = main_data['track_album_release_date'].dt.year

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

main_data['clean_name'] = main_data['track_name'].apply(clean_track_name)

# Find the minimum year for each (clean_name, artist) pair
min_years = main_data.groupby(['clean_name', 'track_artist'])['year'].min().reset_index()
min_years = min_years.rename(columns={'year': 'original_year'})

# Merge back to original dataframe
main_data = pd.merge(main_data, min_years, on=['clean_name', 'track_artist'], how='left')

# Update year and create decade from original_year
# If original_year is NaN (shouldn't be), fallback to year
main_data['year'] = main_data['original_year'].fillna(main_data['year'])
# Use pandas nullable integer dtype so NA values are preserved instead of raising on astype(int)
main_data['year'] = main_data['year'].astype('Int64')

# Compute decade while preserving missing values
def _compute_decade(year_val):
	if pd.isna(year_val):
		return pd.NA
	return (int(year_val) // 10) * 10

main_data['decade'] = main_data['year'].apply(_compute_decade).astype('Int64')
# ----------------------------

# Define features
raw_features = ["energy", "danceability", "valence", "acousticness", "instrumentalness"] #I think this is where we add another feature later

# Create subset
metadata_cols = ['track_name', 'track_artist', 'decade', 'track_id', 'year', 'track_album_release_date', 'playlist_genre']
df_spider = main_data[metadata_cols + raw_features].copy()

# Normalize
for col in raw_features:
    min_val = df_spider[col].min()
    max_val = df_spider[col].max()
    df_spider[col] = (df_spider[col] - min_val) / (max_val - min_val)

# Format decade
def format_decade(year_int):
	# Handle missing decade values
	if pd.isna(year_int):
		return 'Unknown'
	year_str = str(int(year_int))
	return year_str[-2:] + "s"

df_spider['decade'] = df_spider['decade'].apply(format_decade)

# Rename columns
df_spider.rename(columns={c: c.capitalize() for c in raw_features}, inplace=True)
df_spider = df_spider.drop_duplicates(subset=['track_name'], keep='first')

# Save
output_dir = "assets"
os.makedirs(output_dir, exist_ok=True)
spider_csv_path = os.path.join(output_dir, "spider_graph_data.csv")
df_spider.to_csv(spider_csv_path, index=False)

print(f"Success! Spider graph data saved to {spider_csv_path}")
print(df_spider.head())
