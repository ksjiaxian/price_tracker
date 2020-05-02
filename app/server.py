from flask import Flask, render_template, request, redirect, url_for
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
name = ''
table = ''

user_cart = Cart()


@app.route("/")
def splash():
    return render_template("splash.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/item", methods=['GET', 'POST'])
def item():
    kind = request.args.get('kind')
    name = request.args.get('name')
    first_time = 'true'

    error_message = ''
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
        (_, return_name, data) = get_data(name, table)
        (_, max_price, min_price, max_date, min_date, max_history, min_history) = get_quick_info(name, table)
        _, curr_price = get_curr_price(name, table)
        link = get_twitter_link(name)
        item_name = get_item_name(name)
    else:
        table = 'COMMODITIES'
        (_, return_name, data) = get_data(name, table)
        (_, max_price, min_price, max_date, min_date, max_history, min_history) = get_quick_info(name, table)
        _, curr_price = get_curr_price(name, table)
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
                did_add_correctly = cart.addPortfolio(item, str(datetime.today().strftime('%Y%m%d')), int(quantity), float(curr_price[1:]))
                if not did_add_correctly:
                    error_message = 'Error buying item'
            else:
                try:
                    cart.addPortfolio(item, request.form['pretend_date'], int(quantity), float(get_price_by_date(get_ticker(item), get_table_name(item), request.form['pretend_date'])[1:]))
                except:
                    error_message = 'Date Error'
                    cart.addPortfolio(item, str(datetime.today().strftime('%Y%m%d')), int(quantity),float(curr_price[1:]))
        else:
            print('selling')
            did_sell_correctly = cart.removePortfolio(item, str(datetime.today().strftime('%Y%m%d')), int(quantity), float(curr_price[1:]))
            if not did_sell_correctly:
                error_message = 'Error selling item'
        cart.printCart()

        # if successfully changed cart, then go straight there
        if error_message == '':
            print('no errors when buying')
            return redirect(url_for('cart'))

    return render_template("item.html",
                           error_message=error_message,
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

@app.route("/itemexplore", methods=['GET', 'POST'])
def itemexplore():
    kind = request.args.get('kind')
    name = request.args.get('name')
    item_name = get_item_name(name)
    explore_data = get_explore_data(name, kind)
    return render_template("itemexplore.html",
                            item_name=item_name,
                            q1=explore_data[0],
                            q2=explore_data[1], 
                            q3=explore_data[2],
                            q4=explore_data[3],
                            q5=explore_data[4],
                            q6=explore_data[5],
                            q7=explore_data[6],
                            q8_1=explore_data[7],
                            q8_2=explore_data[8],
                            q9_1=explore_data[9],
                            q9_2=explore_data[10])

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
    connection = None
    for (share, share_date), (num_shares, share_price) in portfolio:
        purchase_price += num_shares * share_price
        if connection is None:
            connect, current_price = get_curr_price(get_ticker(share), get_table_name(share))
            current_price = float(current_price[1:])
            connection = connect
        else:
            _, current_price = get_curr_price(get_ticker(share), get_table_name(share), connection)
            current_price = float(current_price[1:])
        cart_value += num_shares * current_price
        template = '<a style = "margin-top: 3px" href = "/item"> <li class ="list-group-item"> ' \
                   '{date} : {quantity} shares of {item} at ${price} each <span style="margin-left: 15px" ' \
                   'class ="badge badge-warning"> Stock </span> </li> </a>'.format(
            date=date_prettify(str(share_date)),
            quantity=num_shares, price=share_price,
            item=share)
        cart_html.append(template)
        if connection is None:
            (connect, return_name, data) = get_data(get_ticker(share), get_table_name(share), share_date)
            connection = connect
        else:
            (_, return_name, data) = get_data(get_ticker(share), get_table_name(share), share_date, connection)
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

    return render_template("cart.html",
                           cart_price=round(purchase_price,2),
                           cart_value=round(cart_value,2),
                           value_by_date = value_by_date,
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
def get_data(item, table_name, date=None, connect=None):
    oldest_date_condition = ''
    if not (date is None):
        oldest_date_condition += ' WHERE dateID >= ' + str(date)

    connection = None
    if connect is None:
        print('here')
        try:
            connection = cx_Oracle.connect(username, password, dsn)

        except cx_Oracle.Error as error:
            print(error)
            connection.close()
    else:
        connection = connect

    c = connection.cursor()
    c.execute('SELECT dateID, ' + item + ' FROM ' + table_name + ' s' + oldest_date_condition)

    data_points = {}
    for i in c:
        data_points[int(i[0])] = i[1]

    return connection, name, data_points


def get_curr_price(item, table_name, connect = None):
    connection = None
    if connect is None:
        connection = None
        try:
            connection = cx_Oracle.connect(username, password, dsn)

        except cx_Oracle.Error as error:
            print(error)
            connection.close()
    else:
        connection = connect

    if table_name == "STOCKS":
        curr_price = connection.cursor()
        curr_price.execute('SELECT ' + item + ' FROM ' + table_name + ' s WHERE s.dateID = 20200409')
        curr_price = '$' + [str(i[0]) for i in curr_price][0]
    else:
        curr_price = connection.cursor()
        curr_price.execute('SELECT ' + item + ' FROM ' + table_name + ' s WHERE s.dateID = 20200324')
        curr_price = '$' + [str(i[0]) for i in curr_price][0]

    return connection, curr_price


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

    c.execute(
        'SELECT MIN( ' + item + ' ) FROM ' + table_name + ' s WHERE s.' + item + ' > 0' + oldest_date_condition)
    min_price = '$' + [str(i[0]) for i in c][0]

    c.execute(
        'SELECT dateID FROM ' + table_name + ' s WHERE s.' + item + ' = (SELECT MIN(' + item + ') FROM ' + table_name + ' s WHERE s.' + item + ' > 0' + oldest_date_condition + ')' + oldest_date_condition)
    min_date = [str(i[0]) for i in c][0]
    min_date_pretty = date_prettify(min_date)


    c.execute(
        'SELECT MAX( ' + item + ' ) FROM ' + table_name + ' s WHERE s.' + item + ' > 0' + oldest_date_condition)
    max_price = '$' + [str(i[0]) for i in c][0]

    c.execute(
        'SELECT dateID FROM ' + table_name + ' s WHERE s.' + item + ' = (SELECT MAX(' + item + ') FROM ' + table_name + ' s WHERE s.' + item + ' > 0 ' + oldest_date_condition + ')' + oldest_date_condition)
    max_date = [str(i[0]) for i in c][0]
    max_date_pretty = date_prettify(max_date)

    c.execute('Select history as new_today From History h Where h.dateid = ' + max_date)
    max_history = c.fetchone()

    c.execute('Select history as new_today From History h Where h.dateid = ' + min_date)
    min_history = c.fetchone()

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

# These are all to get answers for explore pages
# Separated for clarity 
def get_explore_data(item, kind):
    item_string = "'" + item + "'"
    query = "SELECT d.desr FROM Descriptions d WHERE d.itemID = " + item_string
    print(query)
    connection = None
    try:
        connection = cx_Oracle.connect(
            username,
            password,
            dsn)          
    except cx_Oracle.Error as error:
        print(error)
        connection.close()

    c = connection.cursor() 
    c.execute(query) 
    q1_ans = [str(i[0]) for i in c][0]
    query = "SELECT ((t.today_price - x.yesterday_price)/x.yesterday_price * 100) price_delta FROM " + \
            "(SELECT s." + item + " as today_price FROM " + kind +  " s WHERE s.dateID = 20200316) t, " + \
            "(SELECT s." + item + " as yesterday_price FROM " + kind + " s WHERE s.dateID = 20200313) x "
    c.execute(query) 
    q2_ans = [str(round(i[0],2)) for i in c][0]
    query = "SELECT ((t.today_price - x.yesterday_price)/(x.yesterday_price+0.0001) * 100) price_delta FROM " + \
            "(SELECT s." + item + " as today_price FROM " + kind +  " s WHERE s.dateID = 20010917) t, " + \
            "(SELECT s." + item + " as yesterday_price FROM " + kind + " s WHERE s.dateID = 20010910) x "
    c.execute(query)         
    q3_ans = [str(round(i[0],2)) for i in c][0]
    query = "SELECT AVG(adjusted_value) FROM (SELECT (" + item + "/AMOUNT) as adjusted_value " \
            "FROM (SELECT dateID, " + item + " FROM " + kind +  " s WHERE dateID >= 20000103) a " + \
            "JOIN Dates d ON a.dateID = d.dateID JOIN Inflation i ON d.Year = i.Year)"
    c.execute(query) 
    q4_ans = "$" + [str(round(i[0],2)) for i in c][0]
    query = "SELECT (t.today_price - x.yesterday_price) price_delta FROM " + \
            "(SELECT s." + item + " as today_price FROM " + kind +  " s WHERE s.dateID = 20200323) t, " + \
            "(SELECT s." + item + " as yesterday_price FROM " + kind + " s WHERE s.dateID = 20200313) x "
    c.execute(query) 
    q5_ans = "$" + [str(round(i[0],2)) for i in c][0]
    query = "SELECT (t.today_value - p.past_value) price_delta FROM (SELECT c." + item + " as today_value " \
            "FROM " + kind +  " c WHERE c.dateID = 20200102) t, (SELECT c." + item +  " as past_value FROM " + kind + \
            " c WHERE c.dateID = 20190502) p"
    c.execute(query) 
    q6_ans = "$" + [str(round(i[0],2)) for i in c][0]
    query = "WITH Sears AS (SELECT (SHLDQ/AMOUNT) as adjusted_sears FROM (SELECT dateID, SHLDQ FROM Stocks s " \
            "WHERE dateID = 20060323) a JOIN Dates d ON a.dateID = d.dateID JOIN Inflation i ON d.Year = i.Year), " + \
            "Item AS (SELECT (" + item + "/AMOUNT) AS adjusted_product FROM (SELECT dateID, " + item + " FROM " + kind + " c " \
            "WHERE dateID = 20060323) a JOIN Dates d ON a.dateID = d.dateID JOIN Inflation i ON d.Year = i.Year) " + \
            "SELECT v.adjusted_product - s.adjusted_sears as difference FROM Sears s, Item v"
    c.execute(query) 
    q7_ans = "$" + [str(round(i[0],2)) for i in c][0]
    query = "SELECT ((tm.today_mkt_price - xm.yesterday_mkt_price)/xm.yesterday_mkt_price*100) AS market_return, " \
            "((t.today_item_price - x.yesterday_item_price)/x.yesterday_item_price*100) AS item_return FROM (SELECT s." + \
            item + " as today_item_price FROM " + kind + " s WHERE s.dateID = 20200323) t, (SELECT s." + item + \
            " as yesterday_item_price FROM " + kind + " s WHERE s.dateID = 20170103) x, (SELECT i.SP as today_mkt_price " + \
            "FROM Indexes i WHERE i.dateID = 20200323) tm, (SELECT i.SP as yesterday_mkt_price FROM Indexes i WHERE i.dateID = 20170103) xm"
    c.execute(query) 
    q81_ans = [str(round(i[0],2)) for i in c][0]
    c.execute(query) 
    q82_ans = [str(round(i[1],2)) for i in c][0]
    query = "SELECT ((t.today_item_price - x.yesterday_item_price)/x.yesterday_item_price*100) AS item_return, 17.067 AS tbill_return " \
            "FROM (SELECT s." + item + " as today_item_price FROM " + kind + " s WHERE s.dateID = 20200323) t, " + \
            "(SELECT s." + item + " as yesterday_item_price FROM " + kind + " s WHERE s.dateID = 20170103) x"
    c.execute(query) 
    q91_ans = [str(round(i[0],2)) for i in c][0]
    c = connection.cursor() 
    c.execute(query) 
    q92_ans = [str(round(i[1],2)) for i in c][0]
    return [q1_ans, q2_ans, q3_ans, q4_ans, q5_ans, q6_ans, q7_ans, q81_ans, q82_ans, q91_ans, q92_ans]

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
              'Gold': 'Commodities',
              'Oil': 'Commodities',
              'T206 Honus Wagner Baseball Card': 'Commodities',
              'Ty Beanie Baby - Valentino the Bear': 'Commodities',
              '1939 Alfa Romeo 8C 2900B Lungo Spider': 'Commodities',
              'Super Mario 64 - Nintendo 64': 'Commodities',
              'Pokemon FireRed - Game Boy Advance': 'Commodities'}
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
