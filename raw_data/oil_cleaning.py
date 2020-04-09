import pandas as pd
from datetime import datetime
from datetime import date

# Load data
data = pd.read_csv("oil.csv")

# Now reformat all date fields such that they are ints of "yyyymmdd"
for index_label, row_series in data.iterrows():
    # First, convert date string to a more standardized format with all digits
    entry = datetime.strptime(data.at[index_label , 'Date'], '%d-%b-%y').date()
    if date.today() <= entry: 
        entry = entry.replace(year=entry.year - 100)
    # Now, convert this new format into our usual int format
    entry = str(entry)
    int_of_date = int(entry.replace('-', ''))
    data.at[index_label , 'Date'] = int_of_date

# Output CSV
data.to_csv("oil_cleaned.csv", encoding='utf-8', index=False)
