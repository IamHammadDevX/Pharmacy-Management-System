from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, QHBoxLayout, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QLabel
)
from PyQt5.QtCore import Qt
from db import (
    get_suppliers, add_supplier, update_supplier, delete_supplier,
    get_customers, add_customer, update_customer, delete_customer
)

class SupplierCustomerManagement(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Supplier & Customer Management")
        self.setMinimumSize(700, 440)
        self.setStyleSheet("""
            QDialog {
                background: #f5f6fa;
            }
            QTabWidget::pane {
                border: 0;
                background:#fff;
            }
            QTabBar::tab {
                min-width: 160px;
                min-height: 30px;
                font-weight: bold;
                font-size: 16px;
                background: #e3eafc;
                border-radius: 8px 8px 0 0;
                margin-right: 2px;
                padding: 8px 18px;
            }
            QTabBar::tab:selected {
                background: #1565c0;
                color: #fff;
            }
            QTableWidget {
                border-radius: 7px;
                background: #fdfdfd;
                font-size: 14px;
            }
        """)
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Supplier Tab
        self.supplier_tab = QWidget()
        self.tabs.addTab(self.supplier_tab, "Suppliers")
        self.setup_supplier_tab()

        # Customer Tab
        self.customer_tab = QWidget()
        self.tabs.addTab(self.customer_tab, "Customers")
        self.setup_customer_tab()

    # ----------------- SUPPLIER TAB -----------------
    def setup_supplier_tab(self):
        vbox = QVBoxLayout(self.supplier_tab)
        self.supplier_table = QTableWidget()
        self.supplier_table.setColumnCount(4)
        self.supplier_table.setHorizontalHeaderLabels(["Name", "Contact", "Address", "Actions"])
        self.supplier_table.horizontalHeader().setStretchLastSection(True)
        self.supplier_table.setEditTriggers(QTableWidget.NoEditTriggers)
        vbox.addWidget(self.supplier_table)
        self.load_suppliers()

        # Add/Edit Form
        form = QHBoxLayout()
        self.supplier_name = QLineEdit()
        self.supplier_name.setPlaceholderText("Name")
        self.supplier_contact = QLineEdit()
        self.supplier_contact.setPlaceholderText("Contact")
        self.supplier_address = QLineEdit()
        self.supplier_address.setPlaceholderText("Address")
        self.supplier_add_btn = QPushButton("Add Supplier")
        self.supplier_add_btn.setStyleSheet("QPushButton { background: #43cea2; color: #fff; font-weight: bold; border-radius: 6px; padding: 7px 16px; }")
        self.supplier_add_btn.clicked.connect(self.add_or_update_supplier)
        self.supplier_cancel_btn = QPushButton("Cancel")
        self.supplier_cancel_btn.setVisible(False)
        self.supplier_cancel_btn.setStyleSheet("QPushButton { background: #eee; color: #1565c0; font-weight: bold; border-radius: 6px; padding: 7px 16px; }")
        self.supplier_cancel_btn.clicked.connect(self.reset_supplier_form)
        form.addWidget(self.supplier_name)
        form.addWidget(self.supplier_contact)
        form.addWidget(self.supplier_address)
        form.addWidget(self.supplier_add_btn)
        form.addWidget(self.supplier_cancel_btn)
        vbox.addLayout(form)
        self.editing_supplier_id = None

    def load_suppliers(self):
        self.supplier_table.setRowCount(0)
        for row, (sid, name, contact, address) in enumerate(get_suppliers()):
            self.supplier_table.insertRow(row)
            self.supplier_table.setItem(row, 0, QTableWidgetItem(name))
            self.supplier_table.setItem(row, 1, QTableWidgetItem(contact or ""))
            self.supplier_table.setItem(row, 2, QTableWidgetItem(address or ""))
            # Actions (Edit/Delete)
            actions = QWidget()
            h = QHBoxLayout(actions)
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("QPushButton { background: #e3eafc; border-radius: 5px; }")
            edit_btn.setFixedWidth(34)
            edit_btn.clicked.connect(lambda _, sid=sid: self.fill_supplier_form(sid))
            del_btn = QPushButton("Delete")
            del_btn.setStyleSheet("QPushButton { background: #ffbdbd; border-radius: 5px; }")
            del_btn.setFixedWidth(34)
            del_btn.clicked.connect(lambda _, sid=sid: self.delete_supplier_confirm(sid))
            h.addWidget(edit_btn)
            h.addWidget(del_btn)
            h.setAlignment(Qt.AlignCenter)
            h.setContentsMargins(0,0,0,0)
            actions.setLayout(h)
            self.supplier_table.setCellWidget(row, 3, actions)

    def fill_supplier_form(self, sid):
        for s in get_suppliers():
            if s[0] == sid:
                self.editing_supplier_id = sid
                self.supplier_name.setText(s[1])
                self.supplier_contact.setText(s[2] or "")
                self.supplier_address.setText(s[3] or "")
                self.supplier_add_btn.setText("Update Supplier")
                self.supplier_cancel_btn.setVisible(True)
                break

    def add_or_update_supplier(self):
        name = self.supplier_name.text().strip()
        contact = self.supplier_contact.text().strip()
        address = self.supplier_address.text().strip()
        if not name:
            QMessageBox.warning(self, "Input error", "Supplier name is required.")
            return
        if self.editing_supplier_id:
            update_supplier(self.editing_supplier_id, name, contact, address)
        else:
            add_supplier(name, contact, address)
        self.load_suppliers()
        self.reset_supplier_form()

    def delete_supplier_confirm(self, sid):
        reply = QMessageBox.question(self, "Delete", "Are you sure you want to delete this supplier?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            delete_supplier(sid)
            self.load_suppliers()
            self.reset_supplier_form()

    def reset_supplier_form(self):
        self.supplier_name.clear()
        self.supplier_contact.clear()
        self.supplier_address.clear()
        self.supplier_add_btn.setText("Add Supplier")
        self.supplier_cancel_btn.setVisible(False)
        self.editing_supplier_id = None

    # ----------------- CUSTOMER TAB -----------------
    def setup_customer_tab(self):
        vbox = QVBoxLayout(self.customer_tab)
        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(4)
        self.customer_table.setHorizontalHeaderLabels(["Name", "Contact", "Address", "Actions"])
        self.customer_table.horizontalHeader().setStretchLastSection(True)
        self.customer_table.setEditTriggers(QTableWidget.NoEditTriggers)
        vbox.addWidget(self.customer_table)
        self.load_customers()

        # Add/Edit Form
        form = QHBoxLayout()
        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("Name")
        self.customer_contact = QLineEdit()
        self.customer_contact.setPlaceholderText("Contact")
        self.customer_address = QLineEdit()
        self.customer_address.setPlaceholderText("Address")
        self.customer_add_btn = QPushButton("Add Customer")
        self.customer_add_btn.setStyleSheet("QPushButton { background: #43cea2; color: #fff; font-weight: bold; border-radius: 6px; padding: 7px 16px; }")
        self.customer_add_btn.clicked.connect(self.add_or_update_customer)
        self.customer_cancel_btn = QPushButton("Cancel")
        self.customer_cancel_btn.setVisible(False)
        self.customer_cancel_btn.setStyleSheet("QPushButton { background: #eee; color: #1565c0; font-weight: bold; border-radius: 6px; padding: 7px 16px; }")
        self.customer_cancel_btn.clicked.connect(self.reset_customer_form)
        form.addWidget(self.customer_name)
        form.addWidget(self.customer_contact)
        form.addWidget(self.customer_address)
        form.addWidget(self.customer_add_btn)
        form.addWidget(self.customer_cancel_btn)
        vbox.addLayout(form)
        self.editing_customer_id = None

    def load_customers(self):
        self.customer_table.setRowCount(0)
        for row, (cid, name, contact, address) in enumerate(get_customers()):
            self.customer_table.insertRow(row)
            self.customer_table.setItem(row, 0, QTableWidgetItem(name))
            self.customer_table.setItem(row, 1, QTableWidgetItem(contact or ""))
            self.customer_table.setItem(row, 2, QTableWidgetItem(address or ""))
            # Actions (Edit/Delete)
            actions = QWidget()
            h = QHBoxLayout(actions)
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("QPushButton { background: #e3eafc; border-radius: 5px; }")
            edit_btn.setFixedWidth(34)
            edit_btn.clicked.connect(lambda _, cid=cid: self.fill_customer_form(cid))
            del_btn = QPushButton("Delete")
            del_btn.setStyleSheet("QPushButton { background: #ffbdbd; border-radius: 5px; }")
            del_btn.setFixedWidth(34)
            del_btn.clicked.connect(lambda _, cid=cid: self.delete_customer_confirm(cid))
            h.addWidget(edit_btn)
            h.addWidget(del_btn)
            h.setAlignment(Qt.AlignCenter)
            h.setContentsMargins(0,0,0,0)
            actions.setLayout(h)
            self.customer_table.setCellWidget(row, 3, actions)

    def fill_customer_form(self, cid):
        for c in get_customers():
            if c[0] == cid:
                self.editing_customer_id = cid
                self.customer_name.setText(c[1])
                self.customer_contact.setText(c[2] or "")
                self.customer_address.setText(c[3] or "")
                self.customer_add_btn.setText("Update Customer")
                self.customer_cancel_btn.setVisible(True)
                break

    def add_or_update_customer(self):
        name = self.customer_name.text().strip()
        contact = self.customer_contact.text().strip()
        address = self.customer_address.text().strip()
        if not name:
            QMessageBox.warning(self, "Input error", "Customer name is required.")
            return
        if self.editing_customer_id:
            update_customer(self.editing_customer_id, name, contact, address)
        else:
            add_customer(name, contact, address)
        self.load_customers()
        self.reset_customer_form()

    def delete_customer_confirm(self, cid):
        reply = QMessageBox.question(self, "Delete", "Are you sure you want to delete this customer?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            delete_customer(cid)
            self.load_customers()
            self.reset_customer_form()

    def reset_customer_form(self):
        self.customer_name.clear()
        self.customer_contact.clear()
        self.customer_address.clear()
        self.customer_add_btn.setText("Add Customer")
        self.customer_cancel_btn.setVisible(False)
        self.editing_customer_id = None