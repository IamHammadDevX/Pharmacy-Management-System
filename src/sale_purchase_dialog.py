from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox,
    QHBoxLayout, QSpinBox, QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QComboBox
)
from PyQt5.QtCore import Qt
import db
import datetime

def is_expired(expiry_date_str):
    """Returns True if expiry_date_str (format YYYY-MM-DD) is before today."""
    try:
        return datetime.datetime.strptime(expiry_date_str, "%Y-%m-%d").date() < datetime.date.today()
    except Exception:
        return False

class SaleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Record New Sale")
        self.setMinimumSize(1000, 650)

        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f5f6fa, stop:1 #ffffff);
                border-radius: 12px;
            }
            QLabel {
                font-size: 16px;
                color: #34495e;
            }
            QLabel#header_label {
                font-size: 28px;
                font-weight: bold;
                color: white;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #43cea2, stop:1 #185a9d);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }
            QLineEdit, QSpinBox {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }
            QTableWidget {
                background: white;
                border-radius: 8px;
                border: 1px solid #ddd;
                font-size: 13px;
            }
            QTableWidget::item { padding: 6px; }
            QTableWidget::item:alternate { background: #f9f9f9; }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #43cea2, stop:1 #185a9d);
                color: white; font-weight: bold; padding: 8px; border: none;
                border-radius: 8px 8px 0 0;
            }
            QComboBox {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }
            QPushButton {
                border-radius: 8px;
                padding: 10px 20px;
                min-width: 120px;
                font-weight: bold;
                border: none;
                color: white;
                font-size: 15px;
                transition: background 0.3s ease;
            }
            QPushButton#record_sale_btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #28a745, stop:1 #218838);
            }
            QPushButton#record_sale_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #218838, stop:1 #28a745);
            }
            QPushButton#prev_btn, QPushButton#next_btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6c757d, stop:1 #5a6268);
            }
            QPushButton#prev_btn:hover, QPushButton#next_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5a6268, stop:1 #6c757d);
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header_label = QLabel("Record New Sale")
        header_label.setObjectName("header_label")
        main_layout.addWidget(header_label)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Fast Medicine Search
        self.medicine_search = QLineEdit()
        self.medicine_search.setPlaceholderText("Type to search medicine name, batch, etc...")
        self.medicine_search.textChanged.connect(self.fast_filter_medicine_table)
        form_layout.addRow("Medicine Search:", self.medicine_search)

        # Table of Medicines
        self.medicine_table = QTableWidget(0, 6)
        self.medicine_table.setHorizontalHeaderLabels([
            "Name", "Strength", "Batch", "Expiry", "Stock", "Unit Price"
        ])
        self.medicine_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.medicine_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.medicine_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.medicine_table.setMinimumHeight(170)
        form_layout.addRow(self.medicine_table)

        # Pagination Controls
        self.current_page = 0
        self.items_per_page = 100
        pagination_layout = QHBoxLayout()
        pagination_layout.addStretch()
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.setObjectName("prev_btn")
        self.prev_btn.setCursor(Qt.PointingHandCursor)
        self.prev_btn.clicked.connect(self.prev_page)
        pagination_layout.addWidget(self.prev_btn)
        self.page_label = QLabel("Page 1")
        pagination_layout.addWidget(self.page_label)
        self.next_btn = QPushButton("Next")
        self.next_btn.setObjectName("next_btn")
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.next_btn)
        pagination_layout.addStretch()
        form_layout.addRow(pagination_layout)

        # Quantity Input
        self.qty_spin = QSpinBox()
        self.qty_spin.setMinimum(1)
        self.qty_spin.setMaximum(9999)
        form_layout.addRow("Quantity:", self.qty_spin)

        main_layout.addLayout(form_layout)

        # Customer Selection
        self.customer_group = QVBoxLayout()
        self.setup_customer_fields()
        main_layout.addLayout(self.customer_group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.record_sale_btn = QPushButton("Record Sale")
        self.record_sale_btn.setObjectName("record_sale_btn")
        self.record_sale_btn.setCursor(Qt.PointingHandCursor)
        self.record_sale_btn.clicked.connect(self.save_sale)
        btn_layout.addWidget(self.record_sale_btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        self.medicines = []
        self.selected_medicine = None
        self.load_medicines()

    def setup_customer_fields(self):
        self.customer_group.addWidget(QLabel("Customer Information:"))
        
        self.cust_type_combo = QComboBox()
        self.cust_type_combo.addItem("Select Existing Customer", "existing")
        self.cust_type_combo.addItem("New Customer", "new")
        self.customer_group.addWidget(self.cust_type_combo)
        
        self.cust_combo = QComboBox()
        self.load_customers()
        self.customer_group.addWidget(self.cust_combo)
        
        self.new_cust_name = QLineEdit()
        self.new_cust_name.setPlaceholderText("Full Name")
        self.new_cust_name.setVisible(False)
        self.customer_group.addWidget(self.new_cust_name)
        
        self.new_cust_contact = QLineEdit()
        self.new_cust_contact.setPlaceholderText("Phone/Email")
        self.new_cust_contact.setVisible(False)
        self.customer_group.addWidget(self.new_cust_contact)
        
        self.new_cust_address = QLineEdit()
        self.new_cust_address.setPlaceholderText("Address (Optional)")
        self.new_cust_address.setVisible(False)
        self.customer_group.addWidget(self.new_cust_address)
        
        self.cust_type_combo.currentIndexChanged.connect(self.toggle_customer_fields)

    def load_medicines(self):
        self.medicines = db.get_all_medicines()
        self.fast_filter_medicine_table()

    def fast_filter_medicine_table(self):
        search = self.medicine_search.text().strip().lower()
        filtered_meds = []
        for med in self.medicines:
            # Don't show expired medicines in the sale dialog
            if is_expired(med.get("expiry_date", "2099-01-01")):
                continue
            display = (
                search in med['name'].lower() or
                search in str(med.get('strength', '')).lower() or
                search in str(med.get('batch_no', '')).lower() or
                search in str(med.get('expiry_date', '')).lower()
            ) if search else True
            if display:
                filtered_meds.append(med)
        
        # Calculate pagination
        total_items = len(filtered_meds)
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        self.current_page = min(self.current_page, max(0, total_pages - 1))
        start_idx = self.current_page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_items)
        
        # Update table with paginated items
        self.medicine_table.setRowCount(0)
        for med in filtered_meds[start_idx:end_idx]:
            row_pos = self.medicine_table.rowCount()
            self.medicine_table.insertRow(row_pos)
            self.medicine_table.setItem(row_pos, 0, QTableWidgetItem(med['name']))
            self.medicine_table.setItem(row_pos, 1, QTableWidgetItem(str(med.get('strength', ''))))
            self.medicine_table.setItem(row_pos, 2, QTableWidgetItem(str(med.get('batch_no', ''))))
            self.medicine_table.setItem(row_pos, 3, QTableWidgetItem(str(med.get('expiry_date', ''))))
            self.medicine_table.setItem(row_pos, 4, QTableWidgetItem(str(med.get('quantity', ''))))
            self.medicine_table.setItem(row_pos, 5, QTableWidgetItem("₨ {:.2f}".format(med.get('unit_price', 0))))
        
        # Update pagination controls
        self.page_label.setText(f"Page {self.current_page + 1} of {max(1, total_pages)}")
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < total_pages - 1)
        self.medicine_table.clearSelection()
        self.selected_medicine = None

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.fast_filter_medicine_table()

    def next_page(self):
        search = self.medicine_search.text().strip().lower()
        filtered_meds = [med for med in self.medicines if not is_expired(med.get("expiry_date", "2099-01-01")) and (
            search in med['name'].lower() or
            search in str(med.get('strength', '')).lower() or
            search in str(med.get('batch_no', '')).lower() or
            search in str(med.get('expiry_date', '')).lower()
        )] if search else [med for med in self.medicines if not is_expired(med.get("expiry_date", "2099-01-01"))]
        total_pages = (len(filtered_meds) + self.items_per_page - 1) // self.items_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.fast_filter_medicine_table()

    def load_customers(self):
        self.cust_combo.clear()
        self.customers = db.get_customers()
        self.cust_combo.addItem("Select Customer", None)
        for cust in self.customers:
            self.cust_combo.addItem(f"{cust['name']} ({cust['contact']})", cust["id"])

    def toggle_customer_fields(self):
        is_new = self.cust_type_combo.currentData() == "new"
        self.cust_combo.setVisible(not is_new)
        self.new_cust_name.setVisible(is_new)
        self.new_cust_contact.setVisible(is_new)
        self.new_cust_address.setVisible(is_new)

    def get_selected_medicine(self):
        selected_rows = self.medicine_table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        row = selected_rows[0].row()
        name = self.medicine_table.item(row, 0).text()
        strength = self.medicine_table.item(row, 1).text()
        batch = self.medicine_table.item(row, 2).text()
        med = next((m for m in self.medicines if m['name'] == name and str(m.get('strength','')) == strength and str(m.get('batch_no','')) == batch), None)
        return med

    def save_sale(self):
        try:
            # Validate inputs
            med = self.get_selected_medicine()
            if not med:
                QMessageBox.warning(self, "Input Error", "Please select a medicine from the table.")
                return

            # Check again for expiry (in case table is out of sync)
            if is_expired(med.get("expiry_date", "2099-01-01")):
                QMessageBox.warning(self, "Expired Medicine", f"{med['name']} is expired and cannot be sold.")
                return

            qty = self.qty_spin.value()
            if qty > med['quantity']:
                QMessageBox.warning(self, "Stock Error", f"Only {med['quantity']} available in stock for {med['name']}.")
                return

            # Handle customer
            customer_id = self.get_or_create_customer()
            if customer_id is None:
                return  # Error already shown

            # Perform atomic operation
            success, message = db.record_sale_with_stock_update(
                medicine_id=med["id"],
                quantity=qty,
                customer_id=customer_id
            )
            
            if not success:
                raise Exception(message)
            
            QMessageBox.information(self, "Sale Recorded!", "Sale recorded successfully!")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def get_or_create_customer(self):
        if self.cust_type_combo.currentData() == "existing":
            selected_customer_id = self.cust_combo.currentData()
            if selected_customer_id is None:
                QMessageBox.warning(self, "Input Error", "Please select an existing customer or choose 'New Customer'.")
                return None
            return selected_customer_id
        
        name = self.new_cust_name.text().strip()
        contact = self.new_cust_contact.text().strip()
        address = self.new_cust_address.text().strip()
        
        if not name or not contact:
            QMessageBox.warning(self, "Input Error", "New customer name and contact are required.")
            return None
        
        try:
            return db.add_customer(name, contact, address)
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to add new customer: {str(e)}")
            return None

class PurchaseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Record New Purchase")
        self.setMinimumSize(1000, 650)

        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f5f6fa, stop:1 #ffffff);
                border-radius: 12px;
            }
            QLabel {
                font-size: 16px;
                color: #34495e;
            }
            QLabel#header_label {
                font-size: 28px;
                font-weight: bold;
                color: white;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff9966, stop:1 #ff5e62);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }
            QLineEdit, QSpinBox {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }
            QTableWidget {
                background: white;
                border-radius: 8px;
                border: 1px solid #ddd;
                font-size: 13px;
            }
            QTableWidget::item { padding: 6px; }
            QTableWidget::item:alternate { background: #f9f9f9; }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff9966, stop:1 #ff5e62);
                color: white; font-weight: bold; padding: 8px; border: none;
                border-radius: 8px 8px 0 0;
            }
            QComboBox {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }
            QPushButton {
                border-radius: 8px;
                padding: 10px 20px;
                min-width: 120px;
                font-weight: bold;
                border: none;
                color: white;
                font-size: 15px;
                transition: background 0.3s ease;
            }
            QPushButton#record_purchase_btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #007bff, stop:1 #0056b3);
            }
            QPushButton#record_purchase_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0056b3, stop:1 #007bff);
            }
            QPushButton#prev_btn, QPushButton#next_btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6c757d, stop:1 #5a6268);
            }
            QPushButton#prev_btn:hover, QPushButton#next_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5a6268, stop:1 #6c757d);
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header_label = QLabel("Record New Purchase")
        header_label.setObjectName("header_label")
        main_layout.addWidget(header_label)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Fast Medicine Search
        self.medicine_search = QLineEdit()
        self.medicine_search.setPlaceholderText("Type to search medicine name, batch, etc...")
        self.medicine_search.textChanged.connect(self.fast_filter_medicine_table)
        form_layout.addRow("Medicine Search:", self.medicine_search)

        # Table of Medicines
        self.medicine_table = QTableWidget(0, 6)
        self.medicine_table.setHorizontalHeaderLabels([
            "Name", "Strength", "Batch", "Expiry", "Stock", "Unit Price"
        ])
        self.medicine_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.medicine_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.medicine_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.medicine_table.setMinimumHeight(170)
        form_layout.addRow(self.medicine_table)

        # Pagination Controls
        self.current_page = 0
        self.items_per_page = 100
        pagination_layout = QHBoxLayout()
        pagination_layout.addStretch()
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.setObjectName("prev_btn")
        self.prev_btn.setCursor(Qt.PointingHandCursor)
        self.prev_btn.clicked.connect(self.prev_page)
        pagination_layout.addWidget(self.prev_btn)
        self.page_label = QLabel("Page 1")
        pagination_layout.addWidget(self.page_label)
        self.next_btn = QPushButton("Next")
        self.next_btn.setObjectName("next_btn")
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.next_btn)
        pagination_layout.addStretch()
        form_layout.addRow(pagination_layout)

        # Quantity Input
        self.qty_spin = QSpinBox()
        self.qty_spin.setMinimum(1)
        self.qty_spin.setMaximum(9999)
        form_layout.addRow("Quantity:", self.qty_spin)

        # Price Input
        self.price_edit = QLineEdit()
        self.price_edit.setPlaceholderText("Unit price (₨ )")
        form_layout.addRow("Unit Price:", self.price_edit)

        main_layout.addLayout(form_layout)

        # Supplier Selection
        self.supplier_group = QVBoxLayout()
        self.setup_supplier_fields()
        main_layout.addLayout(self.supplier_group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.record_purchase_btn = QPushButton("Record Purchase")
        self.record_purchase_btn.setObjectName("record_purchase_btn")
        self.record_purchase_btn.setCursor(Qt.PointingHandCursor)
        self.record_purchase_btn.clicked.connect(self.save_purchase)
        btn_layout.addWidget(self.record_purchase_btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        self.medicines = []
        self.selected_medicine = None
        self.load_medicines()

    def setup_supplier_fields(self):
        self.supplier_group.addWidget(QLabel("Supplier Information:"))
        
        self.supp_type_combo = QComboBox()
        self.supp_type_combo.addItem("Select Existing Supplier", "existing")
        self.supp_type_combo.addItem("New Supplier", "new")
        self.supplier_group.addWidget(self.supp_type_combo)
        
        self.supp_combo = QComboBox()
        self.load_suppliers()
        self.supplier_group.addWidget(self.supp_combo)
        
        self.new_supp_name = QLineEdit()
        self.new_supp_name.setPlaceholderText("Supplier Name")
        self.new_supp_name.setVisible(False)
        self.supplier_group.addWidget(self.new_supp_name)
        
        self.new_supp_contact = QLineEdit()
        self.new_supp_contact.setPlaceholderText("Contact Info")
        self.new_supp_contact.setVisible(False)
        self.supplier_group.addWidget(self.new_supp_contact)
        
        self.new_supp_address = QLineEdit()
        self.new_supp_address.setPlaceholderText("Address (Optional)")
        self.new_supp_address.setVisible(False)
        self.supplier_group.addWidget(self.new_supp_address)
        
        self.supp_type_combo.currentIndexChanged.connect(self.toggle_supplier_fields)

    def load_medicines(self):
        self.medicines = db.get_all_medicines()
        self.fast_filter_medicine_table()

    def fast_filter_medicine_table(self):
        search = self.medicine_search.text().strip().lower()
        filtered_meds = []
        for med in self.medicines:
            display = (
                search in med['name'].lower() or
                search in str(med.get('strength', '')).lower() or
                search in str(med.get('batch_no', '')).lower() or
                search in str(med.get('expiry_date', '')).lower()
            ) if search else True
            if display:
                filtered_meds.append(med)
        
        # Calculate pagination
        total_items = len(filtered_meds)
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        self.current_page = min(self.current_page, max(0, total_pages - 1))
        start_idx = self.current_page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_items)
        
        # Update table with paginated items
        self.medicine_table.setRowCount(0)
        for med in filtered_meds[start_idx:end_idx]:
            row_pos = self.medicine_table.rowCount()
            self.medicine_table.insertRow(row_pos)
            for col, key in enumerate(['name', 'strength', 'batch_no', 'expiry_date', 'quantity', 'unit_price']):
                value = med.get(key, '')
                if col == 5:
                    value = "₨ {:.2f}".format(med.get('unit_price', 0))
                item = QTableWidgetItem(str(value))
                if is_expired(med.get("expiry_date", "2099-01-01")):
                    item.setForeground(Qt.red)
                    item.setToolTip("Expired medicine - check expiry!")
                self.medicine_table.setItem(row_pos, col, item)
        
        # Update pagination controls
        self.page_label.setText(f"Page {self.current_page + 1} of {max(1, total_pages)}")
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < total_pages - 1)
        self.medicine_table.clearSelection()
        self.selected_medicine = None

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.fast_filter_medicine_table()

    def next_page(self):
        search = self.medicine_search.text().strip().lower()
        filtered_meds = [med for med in self.medicines if (
            search in med['name'].lower() or
            search in str(med.get('strength', '')).lower() or
            search in str(med.get('batch_no', '')).lower() or
            search in str(med.get('expiry_date', '')).lower()
        )] if search else self.medicines
        total_pages = (len(filtered_meds) + self.items_per_page - 1) // self.items_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.fast_filter_medicine_table()

    def load_suppliers(self):
        self.supp_combo.clear()
        self.suppliers = db.get_suppliers()
        self.supp_combo.addItem("Select Supplier", None)
        for supp in self.suppliers:
            self.supp_combo.addItem(f"{supp['name']} ({supp['contact']})", supp["id"])

    def toggle_supplier_fields(self):
        is_new = self.supp_type_combo.currentData() == "new"
        self.supp_combo.setVisible(not is_new)
        self.new_supp_name.setVisible(is_new)
        self.new_supp_contact.setVisible(is_new)
        self.new_supp_address.setVisible(is_new)

    def get_selected_medicine(self):
        selected_rows = self.medicine_table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        row = selected_rows[0].row()
        name = self.medicine_table.item(row, 0).text()
        strength = self.medicine_table.item(row, 1).text()
        batch = self.medicine_table.item(row, 2).text()
        med = next((m for m in self.medicines if m['name'] == name and str(m.get('strength','')) == strength and str(m.get('batch_no','')) == batch), None)
        return med

    def save_purchase(self):
        try:
            med = self.get_selected_medicine()
            if not med:
                QMessageBox.warning(self, "Input Error", "Please select a medicine from the table.")
                return

            qty = self.qty_spin.value()
            try:
                unit_price = float(self.price_edit.text())
                if unit_price <= 0:
                    QMessageBox.warning(self, "Input Error", "Price must be positive.")
                    return
            except ValueError:
                QMessageBox.warning(self, "Input Error", "Please enter a valid unit price.")
                return

            # Show a warning if the med is expired (but allow recording if user chooses)
            if is_expired(med.get("expiry_date", "2099-01-01")):
                reply = QMessageBox.question(
                    self,
                    "Expired Medicine",
                    f"{med['name']} appears to be expired ({med.get('expiry_date', '')}). Are you sure you want to record purchase?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return

            supplier_id = self.get_or_create_supplier()
            if supplier_id is None:
                return

            success, message = db.record_purchase_with_stock_update(
                medicine_id=med["id"],
                quantity=qty,
                unit_price=unit_price,
                supplier_id=supplier_id
            )
            if not success:
                raise Exception(message)
            QMessageBox.information(self, "Purchase Recorded!", "Purchase recorded successfully!")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def get_or_create_supplier(self):
        if self.supp_type_combo.currentData() == "existing":
            selected_supplier_id = self.supp_combo.currentData()
            if selected_supplier_id is None:
                QMessageBox.warning(self, "Input Error", "Please select an existing supplier or choose 'New Supplier'.")
                return None
            return selected_supplier_id
        
        name = self.new_supp_name.text().strip()
        contact = self.new_supp_contact.text().strip()
        address = self.new_supp_address.text().strip()
        
        if not name or not contact:
            QMessageBox.warning(self, "Input Error", "New supplier name and contact are required.")
            return None
        
        try:
            return db.add_supplier(name, contact, address)
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to add new supplier: {str(e)}")
            return None