from flask import Flask, render_template, request
import cx_Oracle
import json
from datetime import datetime
from cart import Cart

# database credentials
username = 'admin'
password = 'password'
dsn = 'cis550pricetracker.cgcukgcycu5f.us-east-1.rds.amazonaws.com/CIS550DB'
port = 1512

app = Flask(__name__)

# current selection
name = 'BB'
table = 'Stocks'

user_cart = Cart()


@app.route("/")
def splash():
    return render_template("splash.html")


@app.route("/item", methods=['GET', 'POST'])
def item():
    kind = request.args.get('kind')
    name = request.args.get('name')

    if kind == "stocks":
        if name == 'SP' or name == 'NASDAQ' or name == 'DOW':
            table = 'INDEXES'
        else:
            table = 'STOCKS'
        (return_name, max_price, min_price, max_date, min_date, max_history, min_history,  data_json, curr_price) = get_data(name, table)
        link = get_twitter_link(name)
        item_name = get_item_name(name)
    else:
        table = 'COMMODITIES'
        (return_name, max_price, min_price, max_date, min_date, max_history, min_history,  data_json, curr_price) = get_data(name, table)
        link = get_twitter_link(name)
        item_name = get_item_name(name)

    if request.method == 'POST':
        cart = user_cart
        quantity = request.form['quantity']
        action_item = request.form['Buy/Sell'].split(';_;')
        action = action_item[0]
        item = action_item[1]
        print(item)
        if action == 'Buy':
            print('buying')
            cart.addPortfolio(item, str(datetime.today().strftime('%Y%m%d')), int(quantity), float(curr_price[1:]))
        else:
            print('selling')
            cart.removePortfolio(item, str(datetime.today().strftime('%Y%m%d')), int(quantity), float(curr_price[1:]))
        cart.printCart()

    return render_template("item.html",
                           item_name=item_name,
                           name=name,
                           max=max_price,
                           max_date=max_date,
                           min=min_price,
                           min_date=min_date,
                           max_history = max_history,
                           min_history = min_history,
                           data=data_json,
                           link=link,
                           curr_price=curr_price)


@app.route("/stocks", methods=['GET', 'POST'])
def stocks():
    return render_template("stocks.html")


@app.route("/commodities", methods=['GET', 'POST'])
def commodities():
    return render_template("commodities.html")


@app.route("/explore", methods=['GET', 'POST'])
def explore():
    return render_template("explore.html")


@app.route("/cart")
def cart():
    cart = user_cart
    portfolio = cart.portfolio.items()
    cart_html = ''
    for (share, share_date), (num_shares, share_price) in portfolio:
        print(share_date)
        print(share)
        print(num_shares)
        print(share_price)
        template = '<a style = "margin-top: 3px" href = "/item"> <li class ="list-group-item"> ' \
                   '{date} : {quantity} shares of {item} at ${price} each <span style="margin-left: 15px" ' \
                   'class ="badge badge-warning"> Stock </span> </li> </a>'.format(
            date=date_prettify(str(share_date)),
            quantity=num_shares, price=share_price,
            item=share)
        cart_html += template
    return render_template("cart.html", cart_html=cart_html)


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
    min_date = [str(i[0]) for i in min_date][0]
    min_date_pretty = date_prettify(min_date)

    max_price = connection.cursor()
    max_price.execute('SELECT MAX( ' + item + ' ) FROM ' + table_name + ' s WHERE s.' + item + ' > 0')
    max_price = '$' + [str(i[0]) for i in max_price][0]
    max_date = connection.cursor()
    max_date.execute(
        'SELECT dateID FROM ' + table_name + ' s WHERE s.' + item + ' = (SELECT MAX(' + item + ') FROM ' + table_name + ' s WHERE s.' + item + ' > 0)')
    max_date = [str(i[0]) for i in max_date][0]
    max_date_pretty = date_prettify(max_date)

    if (table_name == "STOCKS"):
        curr_price = connection.cursor()
        curr_price.execute('SELECT ' + item + ' FROM ' + table_name + ' s WHERE s.dateID = 20200409')
        curr_price = '$' + [str(i[0]) for i in curr_price][0]
    else:
        curr_price = connection.cursor()
        curr_price.execute('SELECT ' + item + ' FROM ' + table_name + ' s WHERE s.dateID = 20200324')
        curr_price = '$' + [str(i[0]) for i in curr_price][0]

    max_history = connection.cursor()
    max_history.execute('Select history as new_today From History h Where h.dateid = ' + max_date)
    max_history = max_history.fetchone()
    # print(max_history.fetchone())
    # if max_history.rowcount > 0:
    #     print([str(i[0]) for i in max_history][0])

    min_history = connection.cursor()
    min_history.execute('Select history as new_today From History h Where h.dateid = ' + min_date)
    min_history = min_history.fetchone()
    # print(max_history)
    # print(min_history)

    try:
        max_history = max_history[0]
    except:
        print('no max history')
        max_history = ''

    try:
        min_history = min_history[0]
    except:
        print('no min history')
        min_history = ''

    data_points = {}
    for i in c:
        data_points[int(i[0])] = i[1]

    data_json = json.dumps(data_points)

    return name, max_price, min_price, max_date_pretty, min_date_pretty, max_history, min_history, data_json, curr_price


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
