import subprocess
import sys
import pandas as pd

# 1. Fix genres and Rename URI -> track_id
print("--- Cleaning Main Data ---")
main_data = pd.read_csv("assets/main_data_kaggle.csv")

# Fix Genres (split comma-separated values)
main_data['playlist_genre'] = main_data['playlist_genre'].str.split(',').str[0]

# RENAME 'uri' to 'track_id' if it exists
if 'uri' in main_data.columns:
    main_data.rename(columns={'uri': 'track_id'}, inplace=True)

# Save AFTER renaming
main_data.to_csv("assets/main_data_kaggle.csv", index=False)
print("Saved cleaned data to assets/main_data_kaggle.csv")

# 2. Run the other scripts
scripts_to_run = ["regenerate_csv.py", "generate_genre_year_data.py", "test_timeline.py"]

for script in scripts_to_run:
    print(f"\n--- Running {script} ---")
    try:
        result = subprocess.run([sys.executable, script], check=True, text=True)
        print(f"Finished {script}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script}: {e}")
        break