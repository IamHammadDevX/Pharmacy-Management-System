# Pharmacy Management System

A modern full-featured Pharmacy Management System built in Python with PyQt5.

---

## 🚀 Features

- **Medicine/Product Inventory:** Add, edit, delete, and search medicines with all details (batch, expiry, price, stock).
- **Fast Search:** Instantly filter/search from tens of thousands of medicines.
- **Expiry & Low Stock Alerts:** Automatic warnings for expiring/expired and low stock items.
- **Paginated Data Tables:** For smooth browsing of large datasets.
- **Sales (POS):** 
  - Per-product and per-line discount.
  - Prevents selling expired medicines.
  - Customer management (walk-in/existing/new).
  - Printable receipts (₨ Pakistani Rupee format).
- **Purchase:** 
  - Supplier management.
  - Records and updates stock, with expiry warning.
- **Admin Controls:** Only admins can manage products and inventory.
- **Export to CSV:** Export inventory for backup/analysis.
- **Modern UI:** Clean, responsive PyQt5 interface.

---

## 🖥️ Screenshots

*(Add screenshots here for Inventory, Sales, Purchase, Alerts, etc.)*

---

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/pharmacy-management-pyqt.git
cd pharmacy-management-pyqt
```

### 2. Set Up a Virtual Environment (Recommended)

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```
If `requirements.txt` is missing, install manually:
```bash
pip install PyQt5
```

### 4. Run the Application

If your project is in `src/` directory:
```bash
python src/main.py
```
Or if it's in root:
```bash
python main.py
```

### 5. First Use

- On first launch, create an admin user (if prompted).
- All management features require admin login.

---

## 🧑‍💻 Usage

- **Inventory Management:** Add/edit/delete medicines. Use the search bar for instant filtering.
- **Sales:** 
  - Search and select non-expired medicines.
  - Enter quantity and per-product discount.
  - Fill customer info (walk-in/existing/new).
  - Print receipt and record sale.
- **Purchase:** 
  - Add stock, record supplier info.
  - Warning if medicine is expired.
- **Alerts:** Click "Generate Alerts" for expiry and low stock warnings.
- **Export:** Click "Export Inventory" to back up to CSV.

---

## 📂 Project Structure

```
pharmacy-management-pyqt/
│
├── src/
│   ├── main.py
│   ├── db.py
│   ├── ...
│   ├── widgets/
│   │   ├── paginated_table.py
│   │   ├── add_medicine_dialog.py
│   │   └── ...
│   └── ...
├── requirements.txt
├── README.md
└── ...
```

---

## 💸 Currency

All prices are shown and printed with Pakistani Rupee symbol (₨).

---

## 🐞 Troubleshooting

- **App won't start:** Ensure all dependencies are installed and you are using Python 3.7+.
- **UI issues:** Try deleting `.pyc` files and re-running.
- **Database errors:** Ensure SQLite database file has write permissions. Delete and restart for a fresh DB (be careful—this erases all data).
- **Cannot manage products:** Only admin users have access.

---

## 📝 Customization

- **Change currency:** Update the symbol in receipt and table formatting in code.
- **Adjust alert thresholds:** Change expiry/stock numbers in relevant methods.
- **Change UI theme:** Edit stylesheet sections in the Python files.

---

## 🎓 License

MIT License

---

## 👤 Author

- [HAMMAD](https://github.com/iamhammad_devx)