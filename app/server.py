from flask import Flask, render_template
import cx_Oracle
import json
from datetime import datetime

# database credentials
username = 'admin'
password = 'password'
dsn = 'cis550pricetracker.cgcukgcycu5f.us-east-1.rds.amazonaws.com/CIS550DB'
port = 1512

app = Flask(__name__)


@app.route("/")
def splash():
    connection = None
    try:
        connection = cx_Oracle.connect(username, password, dsn)

    except cx_Oracle.Error as error:
        print(error)
        connection.close()

    c = connection.cursor()
    c.execute('SELECT * FROM History WHERE dateID >= 20200314')

    dbtest = '<p>'
    for i in c:
        dbtest += i[1] + '</p>'

    return render_template("splash.html", dbtest=dbtest)


@app.route("/stocks")
def stocks():
    return render_template("stocks.html")


@app.route("/commodities")
def commodities():
    return render_template("commodities.html")


@app.route("/cart")
def cart():
    return render_template("cart.html")


# can delete this later - just for testing getting data from database!
@app.route("/timeline")
def timeline():
    name = 'AAPL'
    connection = None
    try:
        connection = cx_Oracle.connect(username, password, dsn)

    except cx_Oracle.Error as error:
        print(error)
        connection.close()

    c = connection.cursor()
    c.execute('SELECT dateID, ' + name + ' FROM Stocks s')

    min_price = connection.cursor()
    min_price.execute('SELECT MIN( ' + name + ' ) FROM Stocks s WHERE s.AAPL > 0')
    min_price = '$' + [str(i[0]) for i in min_price][0]
    min_date = connection.cursor()
    min_date.execute(
        'SELECT dateID FROM Stocks s WHERE s.' + name + ' = (SELECT MIN(' + name + ') FROM Stocks s WHERE s.' + name + ' > 0)')
    min_date = date_prettify([str(i[0]) for i in min_date][0])

    max_price = connection.cursor()
    max_price.execute('SELECT MAX( ' + name + ' ) FROM Stocks s WHERE s.AAPL > 0')
    max_price = '$' + [str(i[0]) for i in max_price][0]
    max_date = connection.cursor()
    max_date.execute(
        'SELECT dateID FROM Stocks s WHERE s.' + name + ' = (SELECT MAX(' + name + ') FROM Stocks s WHERE s.' + name + ' > 0)')
    max_date = date_prettify([str(i[0]) for i in max_date][0])

    data_points = {}
    for i in c:
        data_points[int(i[0])] = i[1]

    data_json = json.dumps(data_points)

    # return render_template("timeline.html", data=dbtest)
    return render_template("timeline.html",
                           name=name,
                           max=max_price,
                           max_date=max_date,
                           min=min_price,
                           min_date=min_date,
                           data=data_json)


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


if __name__ == "__main__":
    app.run(port=8000, debug=True)
