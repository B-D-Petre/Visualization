import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd
import os

def generate_data():

    #changed datasource to main_data_kaggle.csv
    main_data = pd.read_csv("assets/main_data_kaggle.csv")
    print("Data loaded. Columns:", main_data.columns)

    if 'playlist_genre' not in main_data.columns:
        print("Error: 'playlist_genre' column missing.")
        return

    # Process date/year
    main_data["track_album_release_date"] = pd.to_datetime(main_data["track_album_release_date"], format="mixed", errors='coerce')
    main_data['year'] = main_data['track_album_release_date'].dt.year
    
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

    main_data['clean_name'] = main_data['track_name'].apply(clean_track_name)

    # Find the minimum year for each (clean_name, artist) pair
    min_years = main_data.groupby(['clean_name', 'track_artist'])['year'].min().reset_index()
    min_years = min_years.rename(columns={'year': 'original_year'})

    # Merge back to original dataframe
    main_data = pd.merge(main_data, min_years, on=['clean_name', 'track_artist'], how='left')

    # Update year
    main_data['year'] = main_data['original_year'].fillna(main_data['year'])
    # ----------------------------------------------------------------
    
    # Filter for valid years and genres
    # Use .copy() to ensure we modify a separate DataFrame and avoid SettingWithCopyWarning
    df_clean = main_data.dropna(subset=['year', 'playlist_genre']).copy()
    # Use .loc for explicit assignment
    df_clean.loc[:, 'year'] = df_clean['year'].astype(int)
    
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
