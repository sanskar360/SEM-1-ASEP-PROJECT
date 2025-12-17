from flask import Flask, render_template,request, redirect, url_for, flash, session
from database import load_orders_from_db, add_user_to_db, add_order_to_db, login_user_from_db, user_from_addresses_db,load_users_from_db, load_orders_for_admin_from_db, update_order_status_in_db
from sqlalchemy import create_engine, text

app = Flask(__name__)
app.secret_key = "mysecret123"


@app.route("/")
def home():
    return render_template("home.html")

ADMIN_ID = 13
@app.route("/track_orders", methods=["GET", "POST"])  
def track_orders():
    print("METHOD:", request.method)

    user_id = session.get("user_id")

    if user_id is None:
        return redirect(url_for("login"))
    
    user_id = int(user_id)

    if request.method == "POST" and user_id == ADMIN_ID:
        print("🔥 POST BLOCK ENTERED")

        order_id = request.form.get("order_id")
        order_status = request.form.get("order_status")
        print("➡️ ORDER_ID:", order_id)
        print("➡️ ORDER_STATUS:", order_status)


        update_order_status_in_db(order_id, order_status)

        return redirect(url_for("track_orders"))
    
    if user_id == ADMIN_ID:
        orders = load_orders_for_admin_from_db()
        return render_template("admin_orders_table.html", orders=orders)

    orders = load_orders_from_db(user_id)
    return render_template("track_orders.html", orders = orders)


@app.route("/payments")
def payments():
    user_id = session.get("user_id")

    orders = load_orders_from_db(user_id)

    return render_template("payments.html", orders = orders)


@app.route("/profile")
def profile():
    user_id = session.get("user_id")

    address =  user_from_addresses_db(user_id)

    return render_template("profile.html", address=address)


@app.route("/login", methods=["GET"])
def show_login_page():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    passwords = request.form.get("passwords")

    result = login_user_from_db(email, passwords)

    if not result:
        flash("User Not Found. Please Go to Sign Up", "error")
        return redirect(url_for("login_page"))
    
    if str(result.passwords) != str(passwords):
        flash("Incorrect Password. Try Again", "error")
        return redirect(url_for("login_page"))

    
    session["user_id"] = result.id
    session["username"] = result.username
    session["email"] = result.email

    flash("Login Successful!", "success")

    return redirect(url_for("home")) 


@app.route("/add_orders", methods=["GET", "POST"])
def add_orders():
    if request.method == "POST":
        order_data = {
            "user_name": request.form.get("user_name"),
            "phone_no": request.form.get("phone_no"),
            "pincode": request.form.get("pincode"),
            "alternate_phone_no": request.form.get("alternate_phone_no"),
            "state": request.form.get("state"),
            "city": request.form.get("city"),
            "house_no": request.form.get("house_no"),
            "service": request.form.get("service"),
            "order_date": request.form.get("order_date"),
            "num_of_items": request.form.get("num_of_items"),
            "patment_method": request.form.get("patment_method"),
            "suggesstions": request.form.get("suggesstions"),
        }

        result = add_order_to_db(order_data)

        if result.get("error"):
            flash(result["error"], "error")
            return redirect(url_for("add_orders"))

        flash("Order added successfully!", "success")
        return redirect(url_for("add_orders"))

    return render_template("add_orders.html")


@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        form_data = {
            "email": request.form.get("email"),
            "username": request.form.get("username"),
            "passwords": request.form.get("passwords")
        }

        try:
            add_user_to_db(form_data)
            return "Signup successful!"
        except Exception as e:
            return "Your Entered Details Are already Registered go to login"

    return render_template("sign_up.html")


@app.route("/logout")
def logout():
    session.clear()   
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))


@app.route("/admin_users_table")
def admin_users_table():

    id = 1

    users = load_users_from_db(id)

    return render_template("admin_users_table", users = users)


@app.route("/admin_orders_table")
def admin_orders_table():
    return render_template("admin_orders_table")