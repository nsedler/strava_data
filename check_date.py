import pandas as pd

df = pd.read_csv("data/activities.csv")

print(df.sort_values(by="start_date_local"))
