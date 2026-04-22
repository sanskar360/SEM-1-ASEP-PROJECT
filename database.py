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
    
def delete_address_from_db(address_id, user_id):
    with engine.connect() as conn:
        query = text("""
            DELETE FROM address 
            WHERE id = :id AND user_id = :user_id
        """)
        conn.execute(query, {"id": address_id, "user_id": user_id})
        conn.commit()

    return {"success": True}

from sqlalchemy import text
from flask import session

def add_order_to_db(order_data):

    user_id = session.get("user_id")

    if not user_id:
        return {"error": "User not logged in"}

    # 🔹 VALIDATION
    if not order_data.get("service"):
        return {"error": "Service is required"}

    if not order_data.get("num_of_items"):
        return {"error": "Number of items is required"}

    # 🔹 INSERT INTO ORDERS
    try:
        with engine.connect() as conn:

            query = text("""
                INSERT INTO orders 
                (service, num_of_items, patment_method, suggesstions, user_id, delivery_date)
                VALUES 
                (:service, :num_of_items, :patment_method, :suggesstions, :user_id, :delivery_date)
            """)

            data = {
                "service": order_data.get("service"),
                "num_of_items": order_data.get("num_of_items"),
                "patment_method": order_data.get("patment_method"),
                "suggesstions": order_data.get("suggesstions"),
                "delivery_date": order_data.get("delivery_date"),
                "user_id": user_id
            }

            conn.execute(query, data)
            conn.commit()

        return {"success": True}

    except Exception as e:
        return {"error": str(e)}