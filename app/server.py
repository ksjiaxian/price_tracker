from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def splash():
	return render_template("splash.html")

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