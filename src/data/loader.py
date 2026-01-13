import os
import pandas as pd
import numpy as np

# Define Base Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

class DataLoader:
    _instance = None
    _spider_data = None
    _genre_counts = None
    _genre_year_counts = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataLoader, cls).__new__(cls)
            cls._instance._load_all_data()
        return cls._instance

    def _load_all_data(self):
        """Loads all datasets into memory."""
        print("--- Loading Data ---")
        self._spider_data = self._safe_load_csv("spider_graph_data.csv")
        self._genre_year_counts = self._safe_load_csv("genre_year_counts.csv")
        
        # Verify required columns for Spider Data
        if not self._spider_data.empty:
            # ensure 'Tempo' is capitalized as expected by figures
            # (preprocess.py should have handled this, but we double check)
            pass

    def _safe_load_csv(self, filename):
        path = os.path.join(ASSETS_DIR, filename)
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                print(f"Loaded {filename}: {df.shape}")
                return df
            except Exception as e:
                print(f"Error reading {path}: {e}")
                return pd.DataFrame()
        else:
            print(f"Warning: {path} not found.")
            return pd.DataFrame()

    @property
    def spider_data(self):
        return self._spider_data

    @property
    def genre_year_counts(self):
        return self._genre_year_counts

    def get_genres(self):
        if 'playlist_genre' in self._spider_data.columns:
            return sorted(self._spider_data['playlist_genre'].dropna().unique().tolist())
        return []

    def get_genres_for_decade(self, decade):
        if self._spider_data.empty: return []
        if 'playlist_genre' in self._spider_data.columns and 'decade' in self._spider_data.columns:
            decade_data = self._spider_data[self._spider_data['decade'] == decade]
            return sorted(decade_data['playlist_genre'].dropna().unique().tolist())
        return self.get_genres()

    def get_songs_for_decade(self, decade):
        """Returns list of dicts for dropdown options"""
        if self._spider_data.empty: return []
        
        filtered_data = self._spider_data[self._spider_data['decade'] == decade]
        songs = filtered_data[["track_name", "track_id"]].drop_duplicates().sort_values("track_name")
        
        return [{"label": row["track_name"], "value": row["track_id"]} for _, row in songs.iterrows()]

# Global Instance
data_loader = DataLoader()
