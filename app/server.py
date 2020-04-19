from flask import Flask, render_template
import cx_Oracle

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
		connection = cx_Oracle.connect(username,password,dsn)

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
def dashboard():
	return render_template("stocks.html")

@app.route("/commodities")
def timeline():
	return render_template("commodities.html")

@app.route("/cart")
def cart():
	return render_template("cart.html")

if __name__ == "__main__":
	app.run(port=8000, debug=True)