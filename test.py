import pandas as pd
main_data = pd.read_csv("assets/spider_graph_data.csv")
genre = main_data["playlist_genre"]
genre = genre[0].split(", ")[0]
print(genre)