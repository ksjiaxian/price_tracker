import pandas as pd
from datetime import datetime
from datetime import date

# Load data
data = pd.read_csv("bitcoin.csv") 

# Drop all unnecessary columns - basically all, but Date and Close
del data['Symbol']
del data['Open']
del data['High']
del data['Low']
del data['Volume BTC']
del data['Volume USD']

# Rename Close to Price for standardization
data = data.rename(columns={"Close": "Price"})

# Now reformat all date fields such that they are ints of "yyyymmdd"
for index_label, row_series in data.iterrows():
    # First, convert date string to a more standardized format with all digits
    entry = datetime.strptime(data.at[index_label , 'Date'], '%m/%d/%y').date()
    if date.today() <= entry: 
        entry = entry.replace(year=entry.year - 100)
    # Now, convert this new format into our usual int format
    entry = str(entry)
    int_of_date = int(entry.replace('-', ''))
    data.at[index_label , 'Date'] = int_of_date

# Output CSV
data.to_csv("bitcoin_cleaned.csv", encoding='utf-8', index=False)