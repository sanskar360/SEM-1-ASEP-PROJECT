from sqlalchemy import create_engine, text
from flask import flash, redirect, url_for, session
import os

DB_USER = "avnadmin"
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = "mysql-2c884b13-sanskarvijaybhilavade-7834.j.aivencloud.com"
DB_PORT = "12201"
DB_NAME = "defaultdb"

db_connection_string = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

engine = create_engine(
    db_connection_string,
    connect_args={"ssl": {"ca": "ca1.pem"}}
)
                                                                                            
def load_orders_from_db(user_id):
    with engine.connect() as conn:
        orders_querry = text("""
            SELECT order_date, service, num_of_items, suggesstions, order_status, patment_method,payment_status, id, delivery_date, user_id FROM orders
            WHERE user_id = :user_id
                        """)
        result = conn.execute(orders_querry, {"user_id":user_id}).fetchall()

        return [dict(row._mapping) for row in result]


def add_user_to_db(form_data):
    with engine.connect() as conn:
        query = text("""
            INSERT INTO users (email, username, passwords)
            VALUES (:email, :username, :passwords)
        """)

        conn.execute(query, form_data)
        conn.commit()


    
def login_user_from_db(email, passwords):

    with engine.connect() as conn:
        querry_login = text("""
            SELECT id, passwords, username, email FROM users
            WHERE email = :email
                """)
        
        result = conn.execute(querry_login, {"email": email}).fetchone()

        return result
    
def user_from_addresses_db(user_id):

    with engine.connect() as conn:
        querry_address = text("""
            SELECT phone_no, alternate_phone_no FROM address
            WHERE user_id = :user_id           
                             """)
        
        result = conn.execute(querry_address, {"user_id": user_id}).fetchone()

        return dict(result._mapping) if result else None  

def load_users_from_db(user_id):
    with engine.connect() as conn:
        orders_querry = text("""
            SELECT email, username, password id FROM users
            WHERE id = :id
                        """)
        result = conn.execute(orders_querry, {"id":id}).fetchall()

        return [dict(row._mapping) for row in result]
    

def load_orders_for_admin_from_db():
    with engine.connect() as conn:
        orders_querry = text("""
            SELECT order_date, order_status, patment_method, service, num_of_items, suggesstions, user_id, payment_status,id FROM orders
                        """)
        result = conn.execute(orders_querry).fetchall()

        return [dict(row._mapping) for row in result]

def update_order_status_in_db(order_id, order_status):
    if order_id is None:
        print("ERROR: order_id is None")
        return

    with engine.begin() as conn:   
        conn.execute(
            text("""
                UPDATE orders
                SET order_status = :status
                WHERE id = :order_id
            """),
            {
                "status": order_status,
                "order_id": int(order_id)
            }
        )

def update_payment_status_in_db(order_id,payment_status):
    if order_id is None:
        return ("ERROR: order_id is None")

    with engine.begin() as conn:   
        conn.execute(
            text("""
                UPDATE orders
                SET payment_status = :status
                WHERE id = :order_id
            """),
            {
                "status": payment_status,
                "order_id": int(order_id)
            }
        )

def load_users_for_admin_from_db():
    with engine.connect() as conn:
        users_querry = text("""
            SELECT email, username, passwords FROM users
                        """)
        result = conn.execute(users_querry).fetchall()

        return [dict(row._mapping) for row in result]
    

def get_todays_orders_count():
    with engine.connect() as conn:
        return conn.execute(
            text("""
                SELECT COUNT(*) 
                FROM orders
                WHERE order_date = CURDATE()
            """)
        ).scalar()

def add_address_to_db(form):
    user_id = session.get("user_id")

    if not user_id:
        return {"error": "User not logged in"}

    address_data = {
        "user_name": form.get("user_name"),
        "phone_no": form.get("phone_no"),
        "alternate_phone_no": form.get("alternate_phone_no"),
        "pincode": form.get("pincode"),
        "state": form.get("state"),
        "city": form.get("city"),
        "house_no": form.get("house_no"),
        "user_id": user_id
    }

    # 🔹 VALIDATION (same style as yours)
    if len(address_data["phone_no"]) != 10:
        return {"error": "Phone must be 10 digits"}

    required_fields = {
        "user_name": "Enter name",
        "phone_no": "Enter phone",
        "pincode": "Enter pincode",
        "state": "Enter state",
        "city": "Enter city",
        "house_no": "Enter house number"
    }

    for field, msg in required_fields.items():
        if not address_data.get(field):
            return {"error": msg}

    # 🔹 INSERT
    with engine.connect() as conn:
        query = text("""
            INSERT INTO address 
            (user_name, phone_no, alternate_phone_no, pincode, state, city, house_no, user_id)
            VALUES 
            (:user_name, :phone_no, :alternate_phone_no, :pincode, :state, :city, :house_no, :user_id)
        """)

        conn.execute(query, address_data)
        conn.commit()

    return {"success": True}

def get_addresses_from_db(user_id):
    with engine.connect() as conn:
        query = text("SELECT * FROM address WHERE user_id = :user_id")
        result = conn.execute(query, {"user_id": user_id})
        return result.fetchall()
    
def get_address_by_id(address_id):

    with engine.connect() as conn:
        query = text("""
            SELECT * FROM address
            WHERE id = :id
        """)

        result = conn.execute(query, {"id": address_id})

        return result.fetchone()
    
def delete_address_from_db(address_id, user_id):
    with engine.connect() as conn:
        query = text("""
            DELETE FROM address 
            WHERE id = :id AND user_id = :user_id
        """)
        conn.execute(query, {"id": address_id, "user_id": user_id})
        conn.commit()

    return {"success": True}

def get_all_services():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM services"))
        return result.fetchall()
    

def get_vendors(service_id, city, pincode):
    with engine.connect() as conn:
        query = text("""
            SELECT DISTINCT 
                v.id,
                v.name,
                v.rating,
                v.active_orders,
                v.city,
                v.pincode

            FROM vendors v

            JOIN vendor_services vs 
                ON v.id = vs.vendor_id

            WHERE 
                vs.service_id = :service_id
                AND v.city = :city
                AND v.status = 'Active'
        """)

        result = conn.execute(query, {
            "service_id": service_id,
            "city": city,
            "pincode": pincode
        })

        return result.fetchall()
    
def get_items_for_vendor(vendor_id, service_id):

    with engine.connect() as conn:
        query = text("""
            SELECT it.id, it.name, vs.price
            FROM vendor_services vs
            JOIN item_types it ON vs.item_type_id = it.id
            WHERE vs.vendor_id = :vendor_id
            AND vs.service_id = :service_id
        """)

        result = conn.execute(query, {
            "vendor_id": vendor_id,
            "service_id": service_id
        })

        return result.fetchall()
    
def get_address_by_id(address_id):
    with engine.connect() as conn:
        query = text("SELECT * FROM address WHERE id = :id")
        result = conn.execute(query, {"id": address_id})
        return result.fetchone()


#  INSERT ORDER
def insert_order(vendor_id, service_id, address_id, total, payment_method, payment_status, user_id, suggestion):

    with engine.connect() as conn:

        query = text("""
            INSERT INTO addd_orders (vendor_id, service_id, address_id, total_amount, payment_method, payment_status, user_id, suggestion)
            VALUES (:vendor_id, :service_id, :address_id, :total, :payment_method, :payment_status, :user_id, :suggestion)
        """)

        result = conn.execute(query, {
            "vendor_id": vendor_id,
            "service_id": service_id,
            "address_id": address_id,
            "total": total,
            "payment_method":payment_method,
            "payment_status":payment_status,
            "user_id":user_id,
            "suggestion":suggestion
        })

        conn.commit()

        return result.lastrowid   # return order_id


# INSERT ORDER ITEMS
def insert_order_items(order_id, item_ids, qtys, prices):

    with engine.connect() as conn:

        for i in range(len(item_ids)):
            qty = int(qtys[i])

            if qty > 0:
                query = text("""
                    INSERT INTO order_items (order_id, item_type_id, quantity, price)
                    VALUES (:order_id, :item_id, :qty, :price)
                """)

                conn.execute(query, {
                    "order_id": order_id,
                    "item_id": item_ids[i],
                    "qty": qty,
                    "price": prices[i]
                })

        conn.commit()

# functions for admin data

def get_delivery_boys():

    with engine.connect() as conn:

        query = text("""
            SELECT 
                db.id,
                db.code,
                db.name,
                db.phone,
                db.status,
                db.rating,
                db.is_busy,

                -- assigned orders
                (
                    SELECT COUNT(*) 
                    FROM addd_orders o
                    WHERE o.delivery_boy_id = db.id
                    AND o.status != 'delivered'
                ) AS assigned_orders,

                -- completed today
                (
                    SELECT COUNT(*)
                    FROM addd_orders o
                    WHERE o.delivery_boy_id = db.id
                    AND o.status = 'delivered'
                    AND DATE(o.updated_at) = CURDATE()
                ) AS completed_today

            FROM delivery_boys db
            WHERE db.is_busy = false
            ORDER BY db.id DESC
        """)

        return conn.execute(query).fetchall()
    
def assign_delivery_boy(order_id, delivery_boy_id):

    with engine.connect() as conn:
        query = text("""
            UPDATE addd_orders
            SET delivery_boy_id = :delivery_boy_id
            WHERE id = :order_id
        """)

        conn.execute(query, {
            "delivery_boy_id": delivery_boy_id,
            "order_id": order_id
        })

        conn.commit()


def get_admin_orders():

    with engine.connect() as conn:

        query = text("""
           SELECT 
            o.id,
            a.user_name AS customer_name,
            s.name AS service,
            o.created_at,
            o.payment_method,
            o.total_amount,
            o.suggestion,
            o.payment_status,
            o.status,

            SUM(oi.quantity) AS total_items

        FROM addd_orders o
        JOIN address a ON o.address_id = a.id
        JOIN services s ON o.service_id = s.id
        LEFT JOIN order_items oi ON oi.order_id = o.id
        WHERE o.status IN ('accepted','ready')

        GROUP BY o.id
        ORDER BY o.id DESC;
        """)

        return conn.execute(query).fetchall()
    
def get_admin_orders2():

    with engine.connect() as conn:

        query = text("""
           SELECT 
            o.id,
            a.user_name AS customer_name,
            s.name AS service,
            o.created_at,
            o.payment_method,
            o.total_amount,
            o.suggestion,
            o.payment_status,
            o.status,

            SUM(oi.quantity) AS total_items

        FROM addd_orders o
        JOIN address a ON o.address_id = a.id
        JOIN services s ON o.service_id = s.id
        LEFT JOIN order_items oi ON oi.order_id = o.id

        GROUP BY o.id
        ORDER BY o.id DESC;
        """)

        return conn.execute(query).fetchall()
    
def insert_delivery_boy(name, phone, status):

    with engine.connect() as conn:

        # 🔥 generate code like DB-006
        result = conn.execute(text("SELECT COUNT(*) FROM delivery_boys"))
        count = result.scalar() + 1

        code = f"DB-{str(count).zfill(3)}"

        query = text("""
            INSERT INTO delivery_boys (code, name, phone, status)
            VALUES (:code, :name, :phone, :status)
        """)

        conn.execute(query, {
            "code": code,
            "name": name,
            "phone": phone,
            "status": status
        })

        conn.commit()

def toggle_delivery_boy_status(code):

    with engine.connect() as conn:

        # get current status
        result = conn.execute(
            text("SELECT status FROM delivery_boys WHERE code = :code"),
            {"code": code}
        ).fetchone()

        current_status = result.status
        new_status = "inactive" if current_status == "active" else "active"

        conn.execute(
            text("UPDATE delivery_boys SET status = :status WHERE code = :code"),
            {"status": new_status, "code": code}
        )

        conn.commit()

        return new_status
    
def get_payments():

    with engine.connect() as conn:

        query = text("""
            SELECT 
                o.id,
                o.total_amount,
                o.payment_method,
                o.created_at,
                a.user_name AS customer_name
            FROM addd_orders o
            JOIN address a ON o.address_id = a.id
            ORDER BY o.id DESC
        """)

        return conn.execute(query).fetchall()
    

def get_users():

    with engine.connect() as conn:

        query = text("""
            SELECT 
                id,
                name,
                role,
                status,
                created_at
            FROM users_table
            ORDER BY id DESC
        """)

        return conn.execute(query).fetchall()
    
def update_user_db(user_id, role, status):

    with engine.connect() as conn:
        conn.execute(text("""
            UPDATE users_table
            SET role = :role, status = :status
            WHERE id = :id
        """), {
            "role": role,
            "status": status,
            "id": user_id
        })

        conn.commit()

def delete_user_db(user_id):

    with engine.connect() as conn:
        conn.execute(text("DELETE FROM users_table WHERE id = :id"), {"id": user_id})
        conn.commit()

#Function for delivery boys page

def get_delivery_boy_orders(boy_id):

    with engine.connect() as conn:

        query = text("""
            SELECT 
                o.id,
                o.created_at,
                o.status,
                o.payment_method,

                a.user_name,
                a.phone_no,
                a.city,
                a.state,
                a.pincode,

                s.name AS service_name,

                -- total items
                (
                    SELECT SUM(quantity) 
                    FROM order_items 
                    WHERE order_id = o.id
                ) AS total_items

            FROM addd_orders o

            JOIN address a ON o.address_id = a.id
            JOIN services s ON o.service_id = s.id

            WHERE o.delivery_boy_id = :boy_id
            AND o.status IN ('accepted', 'picked_up', 'ready', 'delivered_to_vendor', 'picked_from_vendor')

            ORDER BY o.id DESC
        """)

        return conn.execute(query, {"boy_id": boy_id}).fetchall()


    
def update_delivery_order_status(
    order_id,
    status
):

    with engine.connect() as conn:

        query = text("""

            UPDATE addd_orders

            SET status = :status

            WHERE id = :order_id

        """)

        conn.execute(query, {

            "status": status,
            "order_id": order_id

        })

        conn.commit()
    
def get_delivery_records(boy_id):

    with engine.connect() as conn:

        query = text("""
            SELECT 
                o.id,
                o.created_at,
                o.status,
                o.payment_method,
                o.payment_status,
                o.total_amount,

                a.user_name,
                a.phone_no,

                s.name AS service_name,

                (
                    SELECT SUM(quantity)
                    FROM order_items
                    WHERE order_id = o.id
                ) AS total_items

            FROM addd_orders o
            JOIN address a ON o.address_id = a.id
            JOIN services s ON o.service_id = s.id

            WHERE o.delivery_boy_id = :boy_id
            AND o.status = 'delivered'

            ORDER BY o.id DESC
        """)

        return conn.execute(query, {"boy_id": boy_id}).fetchall()
    
def get_delivery_boy_id(order_id):

    with engine.connect() as conn:

        query = text("""

            SELECT delivery_boy_id

            FROM addd_orders

            WHERE id = :order_id

        """)

        result = conn.execute(
            query,
            {"order_id": order_id}
        ).fetchone()

        return result.delivery_boy_id
    
def update_delivery_boy_busy_status(
    boy_id,
    busy
):

    with engine.connect() as conn:

        query = text("""

            UPDATE delivery_boys

            SET is_busy = :busy

            WHERE id = :boy_id

        """)

        conn.execute(query, {

            "busy": busy,
            "boy_id": boy_id

        })

        conn.commit()

def get_vendors2():

    with engine.connect() as conn:

        query = text("""
            SELECT 
                v.id,
                v.name,
                v.city,
                v.rating,

                GROUP_CONCAT(DISTINCT s.name) AS services

            FROM vendors v

            JOIN vendor_services vs
                ON v.id = vs.vendor_id

            JOIN item_types it
                ON vs.item_type_id = it.id
                     
            JOIN services s
                ON vs.service_id = s.id

            WHERE v.status = 'Active'

            GROUP BY v.id
            ORDER BY v.rating DESC
        """)

        return conn.execute(query).fetchall()
    

def get_user_orders(user_id):

    with engine.connect() as conn:

        query = text("""
            SELECT 
                o.id,
                o.status,
                o.total_amount,

                v.name AS vendor_name,
                s.name AS service_name

            FROM addd_orders o

            JOIN vendors v 
                ON o.vendor_id = v.id

            JOIN services s 
                ON o.service_id = s.id

            WHERE o.user_id = :user_id

            ORDER BY o.id DESC
        """)

        return conn.execute(query, {"user_id": user_id}).fetchall()
    
def get_order_details(order_id):

    with engine.connect() as conn:

        query = text("""
            SELECT 
                o.id,
                o.payment_method,
                o.payment_status,

                a.user_name,
                a.phone_no,
                a.city,
                a.state

            FROM addd_orders o

            JOIN address a 
                ON o.address_id = a.id

            WHERE o.id = :order_id
        """)

        return conn.execute(query, {"order_id": order_id}).fetchone()
    
# vendors_panel/incoming

def assign_vendor(order_id, vendor_id):
    with engine.connect() as conn:
        query = text("""
            UPDATE addd_orders
            SET vendor_id = :vendor_id
            WHERE id = :order_id
        """)
        conn.execute(query, {
            "vendor_id": vendor_id,
            "order_id": order_id
        })
        conn.commit()


def get_pending_orders(vendor_id):
    with engine.connect() as conn:
        query = text("""
            SELECT 
                o.id,
                o.user_id,
                s.name AS service_name,
                o.created_at,
                o.payment_status,
                o.total_amount
            FROM addd_orders o
            JOIN services s ON o.service_id = s.id
            WHERE o.status = 'pending'
            AND o.vendor_id = :vendor_id
            ORDER BY o.created_at DESC
        """)

        result = conn.execute(query, {"vendor_id": vendor_id})
        return result.fetchall()


def update_order_status(order_id, new_status):
    with engine.connect() as conn:
        query = text("""
            UPDATE addd_orders
            SET status = :status
            WHERE id = :order_id
        """)
        conn.execute(query, {
            "status": new_status,
            "order_id": order_id
        })
        conn.commit()

def get_dashboard_stats(vendor_id):
    with engine.connect() as conn:
        query = text("""
            SELECT
                SUM(CASE 
                    WHEN status = 'pending' 
                    AND DATE(created_at) = CURDATE() 
                    AND vendor_id = :vendor_id 
                    THEN 1 ELSE 0 END) AS new_today,

                SUM(CASE 
                    WHEN status = 'accepted' 
                    AND YEARWEEK(created_at, 1) = YEARWEEK(CURDATE(), 1)
                    AND vendor_id = :vendor_id 
                    THEN 1 ELSE 0 END) AS accepted,

                SUM(CASE 
                    WHEN status = 'rejected' 
                    AND YEARWEEK(created_at, 1) = YEARWEEK(CURDATE(), 1)
                    AND vendor_id = :vendor_id 
                    THEN 1 ELSE 0 END) AS rejected

            FROM addd_orders
        """)

        result = conn.execute(query, {"vendor_id": vendor_id}).fetchone()
        return result
    
# vendors_panel/processing

def get_active_orders(vendor_id):
    with engine.connect() as conn:
        query = text("""
            SELECT 
                o.id,
                o.user_id,
                s.name AS service_name,
                o.created_at,
                o.status
            FROM addd_orders o
            JOIN services s 
                ON o.service_id = s.id
            WHERE o.vendor_id = :vendor_id
            AND o.status IN ('accepted', 'processing', 'ready')
            ORDER BY o.created_at DESC
        """)

        result = conn.execute(query, {
            "vendor_id": vendor_id
        })

        return result.fetchall()
    
def get_active_orders_stats(vendor_id):

    with engine.connect() as conn:

        query = text("""

            SELECT

                SUM(CASE
                    WHEN status = 'accepted'
                    AND vendor_id = :vendor_id
                    THEN 1 ELSE 0
                END) AS accepted,

                SUM(CASE
                    WHEN status = 'processing'
                    AND vendor_id = :vendor_id
                    THEN 1 ELSE 0
                END) AS processing,

                SUM(CASE
                    WHEN status = 'ready'
                    AND vendor_id = :vendor_id
                    THEN 1 ELSE 0
                END) AS ready_count

            FROM addd_orders

        """)

        result = conn.execute(
            query,
            {"vendor_id": vendor_id}
        ).fetchone()

        return result

def update_active_order_status(order_id, status):
    with engine.connect() as conn:
        query = text("""
            UPDATE addd_orders
            SET status = :status
            WHERE id = :order_id
        """)

        conn.execute(query, {
            "status": status,
            "order_id": order_id
        })

        conn.commit()


# vendors/history

def get_history_orders(vendor_id):

    with engine.connect() as conn:

        query = text("""

            SELECT
                o.id,
                o.user_id,
                s.name AS service_name,
                o.created_at,
                o.status,
                o.total_amount

            FROM addd_orders o

            JOIN services s
                ON o.service_id = s.id

            WHERE o.vendor_id = :vendor_id

            AND o.status IN ('picked_up', 'delivered','rejected')

            ORDER BY o.created_at DESC

        """)

        result = conn.execute(
            query,
            {"vendor_id": vendor_id}
        ).fetchall()


        return result
    
def get_history_stats(vendor_id):
    with engine.connect() as conn:
        query = text("""
                    SELECT
                        SUM(CASE
                            WHEN status IN ('picked_up', 'delivered', 'rejected')
                            AND vendor_id = :vendor_id
                            THEN 1 ELSE 0
                        END) As total_orders,
                     
                        SUM(CASE
                            WHEN status = 'delivered'
                            AND vendor_id = :vendor_id
                            THEN 1 ELSE 0
                        END) As delivered,
                     
                        SUM(CASE 
                            WHEN status = 'rejected'
                            AND vendor_id = :vendor_id
                            THEN 1 ELSE 0
                            END) As rejected
                     
                    FROM addd_orders

                """)
        
        result = conn.execute(
            query,
            {"vendor_id" : vendor_id}
        ).fetchone()
        
    return result
    
# vendors/services

def add_vendor_service(
    vendor_id,
    service_name,
    price
):

    with engine.connect() as conn:

        # check if service exists

        query = text("""

            SELECT id
            FROM services
            WHERE name = :name

        """)

        service = conn.execute(
            query,
            {"name": service_name}
        ).fetchone()

        # create service if not exists

        if not service:

            insert_query = text("""

                INSERT INTO services(name)
                VALUES(:name)

            """)

            conn.execute(
                insert_query,
                {"name": service_name}
            )

            conn.commit()

            service = conn.execute(
                query,
                {"name": service_name}
            ).fetchone()

        service_id = service.id

        # insert vendor service

        vendor_query = text("""

            INSERT INTO vendor_services(
                vendor_id,
                service_id,
                price
            )

            VALUES(
                :vendor_id,
                :service_id,
                :price
            )

        """)

        conn.execute(vendor_query, {

            "vendor_id": vendor_id,
            "service_id": service_id,
            "price": price

        })

        conn.commit()

def get_vendor_services(vendor_id):

    with engine.connect() as conn:

        query = text("""

            SELECT

                MIN(vs.id) AS id,
                s.id AS service_id,
                s.name,
                MIN(vs.price) AS price

            FROM vendor_services vs

            JOIN services s
                ON vs.service_id = s.id

            WHERE vs.vendor_id = :vendor_id

            GROUP BY s.id, s.name

        """)

        result = conn.execute(
            query,
            {"vendor_id": vendor_id}
        ).fetchall()

        return result
    

def delete_vendor_service(service_id, vendor_id):

    with engine.connect() as conn:

        query = text("""

            DELETE FROM vendor_services

            WHERE id = :service_id
            AND vendor_id = :vendor_id

        """)

        conn.execute(query, {

            "service_id": service_id,
            "vendor_id": vendor_id

        })

        conn.commit()


# vendors/addresses

def save_vendor_address(
    vendor_id,
    street,
    city,
    state,
    pin,
    phone
):

    with engine.connect() as conn:

        query = text("""

            UPDATE vendors

            SET

                street_address = :street,
                city = :city,
                state = :state,
                pincode = :pin,
                phone = :phone

            WHERE id = :vendor_id

        """)

        conn.execute(query, {

            "street": street,
            "city": city,
            "state": state,
            "pin": pin,
            "phone": phone,
            "vendor_id": vendor_id

        })

        conn.commit()

def get_vendor_address(vendor_id):

    with engine.connect() as conn:

        query = text("""

            SELECT

                street_address,
                city,
                state,
                pincode,
                phone

            FROM vendors

            WHERE id = :vendor_id

        """)

        result = conn.execute(
            query,
            {"vendor_id": vendor_id}
        ).fetchone()

        return result
    
