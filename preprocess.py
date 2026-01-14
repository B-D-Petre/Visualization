import pandas as pd
import os
import re

# --- CONFIGURATION ---
INPUT_FILE = "assets/data_backup.csv"
OUTPUT_FILE = "assets/main_data_kaggle.csv"
OUTPUT_DIR = "assets"

SPIDER_OUTPUT = os.path.join(OUTPUT_DIR, "spider_graph_data.csv")
GENRE_YEAR_OUTPUT = os.path.join(OUTPUT_DIR, "genre_year_counts.csv")

# Minimum songs required to keep a genre
MIN_SONGS_PER_GENRE = 5

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- GENRE MAPPING DEFINITIONS ---
GENRE_MAPPING = {
    'Hip Hop': ['hip hop', 'rap', 'trap', 'drill', 'grime', 'old school'],
    'R&B': ['r&b', 'soul', 'funk', 'neo soul', 'new jack swing', 'gospel'],
    'Electronic': ['electronic', 'edm', 'house', 'techno', 'trance', 'dubstep', 'dance', 'disco', 'electro', 'drum and bass', 'synth', 'ambient'],
    'Rock': ['rock', 'punk', 'grunge', 'metal', 'emo', 'indie', 'alternative', 'psychedelic', 'new wave'],
    'Jazz': ['jazz', 'bop', 'swing', 'big band', 'fusion'],
    'Blues': ['blues', 'rhythm and blues'],
    'Classical': ['classical', 'orchestra', 'opera', 'baroque', 'piano'],
    'Country': ['country', 'bluegrass', 'americana', 'western'],
    'Folk': ['folk', 'acoustic'],
    'Reggae': ['reggae', 'ska', 'dancehall', 'dub'],
    'Latin': ['latin', 'reggaeton', 'salsa', 'bachata', 'cumbia', 'tropical'],
    'World': ['afrobeat', 'k-pop', 'j-pop', 'bollywood', 'world'],
    'Pop': ['pop', 'boy band', 'girl group', 'easy listening', 'adult standards', 'lounge'],
}

def clean_track_name(name):
    if not isinstance(name, str): return str(name)
    name = re.sub(r' - .*Remaster.*', '', name, flags=re.IGNORECASE)
    name = re.sub(r' \(.*Remaster.*\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r' - .*Version.*', '', name, flags=re.IGNORECASE)
    name = re.sub(r' \(.*Version.*\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r' - .*Mix.*', '', name, flags=re.IGNORECASE)
    return name.strip()

def map_genre(genre_string):
    if not isinstance(genre_string, str):
        return "Unknown"
    
    clean_str = genre_string.lower().replace('australian', '')
    
    for macro_genre, keywords in GENRE_MAPPING.items():
        for keyword in keywords:
            if keyword in clean_str:
                return macro_genre
    
    first_genre = clean_str.split(',')[0].strip()
    return first_genre.capitalize() if first_genre else "Other"

def main():
    print("--- Starting Unified Preprocessing ---")

    # 1. LOAD DATA
    print(f"Loading raw data from {INPUT_FILE}...")
    try:
        main_data = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found. Please ensure you have a 'data_backup.csv' in assets.")
        return

    # 2. CLEAN GENRES
    print("Consolidating Genres...")
    if 'playlist_genre' in main_data.columns:
        main_data['playlist_genre'] = main_data['playlist_genre'].apply(map_genre)
        
        # --- PRUNING STEP ---
        initial_count = len(main_data)
        genre_counts = main_data['playlist_genre'].value_counts()
        
        valid_genres = genre_counts[genre_counts >= MIN_SONGS_PER_GENRE].index
        dropped_genres = genre_counts[genre_counts < MIN_SONGS_PER_GENRE].index
        
        main_data = main_data[main_data['playlist_genre'].isin(valid_genres)]
        final_count = len(main_data)
        
        print(f"Dropped {len(dropped_genres)} rare genres (< {MIN_SONGS_PER_GENRE} songs).")
        print(f"Removed {initial_count - final_count} tracks. Remaining tracks: {final_count}")

    # Standardize 'track_id'
    if 'track_id' not in main_data.columns:
        if 'uri' in main_data.columns:
            main_data.rename(columns={'uri': 'track_id'}, inplace=True)
        else:
            print("Error: Could not find 'track_id' or 'uri' column.")
            return

    if 'track_name' not in main_data.columns:
        print("Error: 'track_name' column missing.")
        return

    # 3. DATE & RE-RELEASE LOGIC
    print("Processing dates and fixing re-releases...")
    if 'original_year' in main_data.columns:
        main_data.drop(columns=['original_year'], inplace=True)

    main_data["track_album_release_date"] = pd.to_datetime(main_data["track_album_release_date"], format="mixed", errors='coerce')
    main_data['year'] = main_data['track_album_release_date'].dt.year

    main_data['clean_name'] = main_data['track_name'].apply(clean_track_name)

    group_cols = ['clean_name', 'track_artist'] if 'track_artist' in main_data.columns else ['clean_name']
    min_years = main_data.groupby(group_cols)['year'].min().reset_index()
    min_years = min_years.rename(columns={'year': 'original_year'})

    main_data = pd.merge(main_data, min_years, on=group_cols, how='left')
    main_data['year'] = main_data['original_year'].fillna(main_data['year'])
    main_data['year'] = main_data['year'].astype('Int64')

    # SAVE TO WORKING FILE
    main_data.to_csv(OUTPUT_FILE, index=False)
    print(f"Cleaned data saved to {OUTPUT_FILE}")

    # 4. GENERATE SPIDER GRAPH DATA
    print("Generating Spider Graph Data...")
    
    # --- ADDED NEW FEATURES HERE ---
    # We include duration_ms, loudness, speechiness alongside the originals
    raw_features = ["energy", "danceability", "valence", "acousticness", "instrumentalness", "tempo", "loudness", "speechiness", "duration_ms"]
    metadata_cols = ['track_name', 'track_artist', 'year', 'track_id', 'playlist_genre']

    available_cols = [c for c in metadata_cols + raw_features if c in main_data.columns]
    df_spider = main_data[available_cols].copy()

    def _compute_decade_str(year_val):
        if pd.isna(year_val): return 'Unknown'
        return str((int(year_val) // 10) * 10)[-2:] + "s"

    df_spider['decade'] = df_spider['year'].apply(_compute_decade_str)

    # Normalize Features
    import numpy as np
    for col in raw_features:
        if col in df_spider.columns:
            
            # Apply transformation based on feature type
            if col == "duration_ms":
                # For Duration: Robust scaling (5th-95th percentile)
                q05 = df_spider[col].quantile(0.05) 
                q95 = df_spider[col].quantile(0.95)
                df_spider[col] = df_spider[col].clip(q05, q95)
                min_val = q05
                max_val = q95
            
            else:
                # Standard Min-Max for other features
                min_val = df_spider[col].min()
                max_val = df_spider[col].max()

            # Avoid division by zero
            if max_val - min_val != 0:
                df_spider[col] = (df_spider[col] - min_val) / (max_val - min_val)
            else:
                df_spider[col] = 0
            
            # Rename columns to standardized formatting
            if col == "duration_ms":
                df_spider.rename(columns={col: "Duration"}, inplace=True)
            else:
                df_spider.rename(columns={col: col.capitalize()}, inplace=True)

    df_spider = df_spider.drop_duplicates(subset=['track_id'], keep='first')
    df_spider.to_csv(SPIDER_OUTPUT, index=False)
    print(f"Saved: {SPIDER_OUTPUT}")

    # 5. GENERATE GENRE/YEAR DATA
    print("Generating Genre/Year Counts...")
    df_counts = main_data.dropna(subset=['year', 'playlist_genre']).copy()
    df_counts['year'] = df_counts['year'].astype(int)
    df_counts = df_counts[(df_counts['year'] >= 1950) & (df_counts['year'] <= 2030)]

    genre_year_counts = df_counts.groupby(['year', 'playlist_genre']).size().reset_index(name='count')
    genre_year_counts.to_csv(GENRE_YEAR_OUTPUT, index=False)
    print(f"Saved: {GENRE_YEAR_OUTPUT}")

    # 6. DATA ANALYSIS REPORT
    print("\n" + "="*40)
    print("       DATA ANALYSIS SUMMARY       ")
    print("="*40)
    print(f"Total Tracks Processed: {len(main_data)}")
    
    if 'playlist_genre' in main_data.columns:
        genre_counts = main_data['playlist_genre'].value_counts()
        print(f"Total Unique Genres:    {len(genre_counts)}")
        print("-" * 30)
        print("Top 5 Most Common Genres:")
        for genre, count in genre_counts.head(5).items():
            print(f"  - {genre}: {count}")
    
    if 'year' in main_data.columns:
        min_yr = main_data['year'].min()
        max_yr = main_data['year'].max()
        print("-" * 30)
        print(f"Year Range: {min_yr} to {max_yr}")

    print("="*40 + "\n")
    print("--- All preprocessing complete! ---")

if __name__ == "__main__":
    main()