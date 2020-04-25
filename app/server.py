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
    first_time = 'true'

    recent_max_price = ''
    recent_max_date = ''
    recent_min_price = ''
    recent_min_date = ''
    recent_max_history = ''
    recent_min_history = ''

    if kind == "stocks":
        if name == 'SP' or name == 'NASDAQ' or name == 'DOW':
            table = 'INDEXES'
        else:
            table = 'STOCKS'
        (return_name, data) = get_data(name, table)
        (_, max_price, min_price, max_date, min_date, max_history, min_history) = get_quick_info(name, table)
        curr_price = get_curr_price(name, table)
        link = get_twitter_link(name)
        item_name = get_item_name(name)
    else:
        table = 'COMMODITIES'
        (return_name, data) = get_data(name, table)
        (_, max_price, min_price, max_date, min_date, max_history, min_history) = get_quick_info(name, table)
        curr_price = get_curr_price(name, table)
        link = get_twitter_link(name)
        item_name = get_item_name(name)

    if request.method == 'POST' and request.form['action'] == 'date_entry':
        first_time = 'false'
        try:
            print('user typed in ' + request.form['oldest_date'])
            (_, recent_max_price, recent_min_price, recent_max_date, recent_min_date, recent_max_history,
             recent_min_history, _) = get_quick_info(name, table, request.form['oldest_date'])
        except:
            pass
    elif request.method == 'POST' and request.form['action'] == 'clear':
        print('clearing recent prices')
        recent_max_price = ''
        recent_max_date = ''
        recent_min_price = ''
        recent_min_date = ''
        recent_max_history = ''
        recent_min_history = ''
        first_time = 'false'
    elif request.method == 'POST':
        cart = user_cart
        quantity = request.form['quantity']
        action_item = request.form['action'].split(';_;')
        action = action_item[0]
        item = action_item[1]
        first_time = 'false'
        print(item)
        if action == 'Buy':
            print('buying')
            if request.form['pretend_date'] == '':
                cart.addPortfolio(item, str(datetime.today().strftime('%Y%m%d')), int(quantity), float(curr_price[1:]))
            else:
                try:
                    cart.addPortfolio(item, request.form['pretend_date'], int(quantity), float(get_price_by_date(get_ticker(item), get_table_name(item), request.form['pretend_date'])[1:]))
                except:
                    print('error adding item to cart: check the date')
                    cart.addPortfolio(item, str(datetime.today().strftime('%Y%m%d')), int(quantity),float(curr_price[1:]))
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
                           max_history=max_history,
                           min_history=min_history,
                           recent_max=recent_max_price,
                           recent_max_date=recent_max_date,
                           recent_min=recent_min_price,
                           recent_min_date=recent_min_date,
                           recent_max_history=recent_max_history,
                           recent_min_history=recent_min_history,
                           first_time = first_time,
                           data=json.dumps(data),
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
    cart_html = []
    purchase_price = 0
    cart_value = 0
    cart_data = []
    start_dates = []
    names = []
    best = ''
    worst = ''
    best_price_difference = 0
    worst_price_difference = 100000
    value_by_date = {}
    for (share, share_date), (num_shares, share_price) in portfolio:
        purchase_price += num_shares * share_price
        current_price = float(get_curr_price(get_ticker(share), get_table_name(share))[1:])
        cart_value += num_shares * current_price
        template = '<a style = "margin-top: 3px" href = "/item"> <li class ="list-group-item"> ' \
                   '{date} : {quantity} shares of {item} at ${price} each <span style="margin-left: 15px" ' \
                   'class ="badge badge-warning"> Stock </span> </li> </a>'.format(
            date=date_prettify(str(share_date)),
            quantity=num_shares, price=share_price,
            item=share)
        cart_html.append(template)
        (return_name, data) = get_data(get_ticker(share), get_table_name(share), share_date)
        price_difference = current_price - share_price
        if price_difference > best_price_difference:
            best = share
            best_price_difference = price_difference
        if price_difference < worst_price_difference:
            worst = share
            worst_price_difference = price_difference
        cart_data.append(data)
        start_dates.append(share_date)
        names.append(get_ticker(share))

        for d, price in data.items():
            if d in value_by_date:
                value_by_date[d] += num_shares *price
            else:
                value_by_date[d] = num_shares *price

    value_by_date = json.dumps(value_by_date)

    cart_html = sorted(cart_html)
    cart_data = json.dumps(cart_data)
    start_dates = json.dumps(start_dates)
    names = json.dumps(names)

    (return_name, data_json) = get_data('AAPL', 'Stocks')

    return render_template("cart.html",
                           cart_price=round(purchase_price,2),
                           cart_value=round(cart_value,2),
                           value_by_date = value_by_date,
                           data = data_json,
                           names = names,
                           best = best,
                           worst = worst,
                           best_price_difference = round(best_price_difference, 2),
                           worst_price_difference = round(worst_price_difference, 2),
                           start_dates = start_dates,
                           cart_data = cart_data,
                           cart_html=''.join(cart_html))


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
def get_data(item, table_name, date = None):
    oldest_date_condition = ''
    if not (date is None):
        oldest_date_condition += ' WHERE dateID >= ' + str(date)

    connection = None
    try:
        connection = cx_Oracle.connect(username, password, dsn)

    except cx_Oracle.Error as error:
        print(error)
        connection.close()

    c = connection.cursor()
    c.execute('SELECT dateID, ' + item + ' FROM ' + table_name + ' s' + oldest_date_condition)


    data_points = {}
    for i in c:
        data_points[int(i[0])] = i[1]

    return name, data_points


def get_curr_price(item, table_name):
    connection = None
    try:
        connection = cx_Oracle.connect(username, password, dsn)

    except cx_Oracle.Error as error:
        print(error)
        connection.close()

    if table_name == "STOCKS":
        curr_price = connection.cursor()
        curr_price.execute('SELECT ' + item + ' FROM ' + table_name + ' s WHERE s.dateID = 20200409')
        curr_price = '$' + [str(i[0]) for i in curr_price][0]
    else:
        curr_price = connection.cursor()
        curr_price.execute('SELECT ' + item + ' FROM ' + table_name + ' s WHERE s.dateID = 20200324')
        curr_price = '$' + [str(i[0]) for i in curr_price][0]

    return curr_price


def get_price_by_date(item, table_name, date):
    connection = None
    try:
        connection = cx_Oracle.connect(username, password, dsn)

    except cx_Oracle.Error as error:
        print(error)
        connection.close()

    price = connection.cursor()
    print('SELECT ' + item + ' FROM ' + table_name + ' s WHERE s.dateID = ' + date)
    price.execute('SELECT ' + item + ' FROM ' + table_name + ' s WHERE s.dateID = ' + date)
    price = '$' + [str(i[0]) for i in price][0]

    return price


def get_quick_info(item, table_name, oldest_date=None):
    oldest_date_condition = ''
    if not (oldest_date is None):
        oldest_date_condition += ' AND dateID >= ' + str(oldest_date)

    connection = None
    try:
        connection = cx_Oracle.connect(username, password, dsn)

    except cx_Oracle.Error as error:
        print(error)
        connection.close()

    c = connection.cursor()
    c.execute('SELECT dateID, ' + item + ' FROM ' + table_name + ' s')

    min_price = connection.cursor()
    min_price.execute(
        'SELECT MIN( ' + item + ' ) FROM ' + table_name + ' s WHERE s.' + item + ' > 0' + oldest_date_condition)
    min_price = '$' + [str(i[0]) for i in min_price][0]
    min_date = connection.cursor()
    min_date.execute(
        'SELECT dateID FROM ' + table_name + ' s WHERE s.' + item + ' = (SELECT MIN(' + item + ') FROM ' + table_name + ' s WHERE s.' + item + ' > 0' + oldest_date_condition + ')' + oldest_date_condition)
    min_date = [str(i[0]) for i in min_date][0]
    min_date_pretty = date_prettify(min_date)

    max_price = connection.cursor()
    max_price.execute(
        'SELECT MAX( ' + item + ' ) FROM ' + table_name + ' s WHERE s.' + item + ' > 0' + oldest_date_condition)
    max_price = '$' + [str(i[0]) for i in max_price][0]
    max_date = connection.cursor()
    max_date.execute(
        'SELECT dateID FROM ' + table_name + ' s WHERE s.' + item + ' = (SELECT MAX(' + item + ') FROM ' + table_name + ' s WHERE s.' + item + ' > 0 ' + oldest_date_condition + ')' + oldest_date_condition)
    max_date = [str(i[0]) for i in max_date][0]
    max_date_pretty = date_prettify(max_date)

    max_history = connection.cursor()
    max_history.execute('Select history as new_today From History h Where h.dateid = ' + max_date)
    max_history = max_history.fetchone()

    min_history = connection.cursor()
    min_history.execute('Select history as new_today From History h Where h.dateid = ' + min_date)
    min_history = min_history.fetchone()

    try:
        max_history = max_history[0]
    except (cx_Oracle.DatabaseError, TypeError) as e:
        print('no max history')
        max_history = ''

    try:
        min_history = min_history[0]
    except (cx_Oracle.DatabaseError, TypeError) as e:
        print('no min history')
        min_history = ''

    return name, max_price, min_price, max_date_pretty, min_date_pretty, max_history, min_history


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


def get_table_name(item):
    tables = {'S&P 500 Index': 'Indexes',
              'Nasdaq': 'Indexes',
              'Dow Jones Industrial Average': 'Indexes',
              'Apple': 'Stocks',
              'Amazon': 'Stocks',
              'General Electric': 'Stocks',
              'Procter & Gamble': 'Stocks',
              'Sears Holdings Corporation': 'Stocks',
              'J.C. Penney': 'Stocks',
              'The Federal Home Loan Mortgage Corporation': 'Stocks',
              'BlackBerry': 'Stocks',
              'Chesapeake Energy': 'Stocks',
              'American Axle & Manufacturing': 'Stocks',
              'BJ\'s Restaurants': 'Stocks',
              'GW Pharmaceuticals': 'Stocks',
              'IBM': 'Stocks',
              'Carnival Cruise Line': 'Stocks',
              'Exxon Mobil Corporation': 'Stocks',
              'Gold': 'Stocks',
              'Oil': 'Stocks',
              'T206 Honus Wagner Baseball Card': 'Stocks',
              'Ty Beanie Baby - Valentino the Bear': 'Stocks',
              '1939 Alfa Romeo 8C 2900B Lungo Spider': 'Stocks',
              'Super Mario 64 - Nintendo 64': 'Stocks',
              'Pokemon FireRed - Game Boy Advance': 'Stocks'}
    return tables[item]


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


def get_ticker(item):
    handles = {'S&P 500 Index': 'SP',
               'Nasdaq': 'NASDAQ',
               'Dow Jones Industrial Average': 'DOW',
               'Apple': 'AAPL',
               'Amazon': 'AMZN',
               'General Electric': 'GE',
               'Procter & Gamble': 'PG',
               'Sears Holdings Corporation': 'SHLDQ',
               'J.C. Penney': 'JCP',
               'The Federal Home Loan Mortgage Corporation': 'FMCC',
               'BlackBerry': 'BB',
               'Chesapeake Energy': 'CHK',
               'American Axle & Manufacturing': 'AXL',
               'BJ\'s Restaurants': 'BJRI',
               'GW Pharmaceuticals': 'GWPH',
               'IBM': 'IBM',
               'Carnival Cruise Line': 'CCL',
               'Exxon Mobil Corporation': 'XOM',
               'Gold': 'GOLD',
               'Oil': 'OIL',
               'T206 Honus Wagner Baseball Card': 'WAGNER',
               'Ty Beanie Baby - Valentino the Bear': 'VALENTINO',
               '1939 Alfa Romeo 8C 2900B Lungo Spider': 'ROMEO',
               'Super Mario 64 - Nintendo 64': 'MARIO',
               'Pokemon FireRed - Game Boy Advance': 'POKEMON'}
    try:
        return handles[item]
    except:
        return None


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    # this will be a hardcoded example purchase history
    cart = user_cart
    cart.addPortfolio("Apple", str(20010521), 5, 1.46)
    cart.addPortfolio("BlackBerry", str(20060605), 14, 21.73)
    cart.addPortfolio("Exxon Mobil Corporation", str(20150804), 32, 63.71)
    cart.addPortfolio("Chesapeake Energy", str(20100326), 27, 19.51)
    app.run(port=8000, debug=True)
