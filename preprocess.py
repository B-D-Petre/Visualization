import pandas as pd
import os
import re

# --- CONFIGURATION ---
INPUT_FILE = "assets/main_data_kaggle.csv"
OUTPUT_DIR = "assets"
SPIDER_OUTPUT = os.path.join(OUTPUT_DIR, "spider_graph_data.csv")
GENRE_YEAR_OUTPUT = os.path.join(OUTPUT_DIR, "genre_year_counts.csv")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_track_name(name):
    """Removes Remaster/Version/Mix info to find original song matches."""
    if not isinstance(name, str): return str(name)
    name = re.sub(r' - .*Remaster.*', '', name, flags=re.IGNORECASE)
    name = re.sub(r' \(.*Remaster.*\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r' - .*Version.*', '', name, flags=re.IGNORECASE)
    name = re.sub(r' \(.*Version.*\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r' - .*Mix.*', '', name, flags=re.IGNORECASE)
    return name.strip()

def main():
    print("--- Starting Unified Preprocessing ---")

    # 1. LOAD DATA
    print(f"Loading {INPUT_FILE}...")
    try:
        main_data = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found.")
        return

    # 2. INITIAL COLUMN CLEANING
    # Fix Genres (split comma-separated values and take the first one)
    if 'playlist_genre' in main_data.columns:
        main_data['playlist_genre'] = main_data['playlist_genre'].str.split(',').str[0]

    # Rename 'uri' to 'track_id'
    if 'track_id' not in main_data.columns:
        if 'uri' in main_data.columns:
            print("Renaming 'uri' column to 'track_id'...")
            main_data.rename(columns={'uri': 'track_id'}, inplace=True)
        else:
            print("Error: Could not find 'track_id' or 'uri' column.")
            return
            
    # Validate required columns
    if 'track_name' not in main_data.columns:
        print("Error: 'track_name' column missing.")
        return

    # 3. DATE & RE-RELEASE LOGIC
    print("Processing dates and fixing re-releases...")
    
    # --- FIX: Drop 'original_year' if it exists from a previous run ---
    # This prevents the merge from creating 'original_year_x' and 'original_year_y'
    if 'original_year' in main_data.columns:
        main_data.drop(columns=['original_year'], inplace=True)

    # Convert dates
    main_data["track_album_release_date"] = pd.to_datetime(main_data["track_album_release_date"], format="mixed", errors='coerce')
    main_data['year'] = main_data['track_album_release_date'].dt.year

    # Apply clean name logic
    main_data['clean_name'] = main_data['track_name'].apply(clean_track_name)

    # Find the minimum year for each (clean_name, artist) pair
    group_cols = ['clean_name', 'track_artist'] if 'track_artist' in main_data.columns else ['clean_name']
    
    min_years = main_data.groupby(group_cols)['year'].min().reset_index()
    min_years = min_years.rename(columns={'year': 'original_year'})

    # Merge back and update year
    main_data = pd.merge(main_data, min_years, on=group_cols, how='left')
    main_data['year'] = main_data['original_year'].fillna(main_data['year'])
    main_data['year'] = main_data['year'].astype('Int64')

    # Save the cleaned main data
    main_data.to_csv(INPUT_FILE, index=False)
    print(f"Main cleaned data saved to {INPUT_FILE}")

    # ---------------------------------------------------------
    # 4. GENERATE SPIDER GRAPH DATA
    # ---------------------------------------------------------
    print("Generating Spider Graph Data...")
    
    raw_features = ["energy", "danceability", "valence", "acousticness", "instrumentalness"]
    metadata_cols = ['track_name', 'track_artist', 'year', 'track_id', 'playlist_genre']

    # Check columns
    available_cols = [c for c in metadata_cols + raw_features if c in main_data.columns]
    df_spider = main_data[available_cols].copy()

    # Calculate Decade
    def _compute_decade_str(year_val):
        if pd.isna(year_val): return 'Unknown'
        return str((int(year_val) // 10) * 10)[-2:] + "s"

    df_spider['decade'] = df_spider['year'].apply(_compute_decade_str)

    # Normalize Features (0-1)
    for col in raw_features:
        if col in df_spider.columns:
            min_val = df_spider[col].min()
            max_val = df_spider[col].max()
            df_spider[col] = (df_spider[col] - min_val) / (max_val - min_val)
            # Capitalize for display
            df_spider.rename(columns={col: col.capitalize()}, inplace=True)

    # Deduplicate by track_id
    df_spider = df_spider.drop_duplicates(subset=['track_id'], keep='first')

    # Save
    df_spider.to_csv(SPIDER_OUTPUT, index=False)
    print(f"Saved: {SPIDER_OUTPUT}")

    # ---------------------------------------------------------
    # 5. GENERATE GENRE/YEAR DATA
    # ---------------------------------------------------------
    print("Generating Genre/Year Counts...")

    # Filter for valid years and genres
    df_counts = main_data.dropna(subset=['year', 'playlist_genre']).copy()
    df_counts['year'] = df_counts['year'].astype(int)

    # Filter range 1950-2030
    df_counts = df_counts[(df_counts['year'] >= 1950) & (df_counts['year'] <= 2030)]

    # Group
    genre_year_counts = df_counts.groupby(['year', 'playlist_genre']).size().reset_index(name='count')

    # Save
    genre_year_counts.to_csv(GENRE_YEAR_OUTPUT, index=False)
    print(f"Saved: {GENRE_YEAR_OUTPUT}")

    print("\n--- All preprocessing complete! ---")

if __name__ == "__main__":
    main()