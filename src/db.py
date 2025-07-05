import sqlite3
from datetime import datetime
import re
import bcrypt

DB_FILE = "pharmacy.db"

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

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
        unit_price REAL NOT NULL
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

# --- SUPPLIER & CUSTOMER MANAGEMENT ---

def add_supplier(name, contact, address):
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

def add_customer(name, contact, address):
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
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, strength, batch_no, expiry_date, quantity, unit_price FROM medicines ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [
        dict(zip(
            ["id", "name", "strength", "batch_no", "expiry_date", "quantity", "unit_price"],
            row
        )) for row in rows
    ]

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
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medicines WHERE id=?", (med_id,))
    conn.commit()
    conn.close()

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

# --- SALES & PURCHASES ---
def record_sale(medicine_id, quantity, customer_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM medicines WHERE id=?", (medicine_id,))
    row = cursor.fetchone()
    if not row or row[0] < quantity:
        conn.close()
        raise ValueError("Not enough stock for this sale.")
    cursor.execute("UPDATE medicines SET quantity=quantity-? WHERE id=?", (quantity, medicine_id))
    cursor.execute("""
        INSERT INTO sales (medicine_id, quantity, date, customer_id)
        VALUES (?, ?, ?, ?)
    """, (
        medicine_id, quantity, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), customer_id
    ))
    conn.commit()
    conn.close()

def record_purchase(medicine_id, quantity, supplier_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM medicines WHERE id=?", (medicine_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ValueError("Medicine does not exist.")
    cursor.execute("UPDATE medicines SET quantity=quantity+? WHERE id=?", (quantity, medicine_id))
    cursor.execute("""
        INSERT INTO purchases (medicine_id, quantity, date, supplier_id)
        VALUES (?, ?, ?, ?)
    """, (
        medicine_id, quantity, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), supplier_id
    ))
    conn.commit()
    conn.close()

def get_sales_history():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, m.name, s.quantity, s.date, c.name
        FROM sales s
        JOIN medicines m ON s.medicine_id = m.id
        LEFT JOIN customers c ON s.customer_id = c.id
        ORDER BY s.date DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [
        dict(zip(
            ["id", "medicine_name", "quantity", "date", "customer_name"],
            row
        )) for row in rows
    ]

def get_purchases_history():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, m.name, p.quantity, p.date, s.name
        FROM purchases p
        JOIN medicines m ON p.medicine_id = m.id
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        ORDER BY p.date DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [
        dict(zip(
            ["id", "medicine_name", "quantity", "date", "supplier_name"],
            row
        )) for row in rows
    ]

# --- EXPORT HELPERS ---
def get_inventory_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, strength, batch_no, expiry_date, quantity, unit_price FROM medicines")
    rows = cursor.fetchall()
    keys = ["name", "strength", "batch_no", "expiry_date", "quantity", "unit_price"]
    conn.close()
    return [dict(zip(keys, row)) for row in rows]

def get_sales_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, m.name, s.quantity, c.name, s.date
        FROM sales s
        JOIN medicines m ON s.medicine_id = m.id
        LEFT JOIN customers c ON s.customer_id = c.id
        ORDER BY s.date DESC
    """)
    keys = ["sale_id", "medicine", "quantity", "customer", "date"]
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(keys, row)) for row in rows]

def get_purchases_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, m.name, p.quantity, s.name, p.date
        FROM purchases p
        JOIN medicines m ON p.medicine_id = m.id
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        ORDER BY p.date DESC
    """)
    keys = ["purchase_id", "medicine", "quantity", "supplier", "date"]
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(keys, row)) for row in rows]