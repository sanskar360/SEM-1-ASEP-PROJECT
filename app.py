from flask import Flask, render_template,request, redirect, url_for, flash, session,jsonify
from database import  add_user_to_db, get_admin_orders2,  update_delivery_order_status, login_user_from_db, user_from_addresses_db, get_addresses_from_db, add_address_to_db,delete_address_from_db,get_all_services,get_vendors,get_vendors2, get_address_by_id,get_items_for_vendor,get_address_by_id, insert_order, insert_order_items,get_delivery_boys,assign_delivery_boy,get_admin_orders,insert_delivery_boy, toggle_delivery_boy_status,get_payments,  update_user_db, delete_user_db,get_users,get_delivery_boy_orders,get_delivery_records,get_user_orders,get_order_details,update_order_status,get_pending_orders, get_dashboard_stats,get_active_orders,update_active_order_status,get_active_orders_stats,get_history_stats,get_history_orders,add_vendor_service, get_vendor_services,delete_vendor_service,get_vendor_address,save_vendor_address, get_delivery_boy_id, update_delivery_boy_busy_status,mark_order_payment_paid,create_vendor,get_vendor_id_by_user_id,get_delivery_boy_profile1,get_recent_deliveries,get_delivery_boy_profile



app = Flask(__name__)
app.secret_key = "mysecret123"

# Login routes


from werkzeug.security import check_password_hash


@app.route("/login", methods=["GET"])
def show_login_page():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():


    email = request.form.get("email")
    passwords = request.form.get("passwords")

    result = login_user_from_db(email, passwords)

    if not result:

        flash(
            "User Not Found. Please Go to Sign Up",
            "error"
        )

        return redirect(
            url_for("show_login_page")
        )

    # HASH PASSWORD CHECK
    if not check_password_hash(
        result["password_hash"],
        str(passwords)
    ):

        flash(
            "Incorrect Password. Try Again",
            "error"
        )

        return redirect(
            url_for("show_login_page")
        )

    session["user_id"] = result["id"]
    session["username"] = result["username"]
    session["email"] = result["email"]
    session["role"] = result["role"]

    user_id = session.get("user_id")

    print(user_id)

    # ADMIN
    if result["role"] == "admin":

        return redirect(
            url_for("users_table")
        )

    # DELIVERY
    elif result["role"] == "delivery":

        boy_id = get_delivery_boy_id(user_id)
        profile = get_delivery_boy_profile(boy_id)


        orders = get_delivery_boy_orders(boy_id)
        deliveries = get_delivery_records(boy_id)

        print("User ID:", user_id)
        print("Boy ID:", boy_id)

        return render_template(
            "delivery_assigned.html",
            orders=orders,
            profile=profile,
            deliveries=deliveries
        )

    # VENDOR
    elif result["role"] == "vendor":

        session["vendor_id"] = user_id

        return redirect(
            url_for("vendors_incoming")
        )

    flash(
        "Login Successful!",
        "success"
    )

    return redirect(
        url_for("home")
    )


# Admin routes

@app.route("/admin_delivery_boys")
def delivery_boys():
    delivery_boys = get_delivery_boys()
    print(delivery_boys)
    return render_template("admin_delivery_boys.html",delivery_boys=delivery_boys)

@app.route("/admin_users_table")
def users_table():
    users = get_users()

    return render_template(
        "admin_users_table.html",
        users=users
    )
@app.route("/admin_vendors")
def admin_vendors():
    vendors = get_vendors2()
    return render_template(
        "admin_vendors.html",
        vendors=vendors
    )

@app.route("/admin_payments")
def admin_payment():
    payments = get_payments()

    return render_template(
        "admin_payments.html",
        payments=payments
    )

@app.route("/admin_orders_table")
def admin_orders():
    orders = get_admin_orders()
    orders2 = get_admin_orders2()
    delivery_boys = get_delivery_boys()

    return render_template(
        "admin_orders_table.html",
        orders=orders,
        orders2 = orders2,
        delivery_boys=delivery_boys
    )

@app.route("/add_vendor", methods=["POST"])
def add_vendor():

    try:
        data = request.get_json()

        generated_password = data.get("email") + "23"
        hashed_password = generate_password_hash(generated_password)

        create_vendor(
            name=data.get("name"),
            email=data.get("email"),
            password=hashed_password,
            phone=data.get("phone"),
            city=data.get("city"),
            state=data.get("state"),
            pincode=data.get("pincode"),
            street_address=data.get("street_address"),
            status=data.get("status"),
            service_ids=data.get("service_ids", [])
        )

        return jsonify({
            "success": True,
            "message": "Vendor added successfully"
        })

    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
    

# How it works section

@app.route("/how_it_works")
def how_it_works():
    return render_template("how_it_works.html")

# Delivery boy routes

@app.route("/delivery_assigned")
def delivery_assigned():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("login"))

    boy_id = get_delivery_boy_id(user_id)

    if not boy_id:
        return "Delivery boy not found", 404

    profile = get_delivery_boy_profile(boy_id)

    orders = get_delivery_boy_orders(boy_id)

    deliveries = get_delivery_records(boy_id)

    return render_template(
        "delivery_assigned.html",
        orders=orders,
        profile=profile,
        deliveries=deliveries
    )

@app.route(
    "/delivery_update_status",
    methods=["POST"]
)

@app.route(
    "/delivery_update_status",
    methods=["POST"]
)
def delivery_update_status():

    order_id = request.form.get("order_id")

    new_status = request.form.get("order_status")

    # ───────── UPDATE ORDER STATUS ─────────

    update_delivery_order_status(
        order_id,
        new_status
    )

    # ───────── GET DELIVERY BOY ID ─────────

    boy_id = get_delivery_boy_id(order_id)

    # ───────── BUSY STATES ─────────

    if new_status in [
        "picked_up",
        "picked_from_vendor"
    ]:

        update_delivery_boy_busy_status(
            boy_id,
            True
        )

    # ───────── FREE STATES ─────────

    elif new_status in [
        "delivered_to_vendor",
        "delivered"
        ]:

        update_delivery_boy_busy_status(
            boy_id,
            False
        )


    return redirect("/delivery_assigned")

@app.route("/delivery_history")
def delivery_history():
    user_id = session.get("user_id")
    role = session.get("role")
    if role ==  "delivery":
        boy_id = user_id  
        deliveries = get_delivery_records(boy_id)
        return render_template(
            "delivery_history.html",
             deliveries=deliveries
            )
    
@app.route("/mark-payment-paid/<int:order_id>", methods=["POST"])
def mark_payment_paid(order_id):

    method = request.args.get("method")
    rider_id = session.get("delivery_boy_id")

    mark_order_payment_paid(
        order_id,
        method,
        rider_id
    )

    return redirect("/delivery_assigned")

@app.route("/delivery_login.html")
def delivery_login():
    return render_template("delivery_login.html")

@app.route("/delivery-profile")
def delivery_profile():

    user_id = session["user_id"]

    boy_id = get_delivery_boy_id(user_id)

    profile = get_delivery_boy_profile1(boy_id)

    recent_deliveries = get_recent_deliveries(boy_id)

    return render_template(
        "delivery_profile.html",
        profile=profile,
        recent_deliveries=recent_deliveries
    )

# Vendors panel Routes

@app.route("/vendors_history")
def vendors_history():
    return render_template("vendors_history.html")

@app.route("/vendors_incoming.html")
def vendors_incoming():
    return render_template("vendors_incoming.html")

@app.route("/vendors_processing.html")
def vendors_processing():
    return render_template("vendors_processing.html")

@app.route("/vendors_services.html")
def vendors_services():
    return render_template("vendors_services.html")

@app.route("/vendors_address")
def vendors_addresses():
    return render_template("vendors_addresses.html")


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/track_orders", methods=["GET", "POST"])  
def track_orders():

    user_id = session.get("user_id")   # login required

    orders = get_user_orders(user_id)

    return render_template(
        "track_orders.html",
        orders=orders
    )




@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if user_id is None:
        flash("Login First","error")
        return redirect(url_for("show_login_page"))
    
    address =  user_from_addresses_db(user_id)
    return render_template("profile.html", address=address)


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

# Signup routes

from werkzeug.security import generate_password_hash


@app.route('/signup', methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        hashed_password = generate_password_hash(
            str(request.form.get("passwords"))
        )

        form_data = {

            "email": request.form.get("email"),

            "username": request.form.get("username"),

            # STORE HASHED PASSWORD
            "password_hash": hashed_password,

            # DEFAULT ROLE
            "role": "customer"
        }

        try:

            add_user_to_db(form_data)

            flash(
                "Signup Successful!",
                "success"
            )

            return render_template(
                "home.html"
            )

        except Exception as e:

            print(e)

            flash(
                "Signup Unsuccessful!",
                "error"
            )

            return render_template(
                "sign_up.html"
            )

    return render_template(
        "sign_up.html"
    )


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


# SCORING MECHANISM FOR VENDORS

def score_vendors(vendors, user_pincode):
    scored = []

    for v in vendors:
        # --- Convert safely ---
        rating = float(v.rating or 0)
        active_orders = int(v.active_orders or 0)

        # Distance score
        distance_score = 1 if str(v.pincode) == str(user_pincode) else 0.7

        # Availability score
        availability_score = 1 / (1 + active_orders)

        # Rating score
        rating_score = rating / 5

        # Final score
        final_score = (
            0.5 * availability_score +
            0.3 * rating_score +
            0.2 * distance_score
        )

        scored.append({
            "vendor": v,
            "score": final_score
        })

    scored.sort(key=lambda x: x["score"], reverse=True)

    return [item["vendor"] for item in scored]


# 🔥 VENDOR LIST PAGE
@app.route("/vendors")
def vendors():

    service_id = request.args.get("service_id")
    address_id = request.args.get("address_id")

    if not service_id:
        return redirect(url_for("services"))

    if not address_id:
        flash("Please Select An Address", "error")
        return redirect(url_for("select_address", service_id=service_id))

    address = get_address_by_id(address_id)

    vendors = get_vendors(
        service_id,
        address.city,
        address.pincode
    )

    # 🔥 Apply smart ranking
    vendors = score_vendors(vendors, address.pincode)

    return render_template(
        "vendors.html",
        vendors=vendors,
        service_id=service_id,
        address_id=address_id
    )

@app.route("/place_order", methods=["POST"])
def place_order():

    user_id = session.get("user_id")
    service_id = request.form.get("service_id")
    vendor_id = request.form.get("vendor_id")
    address_id = request.form.get("address_id")
    payment_method = request.form.get("payment_method")
    suggestion = request.form.get("suggestion")

    item_ids = request.form.getlist("item_ids[]")
    qtys = request.form.getlist("qtys[]")
    prices = request.form.getlist("prices[]")

    payment_status = "pending"

    # Calculate total and check if any item was selected
    total = 0
    has_items = False

    for i in range(len(item_ids)):
        qty = int(qtys[i])
        price = float(prices[i])

        if qty > 0:
            has_items = True

        total += qty * price

    # Validation
    if not has_items:
        flash("Please Enter Items", "error")
        return redirect(request.referrer)

    # Insert order
    order_id = insert_order(
        vendor_id,
        service_id,
        address_id,
        total,
        payment_method,
        payment_status,
        user_id,
        suggestion
    )

    # Insert order items
    insert_order_items(order_id, item_ids, qtys, prices)

    flash("Order placed successfully!", "success")
    return redirect(url_for("track_orders"))

# admin function routes

@app.route("/assign_delivery", methods=["POST"])
def assign_delivery():

    data = request.get_json()

    order_id = data.get("order_id")
    delivery_boy_id = data.get("delivery_boy_id")

    assign_delivery_boy(order_id, delivery_boy_id)

    return {"status": "success"}

@app.route("/add_delivery_boy", methods=["GET", "POST"])
def add_delivery_boy():

    if request.method == "POST":
        data = request.get_json()

        name = data.get("name")
        phone = data.get("phone")
        status = data.get("status")
        email = data.get("email")

        insert_delivery_boy(name, phone, email, status)

        return {"status": "success"}

    return render_template("admin_delivery_boys.html")

@app.route("/toggle_delivery_status", methods=["POST"])
def toggle_delivery_status():

    data = request.get_json()
    code = data.get("code")

    new_status = toggle_delivery_boy_status(code)

    return {"status": "success", "new_status": new_status}

@app.route("/update_user", methods=["POST"])
def update_user():
    data = request.get_json()

    update_user_db(data["id"], data["role"], data["status"])

    return {"status": "success"}

@app.route("/delete_user", methods=["POST"])
def delete_user():
    data = request.get_json()

    delete_user_db(data["id"])

    return {"status": "success"}

@app.route("/order_details/<int:order_id>")
def order_details(order_id):

    order = get_order_details(order_id)

    return {
        "id": order.id,
        "name": order.user_name,
        "phone": order.phone_no,
        "address": f"{order.city}, {order.state}",
        "payment": f"{order.payment_method} ({order.payment_status})"
    }

@app.route("/api/pending_orders")
def pending_orders():

    user_id = session.get("user_id")
    vendor_id = get_vendor_id_by_user_id(user_id)
 
    print("Vendor id")
    print(vendor_id)

    orders = get_pending_orders(vendor_id)
    print(orders)

    data = []
    for o in orders:
        data.append({
            "id": o.id,
            "user": f"User {o.user_id}",
            "service": o.service_name,
            "pickup_date": str(o.created_at),
            "payment": o.payment_status,
            "amount": o.total_amount
        })

    return jsonify(data)

@app.route("/accept_order", methods=["POST"])
def accept_order():
    order_id = request.json.get("order_id")

    update_order_status(order_id, "accepted")

    return jsonify({"success": True})

@app.route("/reject_order", methods=["POST"])
def reject_order():
    order_id = request.json.get("order_id")

    update_order_status(order_id, "rejected")

    return jsonify({"success": True})

@app.route("/api/dashboard_stats")
def dashboard_stats():

    user_id = session.get("user_id")
    vendor_id = get_vendor_id_by_user_id(user_id)

    stats = get_dashboard_stats(vendor_id)

    return jsonify({
        "new_today": stats.new_today or 0,
        "accepted": stats.accepted or 0,
        "rejected": stats.rejected or 0
    })

# routes for vendors/processing

@app.route("/api/active_orders")
def active_orders():

    user_id = session.get("user_id")
    vendor_id = get_vendor_id_by_user_id(user_id)

    orders = get_active_orders(vendor_id)

    data = []

    for o in orders:
        data.append({
            "id": o.id,
            "user": f"User {o.user_id}",
            "service": o.service_name,
            "accepted": str(o.created_at),
            "status": o.status
        })

    return jsonify(data)

@app.route("/update_order_status", methods=["POST"])
def update_order_status_route():

    data = request.json

    order_id = data.get("order_id")
    status = data.get("status")

    update_active_order_status(order_id, status)

    return jsonify({
        "success": True
    })

@app.route("/api/active_stats")
def active_stats():

    vendor_id = session.get("vendor_id")
    

    stats = get_active_orders_stats(vendor_id)
    print(stats)
    return jsonify({
        "accepted": stats.accepted or 0,
        "processing": stats.processing or 0,
        "ready": stats.ready_count or 0
    })

# routes for vendors/history

@app.route("/api/history_orders")
def history_orders():

    vendor_id = session.get("vendor_id")

    orders = get_history_orders(vendor_id)

    data = []

    for o in orders:

        data.append({
            "id": o.id,
            "user": f"User {o.user_id}",
            "service": o.service_name,
            "date": str(o.created_at),
            "status": o.status,
            "amount": o.total_amount
        })

    return jsonify(data)

@app.route("/api/history_stats")
def history_stats():

    vendor_id = session.get("vendor_id")

    stats = get_history_stats(vendor_id)

    return jsonify({
        "total_orders": stats.total_orders or 0,
        "delivered": stats.delivered or 0,
        "rejected": stats.rejected or 0
    })

# vendors/services

@app.route("/add_service", methods=["POST"])
def add_service_route():

    vendor_id = session.get("vendor_id")

    data = request.json

    add_vendor_service(

        vendor_id,

        data.get("name"),
        data.get("price")

    )

    return jsonify({
        "success": True
    })

@app.route("/api/vendor_services")
def vendor_services():

    user_id = session.get("user_id")
    vendor_id = get_vendor_id_by_user_id(user_id)

    services = get_vendor_services(vendor_id)

    data = []

    for s in services:

        data.append({

            "id": s.id,
            "name": s.name,
            "price": s.price

        })

    return jsonify(data)

@app.route(
    "/delete_service/<int:service_id>",
    methods=["DELETE"]
)
def delete_service(service_id):

    user_id = session.get("user_id")
    vendor_id = get_vendor_id_by_user_id(user_id)

    delete_vendor_service(
        service_id,
        vendor_id
    )

    return jsonify({
        "success": True
    })

# vendors addresses

@app.route(
    "/save_vendor_address",
    methods=["POST"]
)
def save_vendor_address_route():

    user_id = session.get("user_id")
    vendor_id = get_vendor_id_by_user_id(user_id)


    data = request.json

    save_vendor_address(

        vendor_id,

        data.get("street"),
        data.get("city"),
        data.get("state"),
        data.get("pin"),
        data.get("phone")

    )

    return jsonify({
        "success": True
    })

@app.route("/api/vendor_address")
def vendor_address():

    vendor_id = session.get("vendor_id")

    address = get_vendor_address(vendor_id)

    if not address:

        return jsonify({})

    return jsonify({

        "street": address.street_address,
        "city": address.city,
        "state": address.state,
        "pin": address.pincode,
        "phone": address.phone

    })