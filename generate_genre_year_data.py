import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd
import os

def generate_data():
    print("Loading data...")
    file_paths = ["high_popularity_spotify_data.csv", "low_popularity_spotify_data.csv"]
    database = []

    for file_path in file_paths:
        try:
            df = kagglehub.load_dataset(
                KaggleDatasetAdapter.PANDAS,
                "solomonameh/spotify-music-dataset",
                file_path,
            )
            database.append(df)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return

    if not database:
        print("No data loaded.")
        return

    spotify_combined = pd.concat(database, ignore_index=True)
    print("Data loaded. Columns:", spotify_combined.columns)

    if 'playlist_genre' not in spotify_combined.columns:
        print("Error: 'playlist_genre' column missing.")
        return

    # Process date/year
    spotify_combined["track_album_release_date"] = pd.to_datetime(spotify_combined["track_album_release_date"], format="mixed", errors='coerce')
    spotify_combined['year'] = spotify_combined['track_album_release_date'].dt.year
    
    # --- FIX RE-RELEASE DATES (Same logic as regenerate_csv.py) ---
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

    # Update year
    spotify_combined['year'] = spotify_combined['original_year'].fillna(spotify_combined['year'])
    # ----------------------------------------------------------------
    
    # Filter for valid years and genres
    df_clean = spotify_combined.dropna(subset=['year', 'playlist_genre'])
    df_clean['year'] = df_clean['year'].astype(int)
    
    # Filter year range 1950-2030 (as requested/logical)
    df_clean = df_clean[(df_clean['year'] >= 1950) & (df_clean['year'] <= 2030)]

    # Group by year and genre
    genre_year_counts = df_clean.groupby(['year', 'playlist_genre']).size().reset_index(name='count')
    
    output_path = "assets/genre_year_counts.csv"
    os.makedirs("assets", exist_ok=True)
    genre_year_counts.to_csv(output_path, index=False)
    print(f"Saved genre counts to {output_path}")

if __name__ == "__main__":
    generate_data()
