Vega Vastra – Smart Laundry Management System
Vega Vastra is a Smart Laundry Management System designed to simplify and digitize the complete laundry process.
The platform connects customers, vendors, and delivery boys in a single system for efficient order management, tracking,
and delivery operations.
The project focuses on creating a smooth laundry booking experience with real-time order handling, vendor management,
delivery tracking, and payment integration.

Features
Customer Features
User registration and login
Service selection
Vendor selection
Order placement
Order tracking
Address management
Payment support
Order history
Vendor Features
Vendor dashboard
Accept/reject orders
Service management
Price management
Order status updates
Delivery Boy Features
Assigned orders management
Pickup and delivery tracking
Busy/available status system
Payment collection support


//  Technologies Used  //

1. Frontend
   HTML
   CSS
   JavaScript
   
3. Backend
  Python
  Flask

4. Database
  MySQL
  SQLAlchemy

5. Deployment
  Render
  Aiven Cloud Database


Order Flow

Customer selects laundry service
           |
Customer selects address
           |
Customer chooses vendor
           |
Order is placed
           |
Vendor accepts order
           |
Delivery boy gets assigned
           |
Pickup and delivery process starts
           |           
Payment completed
           |
Order delivered successfully


Installation

Clone Repository
git clone https://github.com/your-username/your-repository-name.git
Move into Project Folder
cd your-project-folder
Install Dependencies
pip install -r requirements.txt
Run Application
python app.py


Project Structure

project/
│
├── static/
│   ├── icons/
│   ├── About Us.png
│   ├── admin_style.css
│   ├── booking.css
│   ├── delivery_style.css
│   ├── how_it_works.css
│   ├── image3.jpg
│   ├── Logo.png
│   ├── navbar.css
│   ├── script.js
│   ├── style.css
│   ├── track_orders.css
│   └── vendor_dashboard.css
│
├── templates/
│   ├── add_orders.html
│   ├── admin_delivery_boys.html
│   ├── admin_orders_table.html
│   ├── admin_payments.html
│   ├── admin_users_table.html
│   ├── admin_vendors.html
│   ├── containers.html
│   ├── delivery_assigned.html
│   ├── delivery_history.html
│   ├── delivery_login.html
│   ├── delivery_profile.html
│   ├── home.html
│   ├── how_it_works.html
│   ├── login.html
│   ├── manage_addresses.html
│   ├── nav.html
│   ├── payments.html
│   ├── profile.html
│   ├── select_address.html
│   ├── services.html
│   ├── sign_up.html
│   ├── track_orders.html
│   ├── vendors_address.html
│   ├── vendors_history.html
│   ├── vendors_incoming.html
│   ├── vendors_processing.html
│   ├── vendors_services.html
│   └── vendors.html
│
├── app.py
├── database.py
├── ca1.pem
└── README.md
Future Improvements
AI-based load prediction
GPS delivery tracking
RFID locker integration
Route optimization system
Responsive mobile UI
Notification system
Online payment gateway
Analytics dashboard


Developer

Developed by Sanskar Bhilavade and Sanskar Hedau


License

This project is developed for educational and learning purposes.
