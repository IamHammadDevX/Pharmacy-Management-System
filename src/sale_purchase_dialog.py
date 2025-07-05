from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox
)
import db

class SaleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Record New Sale")
        layout = QVBoxLayout(self)

        self.medicines = db.get_all_medicines()
        self.medicine_box = QComboBox()
        for med in self.medicines:
            self.medicine_box.addItem(f"{med['name']} ({med['strength']})", med["id"])
        layout.addWidget(QLabel("Medicine:"))
        layout.addWidget(self.medicine_box)

        self.qty_edit = QLineEdit()
        self.qty_edit.setPlaceholderText("e.g. 5")
        layout.addWidget(QLabel("Quantity:"))
        layout.addWidget(self.qty_edit)

        # Use dropdown for customer selection (with editable field for new)
        self.cust_box = QComboBox()
        self.cust_box.setEditable(True)
        self.cust_box.setInsertPolicy(QComboBox.NoInsert)
        self.cust_box.addItem("")  # for optional
        for cid, name, contact, address in db.get_customers():
            self.cust_box.addItem(name, cid)
        layout.addWidget(QLabel("Customer (optional):"))
        layout.addWidget(self.cust_box)

        btn = QPushButton("Record Sale")
        btn.clicked.connect(self.save_sale)
        layout.addWidget(btn)

    def save_sale(self):
        med_id = self.medicine_box.currentData()
        try:
            qty = int(self.qty_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Quantity must be a number.")
            return
        cust = self.cust_box.currentText().strip()
        customer = cust if cust else None
        try:
            db.record_sale(med_id, qty, customer=customer)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
            return
        QMessageBox.information(self, "Success", "Sale recorded!")
        self.accept()

class PurchaseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Record New Purchase")
        layout = QVBoxLayout(self)

        self.medicines = db.get_all_medicines()
        self.medicine_box = QComboBox()
        for med in self.medicines:
            self.medicine_box.addItem(f"{med['name']} ({med['strength']})", med["id"])
        layout.addWidget(QLabel("Medicine:"))
        layout.addWidget(self.medicine_box)

        self.qty_edit = QLineEdit()
        self.qty_edit.setPlaceholderText("e.g. 10")
        layout.addWidget(QLabel("Quantity:"))
        layout.addWidget(self.qty_edit)

        # Use dropdown for supplier selection (with editable field for new)
        self.supp_box = QComboBox()
        self.supp_box.setEditable(True)
        self.supp_box.setInsertPolicy(QComboBox.NoInsert)
        self.supp_box.addItem("")
        for sid, name, contact, address in db.get_suppliers():
            self.supp_box.addItem(name, sid)
        layout.addWidget(QLabel("Supplier (optional):"))
        layout.addWidget(self.supp_box)

        btn = QPushButton("Record Purchase")
        btn.clicked.connect(self.save_purchase)
        layout.addWidget(btn)

    def save_purchase(self):
        med_id = self.medicine_box.currentData()
        try:
            qty = int(self.qty_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Quantity must be a number.")
            return
        supp = self.supp_box.currentText().strip()
        supplier = supp if supp else None
        try:
            db.record_purchase(med_id, qty, supplier=supplier)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
            return
        QMessageBox.information(self, "Success", "Purchase recorded!")
        self.accept()