from flask import Flask, render_template,request, redirect, url_for, flash, session
from datetime import date, timedelta
from database import load_orders_from_db, add_user_to_db, login_user_from_db, user_from_addresses_db, get_todays_orders_count,get_addresses_from_db, add_address_to_db,delete_address_from_db,get_all_services,get_vendors,get_address_by_id,get_items_for_vendor,get_address_by_id, insert_order, insert_order_items

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

# Admin routes

@app.route("/admin_delivery_boys")
def delivery_boys():
    return render_template("admin_delivery_boys.html")

@app.route("/admin_users_table")
def users_table():
    return render_template("admin_users_table.html")

@app.route("/admin_vendors")
def admin_vendors():
    return render_template("admin_vendors.html")

@app.route("/admin_payments")
def admin_payment():
    return render_template("admin_payments.html")

@app.route("/admin_orders_table")
def admin_orders():
    return render_template("admin_orders_table.html")




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


    orders = load_orders_from_db(user_id)
    return render_template("track_orders.html", orders = orders)


@app.route("/payments", methods=["GET", "POST"])
def payments():
    user_id = session.get("user_id")

    if user_id is None:
        flash("Login First","error")
        return redirect(url_for("login"))
        
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
    print(ADMIN_ID)
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

    user_id = session.get("user_id")
    print(user_id)

    if user_id == ADMIN_ID:
        print("running")
        return redirect(url_for("users_table"))

    flash("Login Successful!", "success")
    return redirect(url_for("home")) 


@app.route("/add_orders/<int:service_id>/<int:address_id>/<int:vendor_id>")
def add_orders(service_id, address_id, vendor_id):
    if not service_id:
        flash("Please Select a service", "error")
        return redirect(url_for("services"))
    
    if not address_id:
        flash("Please Select a Address", "error")
        return redirect(url_for("select_address"))
    
    if not vendor_id:
        flash("Please Select a vendor", "error")
        return redirect(url_for("vendors"))
    
    items = get_items_for_vendor(vendor_id, service_id)

    address = get_address_by_id(address_id)

    
    return render_template(
        "add_orders.html",
        address=address,
        service_id = service_id,
        address_id = address_id,
        vendor_id = vendor_id,
        items=items
    )


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

@app.route("/services")
def services():
    services = get_all_services()
    return render_template("services.html", services=services)

@app.route("/select_address")
def select_address():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login"))

    service_id = request.args.get("service_id")

    addresses = get_addresses_from_db(user_id)  

    return render_template(
        "select_address.html",
        addresses=addresses,
        service_id=service_id
    )

@app.route("/vendors")
def vendors():

    service_id = request.args.get("service_id")
    address_id = request.args.get("address_id")

    print(service_id)
    if not service_id:
        return redirect(url_for("services"))
    
    if not address_id:
        flash("Please Select A Address or Add a New one", "error")
        return redirect(url_for("select_address", service_id=service_id))


    address = get_address_by_id(address_id)

    vendors = get_vendors(
        service_id,
        address.city,
        address.pincode
    )

    return render_template(
        "vendors.html",
        vendors=vendors,
        service_id=service_id,
        address_id=address_id
    )

@app.route("/place_order", methods=["POST"])
def place_order():

    service_id = request.form.get("service_id")
    vendor_id = request.form.get("vendor_id")
    address_id = request.form.get("address_id")

    item_ids = request.form.getlist("item_ids[]")
    qtys = request.form.getlist("qtys[]")
    prices = request.form.getlist("prices[]")

    # calculate total
    total = 0
    for i in range(len(item_ids)):
        qty = int(qtys[i])
        price = float(prices[i])
        total += qty * price

    # insert order
    order_id = insert_order(vendor_id, service_id, address_id, total)

    # insert items
    insert_order_items(order_id, item_ids, qtys, prices)

    return redirect(url_for("track_orders"))

# Routes For Admin Panel data

@app.route("")