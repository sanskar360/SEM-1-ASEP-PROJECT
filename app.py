from flask import Flask, render_template,request


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/add_orders")
def add_orders():
    return render_template("add_orders.html")

@app.route("/track_orders")
def track_orders():
    return render_template("track_orders.html")

@app.route("/payments")
def payments():
    return render_template("payments.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route('/signup')
def signup():
    return render_template("sign_up.html")


