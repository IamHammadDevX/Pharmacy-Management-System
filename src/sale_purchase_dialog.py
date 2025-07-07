from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit, 
    QPushButton, QMessageBox, QHBoxLayout, QSpinBox, QFormLayout
)
from PyQt5.QtCore import Qt
import db
import datetime

class SaleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Record New Sale")
        self.setMinimumSize(500, 550) # Adjusted size for better layout
        
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
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #43cea2, stop:1 #185a9d); /* Green-blue gradient */
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }
            QComboBox, QLineEdit, QSpinBox {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }
            QComboBox::drop-down {
                border: 0px; /* No border for the dropdown arrow */
            }
            QComboBox::down-arrow {
                image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAAVUlEQVQ4jWNgGAWjYBSMglEwCkYBCSA+jE0gV0yVjQYg1wI+gFgYgPgfSDUaQGg+MhBqgC4g1gwMDSBVAzIKoGaAqhFkgWzUjYDRjYDRgYAIAD8mK3s6+GfXAAAAAElFTkSuQmCC); /* Custom arrow icon */
                width: 16px;
                height: 16px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                background-color: #f0f0f0;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #e0e0e0;
            }
            QSpinBox::up-arrow, QSpinBox::down-arrow {
                width: 10px;
                height: 10px;
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
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #28a745, stop:1 #218838); /* Green gradient */
            }
            QPushButton#record_sale_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #218838, stop:1 #28a745);
            }
            QPushButton#record_purchase_btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #007bff, stop:1 #0056b3); /* Blue gradient */
            }
            QPushButton#record_purchase_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0056b3, stop:1 #007bff);
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

        # Medicine Selection
        self.medicine_box = QComboBox()
        self.load_medicines()
        form_layout.addRow("Medicine:", self.medicine_box)

        # Quantity Input
        self.qty_spin = QSpinBox()
        self.qty_spin.setMinimum(1)
        self.qty_spin.setMaximum(9999) # Increased max quantity
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
        self.medicine_box.clear()
        self.medicines = db.get_all_medicines()
        self.medicine_box.addItem("Select Medicine", None)
        for med in self.medicines:
            # Ensure 'quantity' is treated as an integer for comparison
            stock_info = f" (Stock: {med['quantity']})" if med['quantity'] > 0 else " (Out of Stock)"
            self.medicine_box.addItem(
                f"{med['name']} ({med['strength']}) - ${med['unit_price']:.2f}{stock_info}", 
                med["id"]
            )
            # Disable selection if out of stock
            if med['quantity'] <= 0:
                item_index = self.medicine_box.findData(med["id"])
                if item_index != -1:
                    self.medicine_box.model().item(item_index).setEnabled(False)


    def load_customers(self):
        self.cust_combo.clear()
        self.customers = db.get_customers() # Fetch customers as dicts
        self.cust_combo.addItem("Select Customer", None)
        for cust in self.customers: # Iterate over dicts
            self.cust_combo.addItem(f"{cust['name']} ({cust['contact']})", cust["id"])

    def toggle_customer_fields(self):
        is_new = self.cust_type_combo.currentData() == "new"
        self.cust_combo.setVisible(not is_new)
        self.new_cust_name.setVisible(is_new)
        self.new_cust_contact.setVisible(is_new)
        self.new_cust_address.setVisible(is_new)

    def save_sale(self):
        try:
            # Validate inputs
            med_id = self.medicine_box.currentData()
            if not med_id:
                QMessageBox.warning(self, "Input Error", "Please select a medicine.")
                return

            qty = self.qty_spin.value()
            selected_med = next((m for m in self.medicines if m['id'] == med_id), None)
            if not selected_med:
                QMessageBox.critical(self, "Error", "Selected medicine not found in stock list.")
                return
            if qty > selected_med['quantity']:
                QMessageBox.warning(self, "Stock Error", f"Only {selected_med['quantity']} available in stock for {selected_med['name']}.")
                return

            # Handle customer
            customer_id = self.get_or_create_customer()
            if customer_id is None:
                return  # Error already shown by get_or_create_customer

            # Perform atomic operation - quantity updated within record_sale_with_stock_update
            success, message = db.record_sale_with_stock_update(
                medicine_id=med_id,
                quantity=qty,
                customer_id=customer_id
            )
            
            if not success:
                raise Exception(message)
            
            # Show success message
            QMessageBox.information(self, "Sale Recorded!", "Sale recorded successfully!")
            self.accept() # Close the dialog on success

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
            # db.add_customer returns the ID of the new customer
            return db.add_customer(name, contact, address)
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to add new customer: {str(e)}")
            return None


class PurchaseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Record New Purchase")
        self.setMinimumSize(500, 550) # Adjusted size for better layout

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
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff9966, stop:1 #ff5e62); /* Orange-red gradient */
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }
            QComboBox, QLineEdit, QSpinBox {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAAVUlEQVQ4jWNgGAWjYBSMglEwCkYBCSA+jE0gV0yVjQYg1wI+gFgYgPgfSDUaQGg+MhBqgC4g1gwMDSBVAzIKoGaAqhFkgWzUjYDRjYDRgYAIAD8mK3s6+GfXAAAAAElFTkSuQmCC);
                width: 16px;
                height: 16px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                background-color: #f0f0f0;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #e0e0e0;
            }
            QSpinBox::up-arrow, QSpinBox::down-arrow {
                width: 10px;
                height: 10px;
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
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #007bff, stop:1 #0056b3); /* Blue gradient */
            }
            QPushButton#record_purchase_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0056b3, stop:1 #007bff);
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

        # Medicine Selection
        self.medicine_box = QComboBox()
        self.load_medicines()
        form_layout.addRow("Medicine:", self.medicine_box)

        # Quantity Input
        self.qty_spin = QSpinBox()
        self.qty_spin.setMinimum(1)
        self.qty_spin.setMaximum(9999)
        form_layout.addRow("Quantity:", self.qty_spin)

        # Price Input
        self.price_edit = QLineEdit()
        self.price_edit.setPlaceholderText("Unit price")
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
        self.medicine_box.clear()
        # db.get_all_medicines() now returns dicts due to row_factory in db.py
        self.medicines = db.get_all_medicines() 
        self.medicine_box.addItem("Select Medicine", None)
        for med in self.medicines:
            self.medicine_box.addItem(
                f"{med['name']} ({med['strength']})", 
                med["id"]
            )

    def load_suppliers(self):
        self.supp_combo.clear()
        # db.get_suppliers() now returns dicts due to row_factory in db.py
        self.suppliers = db.get_suppliers() 
        self.supp_combo.addItem("Select Supplier", None)
        for supp in self.suppliers: # Iterate over dicts
            self.supp_combo.addItem(f"{supp['name']} ({supp['contact']})", supp["id"])

    def toggle_supplier_fields(self):
        is_new = self.supp_type_combo.currentData() == "new"
        self.supp_combo.setVisible(not is_new)
        self.new_supp_name.setVisible(is_new)
        self.new_supp_contact.setVisible(is_new)
        self.new_supp_address.setVisible(is_new)

    def save_purchase(self):
        try:
            # Validate inputs
            med_id = self.medicine_box.currentData()
            if not med_id:
                QMessageBox.warning(self, "Input Error", "Please select a medicine.")
                return

            qty = self.qty_spin.value()
            if qty <= 0:
                QMessageBox.warning(self, "Input Error", "Quantity must be positive.")
                return

            try:
                unit_price = float(self.price_edit.text())
                if unit_price <= 0:
                    QMessageBox.warning(self, "Input Error", "Price must be positive.")
                    return
            except ValueError:
                QMessageBox.warning(self, "Input Error", "Please enter a valid unit price.")
                return

            # Handle supplier
            supplier_id = self.get_or_create_supplier()
            if supplier_id is None:
                return  # Error already shown by get_or_create_supplier

            # Perform atomic operation - quantity updated within record_purchase_with_stock_update
            success, message = db.record_purchase_with_stock_update(
                medicine_id=med_id,
                quantity=qty,
                unit_price=unit_price,
                supplier_id=supplier_id
            )
            
            if not success:
                raise Exception(message)
            
            # Show success message
            QMessageBox.information(self, "Purchase Recorded!", "Purchase recorded successfully!")
            self.accept() # Close the dialog on success

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
            # db.add_supplier returns the ID of the new supplier
            return db.add_supplier(name, contact, address)
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to add new supplier: {str(e)}")
            return None

