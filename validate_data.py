import pandas as pd
import os

def validate():
    print("Loading assets/spider_graph_data.csv...")
    try:
        df = pd.read_csv("assets/spider_graph_data.csv")
    except FileNotFoundError:
        print("Error: assets/spider_graph_data.csv not found.")
        return

    # 1. General Stats per Decade
    print("\n--- Decade Statistics ---")
    stats = df.groupby('decade')['year'].agg(['count', 'min', 'max'])
    print(stats)

    # 2. Check Specific Known Re-releases
    print("\n--- Validation of Specific Tracks (potential re-releases) ---")
    # List of tracks that often have re-issue dates
    check_tracks = [
        "Smells Like Teen Spirit", 
        "Edge of Seventeen", 
        "Jump", 
        "Lamento Boliviano", 
        "The Reason", 
        "Where Is My Mind?"
    ]
    
    for track in check_tracks:
        matches = df[df['track_name'].str.contains(track, case=False, regex=False, na=False)]
        if not matches.empty:
            print(f"\nTrack: {track}")
            # Show relevant columns
            cols = ['track_name', 'track_artist', 'decade', 'year', 'track_album_release_date']
            # safely select only existing columns
            cols = [c for c in cols if c in df.columns]
            print(matches[cols].to_string(index=False))
        else:
            print(f"\nTrack: {track} - Not found in dataset")

    # 3. Validation File Output
    output_path = "assets/decade_validation_list.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("VALIDATION OF SONGS PER DECADE\n")
        f.write("==============================\n")
        
        decades = sorted(df['decade'].unique())
        for dec in decades:
            dec_df = df[df['decade'] == dec].copy()
            f.write(f"\n\nDECADE: {dec} (Count: {len(dec_df)})\n")
            f.write("-" * 40 + "\n")
            f.write(f"{'Year':<6} | {'Release Date':<12} | {'Artist':<20} | {'Track Name'}\n")
            f.write("-" * 40 + "\n")
            
            # Sort by year and take a sample or first 50
            # To be useful, let's take the ones with largest discrepancy if possible, 
            # otherwise just sorted by artist
            
            # Check for date mismatch if column exists
            if 'track_album_release_date' in dec_df.columns:
                dec_df['release_year_raw'] = pd.to_datetime(dec_df['track_album_release_date'], errors='coerce').dt.year
                dec_df['is_corrected'] = dec_df['year'] != dec_df['release_year_raw']
                
                # Prioritize showing corrected ones
                corrected = dec_df[dec_df['is_corrected'] == True]
                others = dec_df[dec_df['is_corrected'] == False]
                
                f.write(f"[Showing up to 20 CORRECTED re-releases first]\n")
                code_samples = corrected.head(20)
                for _, row in code_samples.iterrows():
                     f.write(f"{row['year']:<6} | {str(row['track_album_release_date'])[:10]:<12} | {str(row['track_artist'])[:20]:<20} | {row['track_name']}\n")
                
                f.write(f"\n[Sample of up to 20 normal tracks]\n")
                normal_samples = others.head(20)
                for _, row in normal_samples.iterrows():
                     f.write(f"{row['year']:<6} | {str(row['track_album_release_date'])[:10]:<12} | {str(row['track_artist'])[:20]:<20} | {row['track_name']}\n")
            else:
                samples = dec_df.sort_values('year').head(40)
                for _, row in samples.iterrows():
                     f.write(f"{row['year']:<6} | {'N/A':<12} | {str(row['track_artist'])[:20]:<20} | {row['track_name']}\n")

    print(f"\nDetailed validation list saved to: {output_path}")

if __name__ == "__main__":
    validate()
