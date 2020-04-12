import pandas as pd

# Load data
data = pd.read_csv("on_this_day.tsv", sep='\t') 

data.to_csv("on_this_day_cleaned.csv", encoding='utf-8', index=False)