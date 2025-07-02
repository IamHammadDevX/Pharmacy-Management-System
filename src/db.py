import sqlite3
from datetime import datetime

DB_FILE = "pharmacy.db"

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

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
    # --- Sales Table ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        date TEXT NOT NULL,
        customer_name TEXT,
        FOREIGN KEY (medicine_id) REFERENCES medicines(id)
    )
    """)
    # --- Purchases Table ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        date TEXT NOT NULL,
        supplier_name TEXT,
        FOREIGN KEY (medicine_id) REFERENCES medicines(id)
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
    # Add default admin if no users
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        import bcrypt
        pw_hash = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode()
        cursor.execute("INSERT INTO users (username, password_hash, role, full_name, email) VALUES (?, ?, ?, ?, ?)",
            ("admin", pw_hash, "admin", "Admin", "admin@pharmacy.local"))
    conn.commit()
    conn.close()

def get_user_list():
    conn = get_connection()
    cursor = conn.cursor()
    # Returns tuples: (username, full_name, role)
    cursor.execute("SELECT username, full_name, role FROM users ORDER BY role, username")
    users = cursor.fetchall()
    conn.close()
    return users

def validate_login(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash, role, full_name, email FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        import bcrypt
        if bcrypt.checkpw(password.encode(), row[1].encode()):
            return {"id": row[0], "username": username, "role": row[2], "full_name": row[3], "email": row[4]}
    return None

def add_receptionist(username, password, full_name, email):
    import bcrypt
    hash_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
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

def record_sale(medicine_id, quantity, customer_name=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM medicines WHERE id=?", (medicine_id,))
    row = cursor.fetchone()
    if not row or row[0] < quantity:
        conn.close()
        raise ValueError("Not enough stock for this sale.")
    # Update stock
    cursor.execute("UPDATE medicines SET quantity=quantity-? WHERE id=?", (quantity, medicine_id))
    # Insert sale record
    cursor.execute("""
        INSERT INTO sales (medicine_id, quantity, date, customer_name)
        VALUES (?, ?, ?, ?)
    """, (
        medicine_id, quantity, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), customer_name
    ))
    conn.commit()
    conn.close()

def record_purchase(medicine_id, quantity, supplier_name=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM medicines WHERE id=?", (medicine_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ValueError("Medicine does not exist.")
    # Update stock
    cursor.execute("UPDATE medicines SET quantity=quantity+? WHERE id=?", (quantity, medicine_id))
    # Insert purchase record
    cursor.execute("""
        INSERT INTO purchases (medicine_id, quantity, date, supplier_name)
        VALUES (?, ?, ?, ?)
    """, (
        medicine_id, quantity, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), supplier_name
    ))
    conn.commit()
    conn.close()

def get_sales_history():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, m.name, s.quantity, s.date, s.customer_name
        FROM sales s
        JOIN medicines m ON s.medicine_id = m.id
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
        SELECT p.id, m.name, p.quantity, p.date, p.supplier_name
        FROM purchases p
        JOIN medicines m ON p.medicine_id = m.id
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
        SELECT s.id, m.name, s.quantity, s.customer_name, s.date
        FROM sales s
        JOIN medicines m ON s.medicine_id = m.id
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
        SELECT p.id, m.name, p.quantity, p.supplier_name, p.date
        FROM purchases p
        JOIN medicines m ON p.medicine_id = m.id
        ORDER BY p.date DESC
    """)
    keys = ["purchase_id", "medicine", "quantity", "supplier", "date"]
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(keys, row)) for row in rows]

# Script to add a receptionist from command line for easy testing
if __name__ == "__main__":
    init_db()
    print("Add Receptionist User (for testing)")
    username = input("Username: ")
    import getpass
    password = getpass.getpass("Password: ")
    full_name = input("Full Name: ")
    email = input("Email: ")
    try:
        add_receptionist(username, password, full_name, email)
        print("Receptionist added.")
    except Exception as e:
        print("Failed to add:", e)