import subprocess
import sys
import pandas as pd

#Fix genres in csv
main_data = pd.read_csv("assets/main_data_kaggle.csv")
main_data['playlist_genre'] = main_data['playlist_genre'].str.split(',').str[0]
main_data.to_csv("assets/main_data_kaggle.csv", index=False)
main_data.rename(columns={'uri': 'track_id'}, inplace=True)


# List of your scripts
scripts_to_run = ["regenerate_csv.py", "generate_genre_year_data.py", "test_timeline.py"] #"validate_data.py",

for script in scripts_to_run:
    print(f"--- Running {script} ---")
    
    try:
        # 'check=True' raises an error if the script fails
        result = subprocess.run([sys.executable, script], check=True, text=True)
        print(f"Finished {script}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script}: {e}")
        # Optional: break the loop if one fails
        break