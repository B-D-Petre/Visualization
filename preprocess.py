import subprocess
import sys

# List of your scripts
scripts_to_run = ["regenerate_csv.py", "generate_genre_year_data.py", "validate_data.py", "test_timeline.py"]

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


main_data = pd.read_csv("assets/spider_graph_data.csv")
genre = main_data["playlist_genres"]
genre = genre.split(", ")