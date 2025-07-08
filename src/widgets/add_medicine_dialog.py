from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QHBoxLayout, QDateEdit, QDoubleSpinBox, QSpinBox, QFormLayout
)
from PyQt5.QtCore import Qt, QDate
import db

class AddMedicineDialog(QDialog):
    def __init__(self, parent=None, initial_data=None):
        super().__init__(parent)
        self.initial_data = initial_data
        self.is_edit_mode = initial_data is not None
        self.edit_id = initial_data.get("id") if initial_data else None

        self.setWindowTitle("Edit Medicine" if self.is_edit_mode else "Add New Medicine")
        self.setMinimumSize(550, 600)
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
            QLineEdit, QDateEdit, QDoubleSpinBox, QSpinBox {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus, QDateEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {
                border: 1px solid #6c5ce7;
            }
            QDateEdit::drop-down {
                border: 0px;
                width: 16px;
                height: 16px;
            }
            QSpinBox::up-button, QSpinBox::down-button,
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 20px;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                background-color: #f0f0f0;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover,
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #e0e0e0;
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
            QPushButton#save_btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #28a745, stop:1 #218838);
            }
            QPushButton#save_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #218838, stop:1 #28a745);
            }
            QPushButton#cancel_btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e74c3c, stop:1 #c0392b);
            }
            QPushButton#cancel_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #c0392b, stop:1 #e74c3c);
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header_label = QLabel("Edit Medicine" if self.is_edit_mode else "Add New Medicine")
        header_label.setObjectName("header_label")
        main_layout.addWidget(header_label)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(0, 10, 0, 10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Paracetamol")
        form_layout.addRow("Medicine Name:", self.name_input)

        self.strength_input = QLineEdit()
        self.strength_input.setPlaceholderText("e.g., 500mg, 10mg/ml")
        form_layout.addRow("Strength (Optional):", self.strength_input)

        self.batch_no_input = QLineEdit()
        self.batch_no_input.setPlaceholderText("e.g., ABC12345")
        form_layout.addRow("Batch Number:", self.batch_no_input)

        self.expiry_date_input = QDateEdit(calendarPopup=True)
        self.expiry_date_input.setMinimumDate(QDate.currentDate())
        self.expiry_date_input.setDate(QDate.currentDate().addYears(1))
        form_layout.addRow("Expiry Date:", self.expiry_date_input)

        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(0)
        self.quantity_input.setMaximum(99999)
        self.quantity_input.setSingleStep(10)
        form_layout.addRow("Quantity:", self.quantity_input)

        self.unit_price_input = QDoubleSpinBox()
        self.unit_price_input.setMinimum(0.00)
        self.unit_price_input.setMaximum(9999.99)
        self.unit_price_input.setPrefix("₨ ")
        self.unit_price_input.setDecimals(2)
        self.unit_price_input.setSingleStep(0.50)
        form_layout.addRow("Unit Price:", self.unit_price_input)

        main_layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.save_btn = QPushButton("Save Medicine" if not self.is_edit_mode else "Update Medicine")
        self.save_btn.setObjectName("save_btn")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_medicine)
        button_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(button_layout)

        if self.is_edit_mode:
            self._load_medicine_data()
            self.name_input.setEnabled(False)
            self.batch_no_input.setEnabled(False)

    def _load_medicine_data(self):
        if self.initial_data:
            self.name_input.setText(self.initial_data.get('name', ''))
            self.strength_input.setText(self.initial_data.get('strength', ''))
            self.batch_no_input.setText(self.initial_data.get('batch_no', ''))
            expiry_date_str = self.initial_data.get('expiry_date')
            if expiry_date_str:
                expiry_date = QDate.fromString(expiry_date_str, "yyyy-MM-dd")
                if expiry_date.isValid():
                    self.expiry_date_input.setDate(expiry_date)
            self.quantity_input.setValue(self.initial_data.get('quantity', 0))
            self.unit_price_input.setValue(self.initial_data.get('unit_price', 0.0))

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "strength": self.strength_input.text().strip(),
            "batch_no": self.batch_no_input.text().strip(),
            "expiry_date": self.expiry_date_input.date().toString("yyyy-MM-dd"),
            "quantity": self.quantity_input.value(),
            "unit_price": self.unit_price_input.value()
        }

    def save_medicine(self):
        self.save_btn.setEnabled(False)
        try:
            med_data = self.get_data()
            if not med_data["name"]:
                QMessageBox.warning(self, "Input Error", "Medicine Name cannot be empty.")
                return
            if not med_data["batch_no"]:
                QMessageBox.warning(self, "Input Error", "Batch Number cannot be empty.")
                return
            if med_data["quantity"] < 0:
                QMessageBox.warning(self, "Input Error", "Quantity cannot be negative.")
                return
            if med_data["unit_price"] <= 0:
                QMessageBox.warning(self, "Input Error", "Unit Price must be positive.")
                return
            if self.expiry_date_input.date() < QDate.currentDate():
                QMessageBox.warning(self, "Input Error", "Expiry Date cannot be in the past.")
                return

            if self.is_edit_mode:
                db.update_medicine(self.edit_id, med_data)
                self.show_success_dialog(f"Medicine '{med_data['name']}' updated successfully!")
            else:
                if db.batch_number_exists(med_data["name"], med_data["batch_no"]):
                    QMessageBox.warning(self, "Duplicate Entry",
                        f"A medicine with name '{med_data['name']}' and batch number '{med_data['batch_no']}' already exists.")
                    return
                db.add_medicine(med_data)
                self.show_success_dialog(f"New medicine '{med_data['name']}' added to inventory!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save medicine:\n{str(e)}")
        finally:
            self.save_btn.setEnabled(True)

    def show_success_dialog(self, message):
        msg = QMessageBox(self)
        msg.setWindowTitle("Success")
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #eafaf1;
                border-radius: 12px;
            }
            QLabel {
                font-size: 18px;
                color: #218838;
                font-weight: bold;
            }
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 8px;
                font-size: 15px;
                padding: 8px 24px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()