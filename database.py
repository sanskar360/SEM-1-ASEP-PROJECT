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
            SELECT DISTINCT v.*
            FROM vendors v
            JOIN vendor_services vs ON v.id = vs.vendor_id
            WHERE vs.service_id = :service_id
            AND v.city = :city
            ORDER BY 
                CASE 
                    WHEN v.pincode = :pincode THEN 1
                    ELSE 2
                END
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
def insert_order(vendor_id, service_id, address_id, total):

    with engine.connect() as conn:

        query = text("""
            INSERT INTO addd_orders (vendor_id, service_id, address_id, total_amount)
            VALUES (:vendor_id, :service_id, :address_id, :total)
        """)

        result = conn.execute(query, {
            "vendor_id": vendor_id,
            "service_id": service_id,
            "address_id": address_id,
            "total": total
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