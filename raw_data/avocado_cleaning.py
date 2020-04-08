import pandas as pd
from datetime import datetime

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
# Now reformat all date fields such that they are strings of "mm-dd-yyyy"
for entry in data['Date']:
    datetime_object = datetime.strptime(entry,'%Y-%m-%d')
    new_datetime = datetime_object.strftime('%m-%d-%Y')
    data.loc[data.Date == entry, 'Date'] = new_datetime
print(data.head())