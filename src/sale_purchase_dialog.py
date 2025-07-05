from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit, 
    QPushButton, QMessageBox, QHBoxLayout, QSpinBox
)
from PyQt5.QtCore import Qt
import db
import datetime

class SaleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Record New Sale")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)

        # Medicine Selection
        self.medicine_box = QComboBox()
        self.load_medicines()
        layout.addWidget(QLabel("Medicine:"))
        layout.addWidget(self.medicine_box)

        # Quantity Input
        qty_layout = QHBoxLayout()
        self.qty_spin = QSpinBox()
        self.qty_spin.setMinimum(1)
        self.qty_spin.setMaximum(999)
        qty_layout.addWidget(QLabel("Quantity:"))
        qty_layout.addWidget(self.qty_spin)
        layout.addLayout(qty_layout)

        # Customer Selection
        self.customer_group = QVBoxLayout()
        self.setup_customer_fields()
        layout.addLayout(self.customer_group)

        # Buttons
        btn = QPushButton("Record Sale")
        btn.setStyleSheet("background-color: #4CAF50; color: white;")
        btn.clicked.connect(self.save_sale)
        layout.addWidget(btn)

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
            stock_info = f" (Stock: {med['quantity']})" if med['quantity'] > 0 else " (Out of Stock)"
            self.medicine_box.addItem(
                f"{med['name']} ({med['strength']}) - ${med['unit_price']:.2f}{stock_info}", 
                med["id"]
            )

    def load_customers(self):
        self.cust_combo.clear()
        self.cust_combo.addItem("Select Customer", None)
        for cid, name, contact, address in db.get_customers():
            self.cust_combo.addItem(f"{name} ({contact})", cid)

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
                raise ValueError("Please select a medicine")

            qty = self.qty_spin.value()
            selected_med = next((m for m in self.medicines if m['id'] == med_id), None)
            if not selected_med:
                raise ValueError("Selected medicine not found")
            if qty > selected_med['quantity']:
                raise ValueError(f"Only {selected_med['quantity']} available in stock")

            # Handle customer
            customer_id = self.get_or_create_customer()
            if customer_id is None:
                return  # Error already shown

            # Perform atomic operation - quantity updated within record_sale
            success, message = db.record_sale_with_stock_update(
                medicine_id=med_id,
                quantity=qty,
                customer_id=customer_id
            )
            
            if not success:
                raise Exception(message)
            
            self.handle_success(med_id)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def get_or_create_customer(self):
        if self.cust_type_combo.currentData() == "existing":
            return self.cust_combo.currentData()
        
        name = self.new_cust_name.text().strip()
        contact = self.new_cust_contact.text().strip()
        address = self.new_cust_address.text().strip()
        
        if not name or not contact:
            QMessageBox.warning(self, "Error", "Customer name and contact are required")
            return None
        
        try:
            return db.add_customer(name, contact, address)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add customer: {str(e)}")
            return None

    def handle_success(self, med_id):
        # Refresh if medicine was removed
        current_med = next((m for m in db.get_all_medicines() if m['id'] == med_id), None)
        if not current_med:
            QMessageBox.information(self, "Medicine Removed", "This medicine is now out of stock")
            if hasattr(self.parent(), 'refresh_medicine_data'):
                self.parent().refresh_medicine_data()
        
        self.load_medicines()
        QMessageBox.information(self, "Success", "Sale recorded successfully!")
        self.accept()


class PurchaseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Record New Purchase")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)

        # Medicine Selection
        self.medicine_box = QComboBox()
        self.load_medicines()
        layout.addWidget(QLabel("Medicine:"))
        layout.addWidget(self.medicine_box)

        # Quantity Input
        qty_layout = QHBoxLayout()
        self.qty_spin = QSpinBox()
        self.qty_spin.setMinimum(1)
        self.qty_spin.setMaximum(9999)
        qty_layout.addWidget(QLabel("Quantity:"))
        qty_layout.addWidget(self.qty_spin)
        layout.addLayout(qty_layout)

        # Price Input
        self.price_edit = QLineEdit()
        self.price_edit.setPlaceholderText("Unit price")
        layout.addWidget(QLabel("Unit Price:"))
        layout.addWidget(self.price_edit)

        # Supplier Selection
        self.supplier_group = QVBoxLayout()
        self.setup_supplier_fields()
        layout.addLayout(self.supplier_group)

        # Buttons
        btn = QPushButton("Record Purchase")
        btn.setStyleSheet("background-color: #2196F3; color: white;")
        btn.clicked.connect(self.save_purchase)
        layout.addWidget(btn)

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
        self.medicines = db.get_all_medicines()
        self.medicine_box.addItem("Select Medicine", None)
        for med in self.medicines:
            self.medicine_box.addItem(
                f"{med['name']} ({med['strength']})", 
                med["id"]
            )

    def load_suppliers(self):
        self.supp_combo.clear()
        self.supp_combo.addItem("Select Supplier", None)
        for sid, name, contact, address in db.get_suppliers():
            self.supp_combo.addItem(f"{name} ({contact})", sid)

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
                raise ValueError("Please select a medicine")

            qty = self.qty_spin.value()
            if qty <= 0:
                raise ValueError("Quantity must be positive")

            try:
                unit_price = float(self.price_edit.text())
                if unit_price <= 0:
                    raise ValueError("Price must be positive")
            except ValueError:
                raise ValueError("Please enter a valid unit price")

            # Handle supplier
            supplier_id = self.get_or_create_supplier()
            if supplier_id is None:
                return  # Error already shown

            # Perform atomic operation - quantity updated within record_purchase
            success, message = db.record_purchase_with_stock_update(
                medicine_id=med_id,
                quantity=qty,
                unit_price=unit_price,
                supplier_id=supplier_id
            )
            
            if not success:
                raise Exception(message)
            
            QMessageBox.information(self, "Success", "Purchase recorded successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def get_or_create_supplier(self):
        if self.supp_type_combo.currentData() == "existing":
            return self.supp_combo.currentData()
        
        name = self.new_supp_name.text().strip()
        contact = self.new_supp_contact.text().strip()
        address = self.new_supp_address.text().strip()
        
        if not name or not contact:
            QMessageBox.warning(self, "Error", "Supplier name and contact are required")
            return None
        
        try:
            return db.add_supplier(name, contact, address)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add supplier: {str(e)}")
            return None