from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDateEdit, QPushButton, QMessageBox
from PyQt5.QtCore import QDate
from datetime import datetime
from db import batch_number_exists

class AddMedicineDialog(QDialog):
    def __init__(self, parent=None, initial_data=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Medicine" if not initial_data else "Edit Medicine")
        self.setFixedWidth(400)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # Medicine Name
        layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        # Strength
        layout.addWidget(QLabel("Strength (e.g. 500mg):"))
        self.strength_input = QLineEdit()
        layout.addWidget(self.strength_input)

        # Batch Number
        layout.addWidget(QLabel("Batch Number:"))
        self.batch_input = QLineEdit()
        layout.addWidget(self.batch_input)

        # Expiry Date
        layout.addWidget(QLabel("Expiry Date:"))
        self.expiry_input = QDateEdit()
        self.expiry_input.setCalendarPopup(True)
        self.expiry_input.setDate(QDate.currentDate())
        layout.addWidget(self.expiry_input)

        # Quantity
        layout.addWidget(QLabel("Quantity:"))
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Numeric value")
        layout.addWidget(self.quantity_input)

        # Unit Price
        layout.addWidget(QLabel("Unit Price:"))
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("e.g. 1.50")
        layout.addWidget(self.price_input)

        # Buttons
        btns = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        btns.addWidget(self.save_btn)
        btns.addWidget(self.cancel_btn)
        layout.addLayout(btns)

        self.save_btn.clicked.connect(self.save)
        self.cancel_btn.clicked.connect(self.reject)

        # If editing, pre-fill fields and set edit_id
        self.edit_id = None
        if initial_data:
            self.name_input.setText(initial_data.get("name", ""))
            self.strength_input.setText(initial_data.get("strength", ""))
            self.batch_input.setText(initial_data.get("batch_no", ""))
            expiry = initial_data.get("expiry_date")
            if expiry:
                self.expiry_input.setDate(QDate.fromString(expiry, "yyyy-MM-dd"))
            self.quantity_input.setText(str(initial_data.get("quantity", "")))
            self.price_input.setText(str(initial_data.get("unit_price", "")))
            # For uniqueness check during edit
            self.edit_id = initial_data.get("id", None)

    def save(self):
        # Required: Name
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation", "Name is required.")
            return

        # Required: Quantity - must be integer and > 0
        quantity_text = self.quantity_input.text().strip()
        if not quantity_text:
            QMessageBox.warning(self, "Validation", "Quantity is required.")
            return
        try:
            quantity = int(quantity_text)
            if quantity <= 0:
                QMessageBox.warning(self, "Validation", "Quantity must be a positive integer.")
                return
        except ValueError:
            QMessageBox.warning(self, "Validation", "Quantity must be an integer.")
            return

        # Required: Unit Price - must be float and > 0
        price_text = self.price_input.text().strip()
        if not price_text:
            QMessageBox.warning(self, "Validation", "Unit Price is required.")
            return
        try:
            price = float(price_text)
            if price <= 0:
                QMessageBox.warning(self, "Validation", "Unit Price must be a positive number.")
                return
        except ValueError:
            QMessageBox.warning(self, "Validation", "Unit Price must be a valid number.")
            return

        # Expiry Date (optional, but if filled, not in the past)
        expiry_date = self.expiry_input.date().toString("yyyy-MM-dd")
        if expiry_date:
            exp_dt = datetime.strptime(expiry_date, "%Y-%m-%d")
            today = datetime.today()
            if exp_dt < today.replace(hour=0, minute=0, second=0, microsecond=0):
                QMessageBox.warning(self, "Validation", "Expiry date cannot be in the past.")
                return

        # Batch number uniqueness (for add & edit)
        batch_no = self.batch_input.text().strip()
        if batch_no:
            if batch_number_exists(name, batch_no, self.edit_id):
                QMessageBox.warning(self, "Validation", "Batch number already exists for this medicine.")
                return

        self.accept()

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "strength": self.strength_input.text().strip(),
            "batch_no": self.batch_input.text().strip(),
            "expiry_date": self.expiry_input.date().toString("yyyy-MM-dd"),
            "quantity": int(self.quantity_input.text()),
            "unit_price": float(self.price_input.text())
        }