from flask import Flask, render_template, request
import cx_Oracle
import json
from datetime import datetime

# database credentials
username = 'admin'
password = 'password'
dsn = 'cis550pricetracker.cgcukgcycu5f.us-east-1.rds.amazonaws.com/CIS550DB'
port = 1512


class Cart:

    def __init__(self):
        # Represents total cash in the bank
        self.total_cash = 100000.00

        # Dictionary of all stocks/items in portfolio
        # (Share, Date) -> (Number of Shares, Share Price)
        portfolio = {}
        self.portfolio = {}

        print('creating a new cart with $100000 initial amount')

    # num_shares - int, share_price (infl. adj) - float, transaction - string "sell/buy"
    # Return True - Transaction successful, total update
    # Return False - Transaction failed, not enough money
    def updateTotal(self, num_shares, share_price, transaction):
        trans_amount = num_shares * share_price
        if transaction == "sell":
            new_total_cash = self.total_cash + trans_amount
            self.total_cash = new_total_cash
            return True
        else:
            print('buy')
            new_total_cash = self.total_cash - trans_amount
            # This means transaction price is too high
            if (new_total_cash < 0):
                return False
            else:
                print('update')
                self.total_cash = new_total_cash
                return True

    # share_name - string, share_date - int, num_shares - int, share_price - float
    # Return True - Transaction successful, portfolio update
    # Return False - Transaction unsuccessful, portfolio won't update
    # Assume that all inputs are correct
    def addPortfolio(self, share_name, share_date, num_shares, share_price):
        # First make the tuple for the portfolio dictionary
        key_tuple = (share_name, share_date)
        # Make sure the total is valid - must return true (only buy in add portfolio)
        # This also helps us update the bank
        success = self.updateTotal(num_shares, share_price, "buy")
        if success:
            # Check if share/date is already in dict, then update value
            if key_tuple in self.portfolio.keys():
                curr_num_shares = self.portfolio[key_tuple][0]
                new_num_shares = curr_num_shares + num_shares
                # Replace tuple - share price is technically the same!
                value_tuple = (new_num_shares, share_price)
                self.portfolio[key_tuple] = value_tuple
                return True
            # Else make a new key->value pairing
            else:
                value_tuple = (num_shares, share_price)
                self.portfolio[key_tuple] = value_tuple
                return True

    # share_name - string, share_date - int, num_shares - int, share_price - float
    # Return True - Transaction successful, portfolio update
    # Return False - Transaction unsuccessful, portfolio won't update
    # Assume that all inputs are correct
    def removePortfolio(self, share_name, share_date, num_shares, share_price):
        # First make the tuple for the portfolio dictionary
        key_tuple = (share_name, share_date)
        if key_tuple in self.portfolio.keys():
            # Update the cash total
            success = self.updateTotal(num_shares, share_price, "sell")
            # Check how many 
            curr_num_shares = self.portfolio[key_tuple][0]
            print(curr_num_shares)
            new_num_shares = curr_num_shares - num_shares
            # Delete key if no shares left
            if new_num_shares == 0:
                del self.portfolio[key_tuple]
                return True
            # Update it otherwise 
            else:
                value_tuple = (new_num_shares, share_price)
                self.portfolio[key_tuple] = value_tuple
                return True
        # Else not possible to remove anything!
        else:
            return False

    # Add functions to get total worth and curent worth of portfolio

    def returnTotalCash(self):
        return self.total_cash

    def returnPortfolio(self):
        return self.portfolio

    def printCart(self):
        for (share, date), (num_shares, price) in self.portfolio.items():
            print(str(self.date_prettify(str(date))) + ' ' + share + ': ' + str(num_shares) + ' at ' + str(price))

    def date_prettify(self, date_id):
        months = {1: 'January',
                  2: 'February',
                  3: 'March',
                  4: 'April',
                  5: 'May',
                  6: 'June',
                  7: 'July',
                  8: 'August',
                  9: 'September',
                  10: 'October',
                  11: 'November',
                  12: 'December'}
        day = datetime.strptime(date_id, '%Y%m%d').day
        month = months[datetime.strptime(date_id, '%Y%m%d').month]
        year = datetime.strptime(date_id, '%Y%m%d').year
        date_pretty = month + ' ' + str(day) + ', ' + str(year)
        return date_pretty