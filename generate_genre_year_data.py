import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd
import os
import re

def generate_data():
    print("Loading assets/main_data_kaggle.csv...")
    try:
        main_data = pd.read_csv("assets/main_data_kaggle.csv")
    except FileNotFoundError:
        print("Error: assets/main_data_kaggle.csv not found.")
        return

    # Debug: Print columns to be sure
    print("Columns found:", main_data.columns.tolist())

    if 'playlist_genre' not in main_data.columns:
        print("Error: 'playlist_genre' column missing.")
        return

    # Check for track_name (Critical for re-release logic)
    if 'track_name' not in main_data.columns:
        print("Error: 'track_name' column missing. Please run preprocess.py first.")
        return

    # Process date/year
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

    # Apply to 'track_name'
    main_data['clean_name'] = main_data['track_name'].apply(clean_track_name)

    # Find the minimum year for each (clean_name, artist) pair
    # Using 'track_artist' as per your new dataset columns
    if 'track_artist' in main_data.columns:
        group_cols = ['clean_name', 'track_artist']
    else:
        group_cols = ['clean_name'] # Fallback
        
    min_years = main_data.groupby(group_cols)['year'].min().reset_index()
    min_years = min_years.rename(columns={'year': 'original_year'})

    # Merge back to original dataframe
    main_data = pd.merge(main_data, min_years, on=group_cols, how='left')

    # Update year
    main_data['year'] = main_data['original_year'].fillna(main_data['year'])
    # ----------------------------------------------------------------
    
    # Filter for valid years and genres
    df_clean = main_data.dropna(subset=['year', 'playlist_genre']).copy()
    df_clean.loc[:, 'year'] = df_clean['year'].astype(int)
    
    # Filter year range 1950-2030
    df_clean = df_clean[(df_clean['year'] >= 1950) & (df_clean['year'] <= 2030)]

    # Group by year and genre
    genre_year_counts = df_clean.groupby(['year', 'playlist_genre']).size().reset_index(name='count')
    
    output_path = "assets/genre_year_counts.csv"
    os.makedirs("assets", exist_ok=True)
    genre_year_counts.to_csv(output_path, index=False)
    print(f"Saved genre counts to {output_path}")

if __name__ == "__main__":
    generate_data()