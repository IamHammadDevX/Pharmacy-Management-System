# Pharmacy Management System

A modern, secure, and user-friendly desktop application for managing pharmacy inventory, sales, and users.  
Built with **Python 3**, **PyQt5**, and **SQLite**.

---

## 🚀 Features

- **User Authentication:** Secure login with role-based access (Admin & Receptionist/User)
- **Password Security:** Passwords are hashed with bcrypt for safety
- **Inventory Management:** Add, edit, delete, and search medicines by name, batch, expiry, etc.
- **Sales & Purchases:** Record and view sales/purchase history with customer/supplier info
- **Low Stock & Expiry Alerts:** Dashboard cards show low stock and soon-to-expire medicines
- **Role-Based UI:** Receptionist has limited access; Admin sees all features
- **Modern UI:** Responsive, clean, and easy to use with sidebar/topbar/dashboard layout
- **Export Data:** Export inventory and sales data as CSV
- **Extendable:** Modular code for easy enhancements

---

## 🖥️ Screenshots

> _Add screenshots/gifs here for login, dashboard, and inventory screens!_

---

## 🛠️ Setup Instructions

### 1. **Clone the repo**

```bash
git clone https://github.com/YOUR-USERNAME/pharmacy-management-app.git
cd pharmacy-management-app
```

### 2. **Create a virtual environment and install dependencies**

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. **Initialize the Database**

On first run, the app creates the database and a default admin user:
- **Username:** `admin`
- **Password:** `admin123`

To add a receptionist/user:
```bash
python src/db.py
# Follow the prompts
```

### 4. **Run the App**

```bash
python src/main.py
```

---

## 👥 **User Roles**

- **Admin**
  - Full access: manage users, inventory, sales, purchases, export data
- **Receptionist/User**
  - Can view and sell medicines, but cannot add purchases or export inventory

---

## 🔒 **Security Notes**

- All passwords are securely hashed (bcrypt) in the database.
- Only admins should know the admin password.
- Each staff member should have their own user account for accountability.

---

## 📁 Project Structure

```
src/
  main.py
  db.py
  widgets/
    login_dialog.py
    topbar.py
    sidebar.py
    dashboard_card.py
    paginated_table.py
    add_medicine_dialog.py
  ui/
    main_window.py
    dashboard.py
  sale_purchase_dialog.py
pharmacy.db        # ← SQLite DB (auto-created)
requirements.txt
.gitignore
README.md
```

---

## 📋 **.gitignore**

Make sure you’re not pushing sensitive or environment files.  
Typical `.gitignore` for this project:

```
venv/
__pycache__/
*.pyc
*.db
*.sqlite3
*.csv
*.log
.idea/
.vscode/
.DS_Store
```

---

## 🚩 **Troubleshooting**

- **No receptionist/user in dropdown?**
  - Run `python src/db.py` to add a user.
- **Database locked or error?**
  - Make sure the app isn’t running in another window/process.
- **UI looks broken?**
  - Ensure all widget/UI files are in place and dependencies are installed.

---

## 🛡️ **Best Practices**

- Always run in a virtual environment.
- Never share or commit the SQLite DB with real data.
- Update passwords regularly.
- For production, consider adding audit logs and user management UI.

---

## 🙏 **Contributing**

Pull requests are welcome! Fork the repo, create a branch, and submit a PR.

---

## 📝 **License**

[MIT License](LICENSE)

---

## 📞 **Contact**

For issues, please open a [GitHub Issue](https://github.com/YOUR-USERNAME/pharmacy-management-app/issues) or contact the maintainer.
