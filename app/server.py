from flask import Flask, render_template, request
import cx_Oracle
import json
from datetime import datetime

# database credentials
username = 'admin'
password = 'password'
dsn = 'cis550pricetracker.cgcukgcycu5f.us-east-1.rds.amazonaws.com/CIS550DB'
port = 1512

app = Flask(__name__)

# current selection
name = 'BB'
table = 'Stocks'


@app.route("/")
def splash():
    return render_template("splash.html")


@app.route("/stocks", methods=['GET', 'POST'])
def stocks():
    if request.method == 'POST':
        name = request.form['input']
        if name == 'SP' or name == 'NASDAQ' or name == 'DOW':
            table = 'INDEXES'
        else:
            table = 'STOCKS'
        (return_name, max_price, min_price, max_date, min_date, data_json) = get_data(name, table)
        link = get_twitter_link(name)
        item_name = get_item_name(name)
        return render_template("item.html",
                               item_name=item_name,
                               name=name,
                               max=max_price,
                               max_date=max_date,
                               min=min_price,
                               min_date=min_date,
                               data=data_json,
                               link=link)

    return render_template("stocks.html")


@app.route("/commodities", methods=['GET', 'POST'])
def commodities():
    if request.method == 'POST':
        name = request.form['input']
        table = 'COMMODITIES'
        (return_name, max_price, min_price, max_date, min_date, data_json) = get_data(name, table)
        link = get_twitter_link(name)
        item_name = get_item_name(name)
        return render_template("item.html",
                            item_name = item_name,
                            name=name,
                            max=max_price,
                            max_date=max_date,
                            min=min_price,
                            min_date=min_date,
                            data=data_json,
                            link=link)
    return render_template("commodities.html")


@app.route("/cart")
def cart():
    return render_template("cart.html")



def date_prettify(date_id):
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


# this function gets the data of a stock, commodity, or index given its type and name
def get_data(item, table_name):
    connection = None
    try:
        connection = cx_Oracle.connect(username, password, dsn)

    except cx_Oracle.Error as error:
        print(error)
        connection.close()

    c = connection.cursor()
    c.execute('SELECT dateID, ' + item + ' FROM ' + table_name + ' s')

    min_price = connection.cursor()
    min_price.execute('SELECT MIN( ' + item + ' ) FROM ' + table_name + ' s WHERE s.' + item + ' > 0')
    min_price = '$' + [str(i[0]) for i in min_price][0]
    min_date = connection.cursor()
    min_date.execute(
        'SELECT dateID FROM ' + table_name + ' s WHERE s.' + item + ' = (SELECT MIN(' + item + ') FROM ' + table_name + ' s WHERE s.' + item + ' > 0)')
    min_date = date_prettify([str(i[0]) for i in min_date][0])

    max_price = connection.cursor()
    max_price.execute('SELECT MAX( ' + item + ' ) FROM ' + table_name + ' s WHERE s.' + item + ' > 0')
    max_price = '$' + [str(i[0]) for i in max_price][0]
    max_date = connection.cursor()
    max_date.execute(
        'SELECT dateID FROM ' + table_name + ' s WHERE s.' + item + ' = (SELECT MAX(' + item + ') FROM ' + table_name + ' s WHERE s.' + item + ' > 0)')
    max_date = date_prettify([str(i[0]) for i in max_date][0])

    data_points = {}
    for i in c:
        data_points[int(i[0])] = i[1]

    data_json = json.dumps(data_points)

    return name, max_price, min_price, max_date, min_date, data_json

# This function returns the twitter link for embedding
def get_twitter_link(item):
    start_of_link = "https://twitter.com/"
    end_of_link = "?ref_src=twsrc%5Etfw"
    # Create a dictionary with all twitter handles (must be done manually)
    handles = {'SP': 'SPDJIndices',
               'NASDAQ': 'Nasdaq',
               'DOW': 'SPDJIndices',
               'AAPL': 'Apple',
               'AMZN': 'Amazon',
               'GE': 'GeneralElectric',
               'PG': 'ProcterGamble',
               'SHLDQ': 'Sears',
               'JCP': 'jcpenney',
               'FMCC': 'FreddieMac',
               'BB': 'BlackBerry',
               'CHK': 'Chesapeake',
               'AXL': 'AmericanAxle',
               'BJRI': 'bjsrestaurants',
               'GWPH': 'MJBizDaily',
               'IBM': 'IBM',
               'CCL': 'CarnivalCruise',
               'XOM': 'exxonmobil',
               'GOLD': 'GOLDCOUNCIL',
               'OIL': 'WorldOil',
               'WAGNER': 'SABRbbcards',
               'VALENTINO': 'TyInc',
               'ROMEO': 'alfa_romeo',
               'MARIO': 'NintendoAmerica',
               'POKEMON': 'Pokemon'}
    link = start_of_link + handles[item] + end_of_link
    print(link)
    return link

def get_item_name(item):
    handles = {'SP': 'S&P 500 Index',
               'NASDAQ': 'Nasdaq',
               'DOW': 'Dow Jones Industrial Average',
               'AAPL': 'Apple',
               'AMZN': 'Amazon',
               'GE': 'General Electric',
               'PG': 'Procter & Gamble',
               'SHLDQ': 'Sears Holdings Corporation',
               'JCP': 'J.C. Penney',
               'FMCC': 'The Federal Home Loan Mortgage Corporation',
               'BB': 'BlackBerry',
               'CHK': 'Chesapeake Energy',
               'AXL': 'American Axle & Manufacturing',
               'BJRI': 'BJ\'s Restaurants',
               'GWPH': 'GW Pharmaceuticals',
               'IBM': 'IBM',
               'CCL': 'Carnival Cruise Line',
               'XOM': 'Exxon Mobil Corporation',
               'GOLD': 'Gold',
               'OIL': 'Oil',
               'WAGNER': 'T206 Honus Wagner Baseball Card',
               'VALENTINO': 'Ty Beanie Baby - Valentino the Bear',
               'ROMEO': '1939 Alfa Romeo 8C 2900B Lungo Spider',
               'MARIO': 'Super Mario 64 - Nintendo 64',
               'POKEMON': 'Pokemon FireRed - Game Boy Advance'}
    item_name = handles[item]
    return item_name

if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(port=8000, debug=True)
