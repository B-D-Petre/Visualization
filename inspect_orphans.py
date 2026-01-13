import pandas as pd
import re

def inspect_orphans():
    df = pd.read_csv("assets/spider_graph_data.csv")
    
    # Identify which ones have "Remaster" in the name but are still in 00s, 10s, 20s
    def is_suspicious(name):
        n = str(name).lower()
        keywords = ["remaster", "anniversary", "edition", "deluxe", "expanded", "mono", "stereo"]
        return any(k in n for k in keywords)

    # Filter for recent decades
    recent = df[df['decade'].isin(['00s', '10s', '20s'])]
    
    suspicious = recent[recent['track_name'].apply(is_suspicious)]
    
    # Exclude if it's already fixed (year < 2000) - wait, if it's in 00s/10s/20s, year IS >= 2000.
    
    # Print mainly Artist - Title for the agent
    for _, row in suspicious.iterrows():
        print(f"Artist: {row['track_artist']} | Track: {row['track_name']} | Current Year: {row['year']}")

if __name__ == "__main__":
    inspect_orphans()
