Pharmacy Management System
A modern, secure, and user-friendly desktop application for managing pharmacy inventory, sales, and users.
Built with Python 3, PyQt5, and SQLite.

🚀 Features
User Authentication: Secure login with role-based access (Admin & Receptionist/User)

Password Security: Passwords are hashed with bcrypt for safety

Inventory Management: Add, edit, delete, and search medicines by name, batch, expiry, etc.

Sales & Purchases: Record and view sales/purchase history with customer/supplier info

Order Management: Create new medicine orders, track their status (Pending, Approved, Rejected), and update order statuses.

Sales Report: Generate detailed sales reports with date filtering, showing total orders, total quantity sold, and sales broken down by medicine.

User Settings: Allow logged-in users to change their password securely.

Help & Support: Provides an in-app help section with FAQs and contact information.

Low Stock & Expiry Alerts: Dashboard cards show low stock and soon-to-expire medicines

Role-Based UI: Receptionist has limited access; Admin sees all features

Modern UI: Responsive, clean, and easy to use with sidebar/topbar/dashboard layout

Export Data: Export inventory, general sales history, and detailed sales reports as CSV.

Optimized Performance: UI updates are batched for smoother table loading.

Extendable: Modular code for easy enhancements

🖥️ Screenshots
Add screenshots/gifs here for login, dashboard, inventory, orders, sales report, and settings screens!

🛠️ Setup Instructions
1. Clone the repo
git clone https://github.com/YOUR-USERNAME/pharmacy-management-app.git
cd pharmacy-management-app

2. Create a virtual environment and install dependencies
python -m venv venv
# On Windows
venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate

pip install -r requirements.txt

3. Initialize the Database
On first run, the app creates the database and a default admin user:

Username: admin

Password: Admin@123 (Note: Password is case-sensitive and includes special characters)

To add a receptionist/user (if not already present):

python src/db.py
# Follow the prompts (if any, or just run to ensure defaults are created)

4. Run the App
python src/main.py

👥 User Roles
Admin

Full access: manage users, inventory (add/edit/delete medicines), record sales/purchases, manage orders (add/approve/reject), view sales reports, export all data, and access settings.

Receptionist/User

Can view dashboard, record sales, view supplier & customer information, view invoices, and access help & support and personal settings. Cannot add purchases, manage inventory, manage orders, or export inventory/sales reports.

🔒 Security Notes
All passwords are securely hashed (bcrypt) in the database.

Only admins should know the admin password.

Each staff member should have their own user account for accountability.

The default admin password Admin@123 is for initial setup; it is highly recommended to change it after the first login.

📁 Project Structure
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
    supplier_customer_management.py # Added based on your sidebar
    invoice_dialog.py             # Added based on your sidebar
  ui/
    main_window.py
    dashboard.py
    medicine_management.py
    orders_dialog.py
    sales_dialog.py             # New: Sales Report Dialog
    help_support_dialog.py      # New: Help & Support Dialog
    settings_dialog.py          # New: Settings Dialog
    product_management.py       # Added based on your sidebar
    help_support.py             # Added based on your sidebar
  sale_purchase_dialog.py
pharmacy.db                 # ← SQLite DB (auto-created)
requirements.txt
.gitignore
README.md

📋 .gitignore
Make sure you’re not pushing sensitive or environment files.
Typical .gitignore for this project:

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

🚩 Troubleshooting
No receptionist/user in dropdown?

Run python src/db.py to ensure default users are created or add new ones.

Database locked or error?

Make sure the app isn’t running in another window/process.

UI looks broken?

Ensure all widget/UI files are in place and dependencies are installed (pip install -r requirements.txt).

Password change fails?

Ensure your new password meets the strength requirements (8+ chars, upper, lower, digit, special char [@#$]).

🛡️ Best Practices
Always run in a virtual environment.

Never share or commit the SQLite DB with real data.

Update passwords regularly.

For production, consider adding audit logs and more robust user management UI.

🙏 Contributing
Pull requests are welcome! Fork the repo, create a branch, and submit a PR.

📝 License
MIT License

📞 Contact
For issues, please open a GitHub Issue or contact the maintainer.

test cases:
Here are some unique medicine data entries you can use to manually populate your stock:

1.  **Medicine Name:** "Neurofen Plus"
    * **Strength:** "200mg/12.8mg"
    * **Batch No:** "NFPL2025A"
    * **Expiry Date:** "2026-03-15"
    * **Quantity:** 75
    * **Unit Price:** 8.50

2.  **Medicine Name:** "Zyrtec Allergy"
    * **Strength:** "10mg"
    * **Batch No:** "ZYRTEC005B"
    * **Expiry Date:** "2027-08-01"
    * **Quantity:** 120
    * **Unit Price:** 12.25

3.  **Medicine Name:** "Omeprazole"
    * **Strength:** "20mg"
    * **Batch No:** "OMPZ2024C"
    * **Expiry Date:** "2025-11-30"
    * **Quantity:** 90
    * **Unit Price:** 5.75

4.  **Medicine Name:** "Amoxicillin"
    * **Strength:** "500mg"
    * **Batch No:** "AMOX500X7"
    * **Expiry Date:** "2026-06-20"
    * **Quantity:** 60
    * **Unit Price:** 10.00

5.  **Medicine Name:** "Ventolin Inhaler"
    * **Strength:** "100mcg/puff"
    * **Batch No:** "VENTIL99D"
    * **Expiry Date:** "2027-02-28"
    * **Quantity:** 40
    * **Unit Price:** 18.99

6.  **Medicine Name:** "Lisinopril"
    * **Strength:** "10mg"
    * **Batch No:** "LISNPRL01E"
    * **Expiry Date:** "2025-09-10"
    * **Quantity:** 150
    * **Unit Price:** 7.15

7.  **Medicine Name:** "Metformin"
    * **Strength:** "850mg"
    * **Batch No:** "METFM850F"
    * **Expiry Date:** "2026-12-05"
    * **Quantity:** 100
    * **Unit Price:** 6.90

Remember to enter these details carefully into your medicine management section!