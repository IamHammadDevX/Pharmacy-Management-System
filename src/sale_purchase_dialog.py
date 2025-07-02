from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox
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
        layout.addWidget(QLabel("Quantity:"))
        layout.addWidget(self.qty_edit)

        self.cust_edit = QLineEdit()
        layout.addWidget(QLabel("Customer (optional):"))
        layout.addWidget(self.cust_edit)

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
        cust = self.cust_edit.text()
        try:
            db.record_sale(med_id, qty, customer_name=cust)
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
        layout.addWidget(QLabel("Quantity:"))
        layout.addWidget(self.qty_edit)

        self.supp_edit = QLineEdit()
        layout.addWidget(QLabel("Supplier (optional):"))
        layout.addWidget(self.supp_edit)

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
        supp = self.supp_edit.text()
        try:
            db.record_purchase(med_id, qty, supplier_name=supp)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
            return
        QMessageBox.information(self, "Success", "Purchase recorded!")
        self.accept()