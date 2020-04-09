import pandas as pd

# Load data
data = pd.read_csv("avocado.csv") 

# Drop all unnecessary columns - basically all, but Date and Average Price
del data['Unnamed: 0']
del data['Total Volume']
del data['4046']
del data['4225']
del data['4770']
del data['Large Bags']
del data['XLarge Bags']
del data['Total Bags']
del data['Small Bags']
del data['type']
del data['year']
del data['region']

# Rename AveragePrice to Price for standardization
data = data.rename(columns={"AveragePrice": "Price"})

# Now reformat all date fields such that they are ints of "yyyymmdd"
for index_label, row_series in data.iterrows():
    # Date time module is being weird so unfortunately doing it manually
    entry = data.at[index_label , 'Date']
    int_of_date = int(entry.replace('-', ''))
    data.at[index_label , 'Date'] = int_of_date

# Output CSV
data.to_csv("avocado_cleaned.csv", encoding='utf-8', index=False)