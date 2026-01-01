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

def add_order_to_db(order_data):

    user_id = session.get("user_id")

    if not user_id:
        return {"error": "User is not logged in, Please Go and Login"}
    
    phone = order_data["phone_no"]

    if len(phone) != 10:
        return {"error": "Phone Number Must of Ten Digits" }
    
    required_fields = {
    "user_name": "Please Enter Username",
    "phone_no": "Please Enter Phone Number",
    "pincode": "Please Enter pincode",
    "state": "Please Enter state",
    "city": "Please Enter city",
    "house_no": "Please Enter your house number",
    "service": "Service is required",
    "num_of_items": "Number of items is required"
}
    for fields, msg in required_fields.items():
        if not order_data.get(fields):
            return {"error":msg}
        
        order_data["user_id"] = user_id
        
    with engine.connect() as conn:
        query_address = text("""
            INSERT INTO address (user_name, phone_no, pincode, alternate_phone_no, state, city, house_no, user_id)
            VALUES (:user_name, :phone_no, :pincode, :alternate_phone_no, :state, :city, :house_no, :user_id)    
                """)
        
        conn.execute(query_address, order_data)

        query_order = text("""
            INSERT INTO orders (service, num_of_items, patment_method, suggesstions, user_id, delivery_date)
            VALUES (:service, :num_of_items, :patment_method, :suggesstions, :user_id, :delivery_date)    
                """)

        conn.execute(query_order, order_data)

        conn.commit()
        
        return {"success": True}
    
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

    