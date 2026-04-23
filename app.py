from flask import Flask, render_template,request, redirect, url_for, flash, session
from datetime import date, timedelta
from database import load_orders_from_db, add_user_to_db, login_user_from_db, user_from_addresses_db, load_orders_for_admin_from_db, update_order_status_in_db, load_users_for_admin_from_db, update_payment_status_in_db, get_todays_orders_count,get_addresses_from_db, add_address_to_db,delete_address_from_db,add_order_to_db

app = Flask(__name__)
app.secret_key = "mysecret123"


def predict_date(service, items):
    
        if service == "iron" and items >= 10:
            days = 5
        elif service == "iron":
            days = 3

        elif service == "wash_fold" and items >= 10:
            days = 5
        elif service == "wash_fold":
            days = 2

        elif service == "dry_clean" and items >= 10:
            days = 6
        elif service == "dry_clean":
            days = 3

        elif service == "steam_iron" and items >= 10:
            days = 5
        elif service == "steam_iron":
            days = 2

        elif service == "wash_iron" and items >= 10:
            days = 5
        elif service == "wash_iron":
            days = 3
        else:
            days = 2

        todays_orders = get_todays_orders_count()
        if todays_orders > 20:
            days += 1

        return date.today() + timedelta(days=days)

@app.context_processor
def inject_admin_id():
    return dict(ADMIN_ID=ADMIN_ID)


@app.route("/")
def home():
    return render_template("home.html")

ADMIN_ID = 13
@app.route("/track_orders", methods=["GET", "POST"])  
def track_orders():

    user_id = session.get("user_id")

    if user_id is None:
        flash("Login First","error")
        return redirect(url_for("login"))
    
    user_id = int(user_id)

    if request.method == "POST" and user_id == ADMIN_ID:

        order_id = request.form.get("order_id")
        order_status = request.form.get("order_status")

        update_order_status_in_db(order_id, order_status)

        return redirect(url_for("track_orders"))
    
    if user_id == ADMIN_ID:
        orders = load_orders_for_admin_from_db()
        return render_template("admin_orders_table.html", orders=orders)

    orders = load_orders_from_db(user_id)
    return render_template("track_orders.html", orders = orders)


@app.route("/payments", methods=["GET", "POST"])
def payments():
    user_id = session.get("user_id")

    if user_id is None:
        flash("Login First","error")
        return redirect(url_for("login"))

    if request.method == "POST" and user_id == ADMIN_ID:
        payment_status = request.form.get("payment_status")
        order_id = request.form.get("order_id")
        update_payment_status_in_db(order_id, payment_status) 
        return redirect(url_for("payments"))
    
    if user_id == ADMIN_ID:
            orders = load_orders_for_admin_from_db()
            return render_template("admin_payments.html", orders=orders)
        
    orders = load_orders_from_db(user_id)
    return render_template("payments.html", orders = orders)


@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if user_id is None:
        flash("Login First","error")
        return redirect(url_for("show_login_page"))
    
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
        return redirect(url_for("show_login_page"))
    
    if str(result.passwords) != str(passwords):
        flash("Incorrect Password. Try Again", "error")
        return redirect(url_for("show_login_page"))

    
    session["user_id"] = result.id
    session["username"] = result.username
    session["email"] = result.email

    flash("Login Successful!", "success")
    return redirect(url_for("home")) 


@app.route("/add_orders", methods=["GET", "POST"])
@app.route("/add_orders", methods=["GET", "POST"])
def add_orders():
    user_id = session.get("user_id")

    if not user_id:
        flash("Login First", "error")
        return redirect(url_for("show_login_page"))

    if request.method == "POST":

        service = request.form.get("service")
        items = int(request.form.get("num_of_items"))

        delivery_date = predict_date(service, items)

        order_data = {
            "service": service,
            "num_of_items": items,
            "patment_method": request.form.get("patment_method"),
            "suggesstions": request.form.get("suggesstions"),
            "delivery_date": delivery_date
        }

        result = add_order_to_db(order_data)

        if result.get("error"):
            flash(result["error"], "error")
        else:
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
            flash("Signup Successful!", "success")
            return render_template("home.html")
        except Exception as e:
            flash("Signup Unsuccessful!", "error")
            return render_template("sign_up.html")

    return render_template("sign_up.html")


@app.route("/logout")
def logout():
    session.clear()   
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))


@app.route("/admin_users_table")
def admin_users_table():
    return render_template("admin_users_table")


@app.route("/admin_orders_table")
def admin_orders_table():
    return render_template("admin_orders_table")


@app.route("/admin_payments")
def admin_payments():
    return render_template("admin_payments")

@app.route("/manage_addresses", methods=["GET", "POST"])
def manage_addresses():
    user_id = session.get("user_id")

    if user_id is None:
        flash("Login First", "error")
        return redirect(url_for("show_login_page"))

    if request.method == "POST":
        result = add_address_to_db(request.form)

        if result.get("error"):
            flash(result["error"], "error")
        else:
            flash("Address added successfully!", "success")

        return redirect(url_for("manage_addresses"))

    addresses = get_addresses_from_db(user_id)

    return render_template("manage_addresses.html", addresses=addresses)

@app.route("/delete_address/<int:address_id>")
def delete_address(address_id):
    user_id = session.get("user_id")

    if not user_id:
        flash("Login required", "error")
        return redirect(url_for("show_login_page"))

    delete_address_from_db(address_id, user_id)

    flash("Address deleted successfully", "success")
    return redirect(url_for("manage_addresses"))