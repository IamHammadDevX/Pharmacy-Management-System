import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import sqlite3
from datetime import datetime
import re
import bcrypt
from PyQt5.QtCore import QObject, pyqtSignal
import os
import sys
import shutil

class DBSignals(QObject):
    medicine_updated = pyqtSignal()
    sale_recorded = pyqtSignal()
    order_updated = pyqtSignal()

db_signals = DBSignals()

# --- Get a Writable Database Path ---
def get_writable_db_path():
    """
    Determines the correct writable path for the database:
    - Dev mode: Uses pharmacy.db from project root (one level above src/).
    - Packaged .exe: Copies pharmacy.db to PUBLIC\PharmacyData if not already present.
    """
    if getattr(sys, 'frozen', False):
        # --- Running in PyInstaller packaged app ---
        try:
            public_dir = os.path.join(os.environ.get('PUBLIC', r'C:/Users/Public'), 'PharmacyData')
            if not os.path.exists(public_dir):
                os.makedirs(public_dir, exist_ok=True)

            db_path = os.path.join(public_dir, 'pharmacy.db')

            if not os.path.exists(db_path):
                # Copy bundled DB from the app directory
                bundled_db = os.path.join(sys._MEIPASS, 'pharmacy.db')
                if os.path.exists(bundled_db):
                    shutil.copy2(bundled_db, db_path)
                else:
                    print(f"⚠️ Warning: Bundled DB not found at {bundled_db}")

            return db_path
        except Exception as e:
            print(f"❌ Error setting up writable DB: {e}")
            raise
    else:
        # --- Running in development mode ---
        project_root_db = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pharmacy.db")
        if not os.path.exists(project_root_db):
            print(f"⚠️ Warning: Development DB not found at {project_root_db}")
        return project_root_db

# Global DB file path
DB_FILE = get_writable_db_path()

def get_connection():
    """Returns a SQLite connection with dictionary-like row access."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# --- Password Policy Utils ---

def is_strong_admin_password(password):
    """Admin password must be 8+ chars, with uppercase, lowercase, digit, special char."""
    return (
        len(password) >= 8 and
        re.search(r'[A-Z]', password) and
        re.search(r'[a-z]', password) and
        re.search(r'\d', password) and
        re.search(r'[@#$]', password)
    )

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

# --- DB Initialization ---

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # --- Medicines Table ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        strength TEXT,
        batch_no TEXT,
        expiry_date TEXT,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        last_updated TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # --- Archived Medicines Table ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS archived_medicines (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        strength TEXT,
        batch_no TEXT,
        expiry_date TEXT,
        quantity INTEGER DEFAULT 0,
        unit_price REAL,
        last_updated TEXT,
        archive_date TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # --- Suppliers Table ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact TEXT,
        address TEXT
    )
    """)

    # --- Customers Table ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact TEXT,
        address TEXT
    )
    """)

    # --- Sales Table ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        date TEXT NOT NULL,
        customer_id INTEGER,
        FOREIGN KEY (medicine_id) REFERENCES medicines(id),
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    """)

    # --- Purchases Table ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        date TEXT NOT NULL,
        supplier_id INTEGER,
        FOREIGN KEY (medicine_id) REFERENCES medicines(id),
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
    )
    """)

    # --- Users Table ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT,
        email TEXT
    )
    """)
    
    # --- Orders Table ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_name TEXT NOT NULL,
        quantity_ordered INTEGER NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('Pending', 'Approved', 'Rejected')),
        order_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Add default users if no users exist
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Add default admin
        admin_pw = hash_password("Admin@123")
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, full_name, email) 
            VALUES (?, ?, ?, ?, ?)
        """, ("admin", admin_pw, "admin", "Admin", "admin@pharmacy.local"))
        
        # Add default receptionist
        recep_pw = hash_password("user123")
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, full_name, email) 
            VALUES (?, ?, ?, ?, ?)
        """, ("recept1", recep_pw, "user", "Receptionist One", "recept1@pharmacy.local"))
    
    # Add sample orders if none exist
    cursor.execute("SELECT COUNT(*) FROM orders")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO orders (medicine_name, quantity_ordered, status, order_date) VALUES
            ('Aspirin', 50, 'Pending', '2025-07-07 12:00:00'),
            ('Paracetamol', 30, 'Approved', '2025-07-06 14:00:00'),
            ('Ibuprofen', 40, 'Rejected', '2025-07-05 09:00:00')
        """)
    
    conn.commit()
    conn.close()

def reset_users_table():
    """Drops and recreates the users table with default admin and receptionist"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT,
        email TEXT
    )
    """)
    
    # Add default admin
    admin_pw = hash_password("Admin@123")
    cursor.execute("""
        INSERT INTO users (username, password_hash, role, full_name, email) 
        VALUES (?, ?, ?, ?, ?)
    """, ("admin", admin_pw, "admin", "Admin", "admin@pharmacy.local"))
    
    # Add default receptionist
    recep_pw = hash_password("user123")
    cursor.execute("""
        INSERT INTO users (username, password_hash, role, full_name, email) 
        VALUES (?, ?, ?, ?, ?)
    """, ("recept1", recep_pw, "user", "Receptionist One", "recept1@pharmacy.local"))
    
    conn.commit()
    conn.close()

def get_user_list():
    """Returns list of all users with username, full_name, and role"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username, full_name, role 
        FROM users 
        ORDER BY role, username
    """)
    users = cursor.fetchall()
    conn.close()
    return users

def validate_login(username, password):
    """Validates user credentials and returns user data if successful"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, password_hash, role, full_name, email 
        FROM users 
        WHERE username=?
    """, (username,))
    row = cursor.fetchone()
    conn.close()
    
    if row and check_password(password, row[1]):
        return {
            "id": row[0], 
            "username": username, 
            "role": row[2], 
            "full_name": row[3], 
            "email": row[4]
        }
    return None

def add_admin(username, password, full_name, email):
    if not is_strong_admin_password(password):
        raise ValueError("Admin password must be 8+ chars, include upper, lower, digit, and special char [@#$].")
    hash_pw = hash_password(password)
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, role, full_name, email) VALUES (?, ?, ?, ?, ?)",
            (username, hash_pw, "admin", full_name, email)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError("Username already exists")
    finally:
        conn.close()

def add_receptionist(username, _password_ignore, full_name, email):
    shared_pw = "user123"
    hash_pw = hash_password(shared_pw)
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, role, full_name, email) VALUES (?, ?, ?, ?, ?)",
            (username, hash_pw, "user", full_name, email)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError("Username already exists")
    finally:
        conn.close()
def update_user_password(user_id, new_password):
    """
    Updates a user's password in the database.
    The new password will be hashed before storing.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        hashed_password = hash_password(new_password) # Use your existing hash_password function
        
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed_password, user_id))
        conn.commit()
        if cursor.rowcount == 0:
            raise ValueError(f"User with ID {user_id} not found.")
    except sqlite3.Error as e:
        conn.rollback()
        raise Exception(f"Database error updating password: {str(e)}")
    finally:
        conn.close()

# --- SUPPLIER & CUSTOMER MANAGEMENT ---

def add_supplier(name, contact, address=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO suppliers (name, contact, address) VALUES (?, ?, ?)",
        (name, contact, address)
    )
    conn.commit()
    conn.close()

def get_suppliers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, contact, address FROM suppliers ORDER BY name")
    suppliers = cursor.fetchall()
    conn.close()
    return suppliers

def update_supplier(supplier_id, name, contact, address):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE suppliers SET name=?, contact=?, address=? WHERE id=?",
        (name, contact, address, supplier_id)
    )
    conn.commit()
    conn.close()

def delete_supplier(supplier_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM suppliers WHERE id=?", (supplier_id,))
    conn.commit()
    conn.close()
    db_signals.medicine_updated.emit() # Assuming this signal is relevant for supplier changes as well

def add_customer(name, contact, address=""):  # Make address optional
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO customers (name, contact, address) VALUES (?, ?, ?)",
        (name, contact, address)
    )
    conn.commit()
    conn.close()

def get_customers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, contact, address FROM customers ORDER BY name")
    customers = cursor.fetchall()
    conn.close()
    return customers

def update_customer(customer_id, name, contact, address):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE customers SET name=?, contact=?, address=? WHERE id=?",
        (name, contact, address, customer_id)
    )
    conn.commit()
    conn.close()

def delete_customer(customer_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers WHERE id=?", (customer_id,))
    conn.commit()
    conn.close()

# --- MEDICINE MANAGEMENT ---
def get_all_medicines():
    """Returns only in-stock medicines (quantity > 0)"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, strength, batch_no, expiry_date, quantity, unit_price 
            FROM medicines 
            WHERE quantity > 0
            ORDER BY name
        """)
        rows = cursor.fetchall()
        # Rows are already sqlite3.Row objects (dictionary-like) due to get_connection()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def add_medicine(med):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO medicines (name, strength, batch_no, expiry_date, quantity, unit_price)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        med["name"], med["strength"], med["batch_no"], med["expiry_date"], med["quantity"], med["unit_price"]
    ))
    conn.commit()
    conn.close()
    
def update_medicine(med_id, med):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE medicines SET
            name=?,
            strength=?,
            batch_no=?,
            expiry_date=?,
            quantity=?,
            unit_price=?
        WHERE id=?
    """, (
        med["name"], med["strength"], med["batch_no"], med["expiry_date"],
        med["quantity"], med["unit_price"], med_id
    ))
    conn.commit()
    conn.close()

def delete_medicine(med_id):
    """Delete a medicine by ID from the database"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM medicines WHERE id = ?", (med_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise ValueError("No medicine found with the given ID.")
    except sqlite3.Error as e:
        raise Exception(f"Database error: {str(e)}")
    finally:
        conn.close()
        db_signals.medicine_updated.emit()  # Signal update after deletion

def batch_number_exists(name, batch_no, exclude_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    if exclude_id:
        cursor.execute(
            "SELECT 1 FROM medicines WHERE name=? AND batch_no=? AND id!=? LIMIT 1",
            (name, batch_no, exclude_id)
        )
    else:
        cursor.execute(
            "SELECT 1 FROM medicines WHERE name=? AND batch_no=? LIMIT 1",
            (name, batch_no)
        )
    result = cursor.fetchone()
    conn.close()
    return bool(result)

def check_and_remove_zero_stock():
    """Remove medicines with zero quantity from database"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Get all medicines with zero quantity
        cursor.execute("SELECT id, name FROM medicines WHERE quantity <= 0")
        zero_stock_meds = cursor.fetchall()
        
        if zero_stock_meds:
            # Archive before deleting
            # Ensure the order of columns matches the INSERT statement
            cursor.executemany("""
                INSERT INTO archived_medicines 
                (id, name, strength, batch_no, expiry_date, quantity, unit_price, last_updated)
                SELECT id, name, strength, batch_no, expiry_date, quantity, unit_price, last_updated
                FROM medicines WHERE id = ?
            """, [(med["id"],) for med in zero_stock_meds]) # Access by key due to row_factory
            
            # Delete from medicines table
            cursor.executemany("DELETE FROM medicines WHERE id = ?", 
                             [(med["id"],) for med in zero_stock_meds]) # Access by key
            
            conn.commit()
            return True, f"Removed {len(zero_stock_meds)} out-of-stock medicines"
        return False, "No out-of-stock medicines found"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def update_medicine_quantity(medicine_id, quantity_change):
    """Update medicine quantity and remove if reaches 0"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Update quantity
        cursor.execute("UPDATE medicines SET quantity = quantity + ? WHERE id = ?", 
                      (quantity_change, medicine_id))
        
        # Check if quantity is now <= 0
        cursor.execute("""
            SELECT id, name, strength, batch_no, expiry_date, quantity, unit_price 
            FROM medicines WHERE id = ?
        """, (medicine_id,))
        med_data = cursor.fetchone() # This is now a sqlite3.Row object
        
        if med_data and med_data["quantity"] <= 0:  # Access by key
            # Archive before deleting
            cursor.execute("""
                INSERT INTO archived_medicines 
                (id, name, strength, batch_no, expiry_date, quantity, unit_price, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (med_data["id"], med_data["name"], med_data["strength"], med_data["batch_no"],
                  med_data["expiry_date"], med_data["quantity"], med_data["unit_price"]))
            
            cursor.execute("DELETE FROM medicines WHERE id = ?", (medicine_id,))
            message = f"Medicine '{med_data['name']}' removed due to zero stock"
            db_signals.medicine_updated.emit()
        else:
            message = f"Quantity updated for medicine ID {medicine_id}"
        
        conn.commit()
        return True, message
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

# --- SALES & PURCHASES ---
def record_sale(medicine_id, quantity, customer_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT quantity FROM medicines WHERE id=?", (medicine_id,))
        row = cursor.fetchone()
        if not row or row["quantity"] < quantity: # Access by key
            raise ValueError("Not enough stock for this sale.")
        
        # Update quantity (will auto-remove if reaches 0)
        success, message = update_medicine_quantity(medicine_id, -quantity)
        if not success:
            raise ValueError(message)
        
        cursor.execute("""
            INSERT INTO sales (medicine_id, quantity, date, customer_id)
            VALUES (?, ?, ?, ?)
        """, (
            medicine_id, quantity, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), customer_id
        ))
        conn.commit()
        db_signals.sale_recorded.emit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def record_purchase(medicine_id, quantity, supplier_id=None): # Removed unit_price as it's not in your sales table
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM medicines WHERE id=?", (medicine_id,))
        if not cursor.fetchone():
            raise ValueError("Medicine does not exist.")
        
        # Update quantity (will auto-remove if reaches 0)
        success, message = update_medicine_quantity(medicine_id, quantity)
        if not success:
            raise ValueError(message)
        
        cursor.execute("""
            INSERT INTO purchases (medicine_id, quantity, date, supplier_id)
            VALUES (?, ?, ?, ?)
        """, (
            medicine_id, quantity, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), supplier_id
        ))
        conn.commit()
        db_signals.medicine_updated.emit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_sales_history():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, m.name AS medicine_name, s.quantity, s.date, c.name AS customer_name
        FROM sales s
        JOIN medicines m ON s.medicine_id = m.id
        LEFT JOIN customers c ON s.customer_id = c.id
        ORDER BY s.date DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_purchases_history():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, m.name AS medicine_name, p.quantity, p.date, s.name AS supplier_name
        FROM purchases p
        JOIN medicines m ON p.medicine_id = m.id
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        ORDER BY p.date DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# --- EXPORT HELPERS ---
def get_inventory_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, strength, batch_no, expiry_date, quantity, unit_price 
        FROM medicines 
        WHERE quantity > 0
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_sales_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id AS sale_id, m.name AS medicine, s.quantity, c.name AS customer, s.date
        FROM sales s
        JOIN medicines m ON s.medicine_id = m.id
        LEFT JOIN customers c ON s.customer_id = c.id
        ORDER BY s.date DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_purchases_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id AS purchase_id, m.name AS medicine, p.quantity, s.name AS supplier, p.date
        FROM purchases p
        JOIN medicines m ON p.medicine_id = m.id
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        ORDER BY p.date DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_archived_medicines():
    """Get list of all archived medicines"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, strength, batch_no, expiry_date, quantity, unit_price, archive_date
        FROM archived_medicines
        ORDER BY archive_date DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def record_sale_with_stock_update(medicine_id, quantity, customer_id=None):
    """Atomically records sale and updates stock"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # First verify stock
        cursor.execute("SELECT quantity FROM medicines WHERE id=?", (medicine_id,))
        row = cursor.fetchone()
        if not row or row["quantity"] < quantity: # Access by key
            return False, "Not enough stock for this sale"
        
        # Update stock
        cursor.execute("UPDATE medicines SET quantity=quantity-? WHERE id=?", 
                      (quantity, medicine_id))
        
        # Record sale
        cursor.execute("""
            INSERT INTO sales (medicine_id, quantity, date, customer_id)
            VALUES (?, ?, datetime('now'), ?)
        """, (medicine_id, quantity, customer_id))
        
        conn.commit()
        return True, "Sale recorded successfully"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def record_purchase_with_stock_update(medicine_id, quantity, unit_price, supplier_id=None):
    """Atomically records purchase and updates stock"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Update stock
        cursor.execute("UPDATE medicines SET quantity=quantity+?, unit_price=? WHERE id=?", 
                      (quantity, unit_price, medicine_id))
        
        # Record purchase
        cursor.execute("""
            INSERT INTO purchases (medicine_id, quantity, date, supplier_id)
            VALUES (?, ?, datetime('now'), ?)
        """, (medicine_id, quantity, supplier_id))
        
        conn.commit()
        return True, "Purchase recorded successfully"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

# --- ORDER MANAGEMENT ---
def get_all_orders():
    """Retrieve all orders from the database"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, medicine_name, quantity_ordered, status, order_date FROM orders")
        orders = [dict(row) for row in cursor.fetchall()] # Convert to dicts
        return orders
    except sqlite3.Error as e:
        raise Exception(f"Database error: {str(e)}")
    finally:
        conn.close()

def insert_order(medicine_name, quantity_ordered):
    """Insert a new order into the database"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (medicine_name, quantity_ordered, status, order_date)
            VALUES (?, ?, ?, ?)
        """, (medicine_name, quantity_ordered, "Pending", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        conn.rollback()
        raise Exception(f"Database error: {str(e)}")
    finally:
        conn.close()
        db_signals.order_updated.emit()

def update_order_status(order_id, status):
    """Update the status of an order"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        conn.commit()
        if cursor.rowcount == 0:
            raise ValueError("No order found with the given ID.")
    except sqlite3.Error as e:
        raise Exception(f"Database error: {str(e)}")
    finally:
        conn.close()
        db_signals.order_updated.emit()

# --- NEW: SALES REPORT FUNCTION ---
def get_sales_report_data(start_date=None, end_date=None):
    """
    Retrieves sales report data from the database, aggregating by medicine.
    Only considers 'Approved' orders.
    Optionally filters by order date.

    Args:
        start_date (str, optional): Start date in 'YYYY-MM-DD' format.
        end_date (str, optional): End date in 'YYYY-MM-DD' format.

    Returns:
        tuple: A tuple containing:
            - summary_data (dict): {'total_orders': int, 'total_quantity_sold': int}
            - sales_by_medicine_list (list): [{'medicine_name': str, 'total_quantity_sold': int, 'num_orders': int}, ...]
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Build the WHERE clause for date filtering
        date_filter_sql = ""
        params = []
        if start_date:
            date_filter_sql += " AND date >= ?" # Using 'date' column from sales table
            params.append(start_date + " 00:00:00") # Include start of day
        if end_date:
            date_filter_sql += " AND date <= ?"   # Using 'date' column from sales table
            params.append(end_date + " 23:59:59") # Include end of day

        # Query for sales by medicine
        # Joining with medicines table to get medicine_name
        cursor.execute(f"""
            SELECT
                m.name AS medicine_name,
                SUM(s.quantity) AS total_quantity_sold,
                COUNT(s.id) AS num_orders
            FROM
                sales s
            JOIN
                medicines m ON s.medicine_id = m.id
            WHERE
                1=1 {date_filter_sql} -- 1=1 is a trick to easily append AND clauses
            GROUP BY
                m.name
            ORDER BY
                total_quantity_sold DESC
        """, params)
        sales_by_medicine = [
            {
                "medicine_name": row["medicine_name"],
                "total_quantity_sold": row["total_quantity_sold"],
                "num_orders": row["num_orders"]
            } for row in cursor.fetchall()
        ]

        # Query for overall summary
        cursor.execute(f"""
            SELECT
                COUNT(id) AS total_orders,
                SUM(quantity) AS total_quantity_sold
            FROM
                sales
            WHERE
                1=1 {date_filter_sql}
        """, params)
        summary_row = cursor.fetchone()
        summary_data = {
            "total_orders": summary_row["total_orders"] if summary_row and summary_row["total_orders"] is not None else 0,
            "total_quantity_sold": summary_row["total_quantity_sold"] if summary_row and summary_row["total_quantity_sold"] is not None else 0
        }

        return summary_data, sales_by_medicine

    except sqlite3.Error as e:
        raise Exception(f"Database error fetching sales report: {str(e)}")
    finally:
        if conn:
            conn.close()
