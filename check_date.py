import pandas as pd

df = pd.read_csv("data/activities.csv")
df.sort_values(by="start_date_local", ascending=False, inplace=True)

df["start_date_local"][0]
