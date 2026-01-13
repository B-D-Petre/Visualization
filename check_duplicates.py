import pandas as pd
import kagglehub
from kagglehub import KaggleDatasetAdapter
import re

def check():
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
        except:
            pass

    if not database:
        return

    df = pd.concat(database, ignore_index=True)
    df["track_album_release_date"] = pd.to_datetime(df["track_album_release_date"], format="mixed", errors='coerce')
    df['year'] = df['track_album_release_date'].dt.year
    df = df.dropna(subset=['year'])
    df['year'] = df['year'].astype(int)

    # Basic cleaning of track names to catch Remasters
    def clean_name(name):
        if not isinstance(name, str): return str(name)
        # Remove " - Remastered..." or " (Remastered...)" or " - .... Version"
        name = re.sub(r' - .*Remaster.*', '', name, flags=re.IGNORECASE)
        name = re.sub(r' \(.*Remaster.*\)', '', name, flags=re.IGNORECASE)
        name = re.sub(r' - .*Version.*', '', name, flags=re.IGNORECASE)
        return name.strip()

    df['clean_name'] = df['track_name'].apply(clean_name)

    # Check duplicates
    groups = df.groupby(['clean_name', 'track_artist'])
    
    print("\nChecking for year discrepancies...")
    count = 0
    for (name, artist), group in groups:
        years = group['year'].unique()
        if len(years) > 1:
            print(f"Song: '{name}' by '{artist}' has years: {sorted(years)}")
            count += 1
            if count > 10:
                break
    
    if count == 0:
        print("No discrepancies found with simple grouping.")

if __name__ == "__main__":
    check()
