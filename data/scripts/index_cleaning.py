import pandas as pd

# Since all 3 CSVs are of the same format, I'll just loop through them
# and apply the same operations
raw_data = ['sp500.csv', 'nasdaq.csv', 'dow.csv']

for file_name in raw_data:
    curr_file = file_name.split(".")[0]
    # Load data
    data = pd.read_csv(curr_file + ".csv") 

    # Drop all unnecessary columns - basically all, but Date and Adj Close
    del data['Open']
    del data['High']
    del data['Low']
    del data['Close']
    del data['Volume']

    # Rename Adj Close to Price for standardization
    data = data.rename(columns={"Adj Close": "Price"})

    # Now reformat all date fields such that they are ints of "yyyymmdd"
    for index_label, row_series in data.iterrows():
        # Truncate prices to two decimal points
        curr_price = data.at[index_label , 'Price']
        rounded_price = round(curr_price, 2)
        data.at[index_label , 'Price'] = rounded_price

        # Date time module is being weird so unfortunately doing it manually
        entry = data.at[index_label , 'Date']
        int_of_date = int(entry.replace('-', ''))
        data.at[index_label , 'Date'] = int_of_date

    # Output CSV
    data.to_csv(curr_file + "_cleaned.csv", encoding='utf-8', index=False)
